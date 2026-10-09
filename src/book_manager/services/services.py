"""Servicios del sistema Book Manager.

Contiene la lógica de negocio por entidad con inyección de repositorios,
las reglas de integridad referencial (ISBN único, no eliminar géneros/editoriales con libros)
y la clase orquestadora LibreriaService para coordinar operaciones y reportes.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Dict, List, Optional

from book_manager.entities.entities import (
    CotizacionDolar,
    Editorial,
    Genero,
    Libro,
    Moneda,
    Precio,
    Stock,
    TipoCotizacion,
)
from book_manager.repositories.repositories import (
    IRepositorio,
    IRepositorioCotizacionDolar,
    IRepositorioStock,
    RepositorioCotizacionDolarCSV,
    RepositorioEditorialCSV,
    RepositorioGeneroCSV,
    RepositorioLibroCSV,
    RepositorioMonedaCSV,
    RepositorioPrecioCSV,
    RepositorioStockCSV,
    RepositorioTipoCotizacionCSV,
)


class GeneroService:
    """Servicio para la gestión de géneros literarios."""

    def __init__(
        self,
        repo_generos: IRepositorio[Genero],
        repo_libros: Optional[IRepositorio[Libro]] = None,
    ) -> None:
        self.repo = repo_generos
        self.repo_libros = repo_libros

    def alta_genero(self, genero: Genero) -> Genero:
        return self.repo.crear(genero)

    def modificar_genero(self, genero: Genero) -> Genero:
        return self.repo.actualizar(genero)

    def eliminar_genero(self, id: int) -> bool:
        if self.repo_libros is not None:
            libros = self.repo_libros.leer_todos()
            if any(l.genero.id == id for l in libros):
                raise ValueError("No se puede eliminar el género porque tiene libros asociados")
        return self.repo.eliminar(id)

    def obtener_genero(self, id: int) -> Optional[Genero]:
        return self.repo.leer_por_id(id)

    def listar_generos(self) -> List[Genero]:
        return self.repo.leer_todos()


class EditorialService:
    """Servicio para la gestión de editoriales."""

    def __init__(
        self,
        repo_editoriales: IRepositorio[Editorial],
        repo_libros: Optional[IRepositorio[Libro]] = None,
    ) -> None:
        self.repo = repo_editoriales
        self.repo_libros = repo_libros

    def alta_editorial(self, editorial: Editorial) -> Editorial:
        return self.repo.crear(editorial)

    def modificar_editorial(self, editorial: Editorial) -> Editorial:
        return self.repo.actualizar(editorial)

    def eliminar_editorial(self, id: int) -> bool:
        if self.repo_libros is not None:
            libros = self.repo_libros.leer_todos()
            if any(l.editorial.id == id for l in libros):
                raise ValueError("No se puede eliminar la editorial porque tiene libros asociados")
        return self.repo.eliminar(id)

    def obtener_editorial(self, id: int) -> Optional[Editorial]:
        return self.repo.leer_por_id(id)

    def listar_editoriales(self) -> List[Editorial]:
        return self.repo.leer_todos()


class MonedaService:
    """Servicio para la gestión de monedas."""

    def __init__(
        self,
        repo_monedas: IRepositorio[Moneda],
        repo_precios: Optional[IRepositorio[Precio]] = None,
    ) -> None:
        self.repo = repo_monedas
        self.repo_precios = repo_precios

    def alta_moneda(self, moneda: Moneda) -> Moneda:
        return self.repo.crear(moneda)

    def modificar_moneda(self, moneda: Moneda) -> Moneda:
        return self.repo.actualizar(moneda)

    def eliminar_moneda(self, id: int) -> bool:
        if self.repo_precios is not None:
            precios = self.repo_precios.leer_todos()
            if any(p.moneda.id == id for p in precios):
                raise ValueError("No se puede eliminar la moneda porque está asociada a precios existentes")
        return self.repo.eliminar(id)

    def obtener_moneda(self, id: int) -> Optional[Moneda]:
        return self.repo.leer_por_id(id)

    def listar_monedas(self) -> List[Moneda]:
        return self.repo.leer_todos()


class TipoCotizacionService:
    """Servicio para la gestión de tipos de cotización."""

    def __init__(
        self,
        repo_tipos: IRepositorio[TipoCotizacion],
        repo_cotizaciones: Optional[IRepositorioCotizacionDolar] = None,
    ) -> None:
        self.repo = repo_tipos
        self.repo_cotizaciones = repo_cotizaciones

    def alta_tipo_cotizacion(self, tipo: TipoCotizacion) -> TipoCotizacion:
        return self.repo.crear(tipo)

    def modificar_tipo_cotizacion(self, tipo: TipoCotizacion) -> TipoCotizacion:
        return self.repo.actualizar(tipo)

    def eliminar_tipo_cotizacion(self, id: int) -> bool:
        if self.repo_cotizaciones is not None:
            cotizaciones = self.repo_cotizaciones.leer_todos()
            if any(c.tipo.id == id for c in cotizaciones):
                raise ValueError("No se puede eliminar el tipo de cotización porque tiene cotizaciones asociadas")
        return self.repo.eliminar(id)

    def obtener_tipo_cotizacion(self, id: int) -> Optional[TipoCotizacion]:
        return self.repo.leer_por_id(id)

    def listar_tipos_cotizacion(self) -> List[TipoCotizacion]:
        return self.repo.leer_todos()


class LibroService:
    """Servicio para la gestión de libros con validación de relaciones e ISBN único."""

    def __init__(
        self,
        repo_libros: IRepositorio[Libro],
        repo_editoriales: IRepositorio[Editorial],
        repo_generos: IRepositorio[Genero],
        repo_precios: Optional[IRepositorio[Precio]] = None,
        repo_stock: Optional[IRepositorioStock] = None,
    ) -> None:
        self.repo = repo_libros
        self.repo_editoriales = repo_editoriales
        self.repo_generos = repo_generos
        self.repo_precios = repo_precios
        self.repo_stock = repo_stock

    def _validar_isbn_unico(self, isbn: str, libro_id_actual: Optional[int] = None) -> None:
        """Verifica que el ISBN no esté asignado a otro libro."""
        isbn_normalizado = isbn.strip()
        for libro in self.repo.leer_todos():
            if libro.id != libro_id_actual and libro.isbn.strip() == isbn_normalizado:
                raise ValueError(f"Ya existe un libro con el ISBN '{isbn}'")

    def _validar_relaciones(self, libro: Libro) -> None:
        """Verifica que la editorial y el género existan en sus repositorios."""
        if self.repo_editoriales.leer_por_id(libro.editorial.id) is None:
            raise ValueError("Editorial inexistente")
        if self.repo_generos.leer_por_id(libro.genero.id) is None:
            raise ValueError("Género inexistente")

    def alta_libro(self, libro: Libro) -> Libro:
        self._validar_isbn_unico(libro.isbn)
        self._validar_relaciones(libro)
        return self.repo.crear(libro)

    def modificar_libro(self, libro: Libro) -> Libro:
        self._validar_isbn_unico(libro.isbn, libro_id_actual=libro.id)
        self._validar_relaciones(libro)
        return self.repo.actualizar(libro)

    def eliminar_libro(self, id: int) -> bool:
        if self.repo_stock is not None:
            stock = self.repo_stock.leer_por_libro(id)
            if stock is not None:
                raise ValueError("No se puede eliminar el libro porque tiene registros de stock")
        if self.repo_precios is not None:
            precios = self.repo_precios.leer_todos()
            if any(p.libro.id == id for p in precios):
                raise ValueError("No se puede eliminar el libro porque tiene precios asociados")
        return self.repo.eliminar(id)

    def obtener_libro(self, id: int) -> Optional[Libro]:
        return self.repo.leer_por_id(id)

    def listar_libros(self) -> List[Libro]:
        return self.repo.leer_todos()


class PrecioService:
    """Servicio para la gestión de precios monetarios de libros."""

    def __init__(
        self,
        repo_precios: IRepositorio[Precio],
        repo_libros: IRepositorio[Libro],
        repo_monedas: IRepositorio[Moneda],
    ) -> None:
        self.repo = repo_precios
        self.repo_libros = repo_libros
        self.repo_monedas = repo_monedas

    def _validar_relaciones(self, precio: Precio) -> None:
        if self.repo_libros.leer_por_id(precio.libro.id) is None:
            raise ValueError("Libro inexistente")
        if self.repo_monedas.leer_por_id(precio.moneda.id) is None:
            raise ValueError("Moneda inexistente")

    def alta_precio(self, precio: Precio) -> Precio:
        self._validar_relaciones(precio)
        return self.repo.crear(precio)

    def modificar_precio(self, precio: Precio) -> Precio:
        self._validar_relaciones(precio)
        return self.repo.actualizar(precio)

    def eliminar_precio(self, id: int) -> bool:
        return self.repo.eliminar(id)

    def obtener_precio(self, id: int) -> Optional[Precio]:
        return self.repo.leer_por_id(id)

    def listar_precios(self) -> List[Precio]:
        return self.repo.leer_todos()


class StockService:
    """Servicio para la gestión de existencias de libros."""

    def __init__(
        self,
        repo_stock: IRepositorioStock,
        repo_libros: IRepositorio[Libro],
    ) -> None:
        self.repo = repo_stock
        self.repo_libros = repo_libros

    def _validar_libro(self, stock: Stock) -> None:
        if self.repo_libros.leer_por_id(stock.libro.id) is None:
            raise ValueError("Libro inexistente")

    def alta_stock(self, stock: Stock) -> Stock:
        self._validar_libro(stock)
        return self.repo.crear(stock)

    def modificar_stock(self, stock: Stock) -> Stock:
        self._validar_libro(stock)
        return self.repo.actualizar(stock)

    def eliminar_stock(self, libro_id: int) -> bool:
        return self.repo.eliminar(libro_id)

    def obtener_stock(self, libro_id: int) -> Optional[Stock]:
        return self.repo.leer_por_libro(libro_id)

    def listar_stock(self) -> List[Stock]:
        return self.repo.leer_todos()


class CotizacionDolarService:
    """Servicio para la gestión de cotizaciones del dólar."""

    def __init__(
        self,
        repo_cotizaciones: IRepositorioCotizacionDolar,
        repo_tipos: IRepositorio[TipoCotizacion],
    ) -> None:
        self.repo = repo_cotizaciones
        self.repo_tipos = repo_tipos

    def _validar_tipo(self, cotizacion: CotizacionDolar) -> None:
        if self.repo_tipos.leer_por_id(cotizacion.tipo.id) is None:
            raise ValueError("Tipo de cotización inexistente")

    def alta_cotizacion(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        self._validar_tipo(cotizacion)
        return self.repo.crear(cotizacion)

    def modificar_cotizacion(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        self._validar_tipo(cotizacion)
        return self.repo.actualizar(cotizacion)

    def eliminar_cotizacion(self, tipo_id: int, fecha: date) -> bool:
        return self.repo.eliminar(tipo_id, fecha)

    def obtener_cotizacion(
        self, tipo_id: int, fecha: date
    ) -> Optional[CotizacionDolar]:
        return self.repo.leer_por_tipo_y_fecha(tipo_id, fecha)

    def listar_cotizaciones(
        self, tipo_id: Optional[int] = None
    ) -> List[CotizacionDolar]:
        if tipo_id is not None:
            return self.repo.leer_historico_por_tipo(tipo_id)
        return self.repo.leer_todos()


class LibreriaService:
    """Servicio central: orquesta los servicios por entidad y provee los reportes del sistema."""

    def __init__(
        self,
        genero_service: GeneroService,
        editorial_service: EditorialService,
        moneda_service: MonedaService,
        tipo_cotizacion_service: TipoCotizacionService,
        libro_service: LibroService,
        precio_service: PrecioService,
        stock_service: StockService,
        cotizacion_service: CotizacionDolarService,
    ) -> None:
        self.genero_service = genero_service
        self.editorial_service = editorial_service
        self.moneda_service = moneda_service
        self.tipo_cotizacion_service = tipo_cotizacion_service
        self.libro_service = libro_service
        self.precio_service = precio_service
        self.stock_service = stock_service
        self.cotizacion_service = cotizacion_service

        # Exposición directa de repositorios para compatibilidad y consultas
        self.repo_generos = genero_service.repo
        self.repo_editoriales = editorial_service.repo
        self.repo_monedas = moneda_service.repo
        self.repo_tipos_cotizacion = tipo_cotizacion_service.repo
        self.repo_libros = libro_service.repo
        self.repo_precios = precio_service.repo
        self.repo_stock = stock_service.repo
        self.repo_cotizaciones = cotizacion_service.repo

    @classmethod
    def crear_con_archivos_csv(
        cls, base_dir: str | Path | None = None
    ) -> LibreriaService:
        """Crea la jerarquía de repositorios CSV y servicios por entidad."""
        if base_dir is None:
            base_path = Path(__file__).resolve().parent.parent / "migrations" / "csv"
        else:
            base_path = Path(base_dir)

        base_path.mkdir(parents=True, exist_ok=True)

        repo_generos = RepositorioGeneroCSV(base_path / "genero.csv")
        repo_editoriales = RepositorioEditorialCSV(base_path / "editorial.csv")
        repo_monedas = RepositorioMonedaCSV(base_path / "moneda.csv")
        repo_tipos = RepositorioTipoCotizacionCSV(base_path / "tipo_cotizacion.csv")
        repo_libros = RepositorioLibroCSV(
            base_path / "libro.csv",
            repo_editoriales=repo_editoriales,
            repo_generos=repo_generos,
        )
        repo_precios = RepositorioPrecioCSV(
            base_path / "precio.csv",
            repo_libros=repo_libros,
            repo_monedas=repo_monedas,
        )
        repo_stock = RepositorioStockCSV(
            base_path / "stock.csv", repo_libros=repo_libros
        )
        repo_cotizaciones = RepositorioCotizacionDolarCSV(
            base_path / "cotizacion_dolar.csv", repo_tipos=repo_tipos
        )

        genero_service = GeneroService(repo_generos, repo_libros)
        editorial_service = EditorialService(repo_editoriales, repo_libros)
        moneda_service = MonedaService(repo_monedas, repo_precios)
        tipo_cotizacion_service = TipoCotizacionService(repo_tipos, repo_cotizaciones)
        libro_service = LibroService(
            repo_libros,
            repo_editoriales,
            repo_generos,
            repo_precios=repo_precios,
            repo_stock=repo_stock,
        )
        precio_service = PrecioService(repo_precios, repo_libros, repo_monedas)
        stock_service = StockService(repo_stock, repo_libros)
        cotizacion_service = CotizacionDolarService(repo_cotizaciones, repo_tipos)

        return cls(
            genero_service=genero_service,
            editorial_service=editorial_service,
            moneda_service=moneda_service,
            tipo_cotizacion_service=tipo_cotizacion_service,
            libro_service=libro_service,
            precio_service=precio_service,
            stock_service=stock_service,
            cotizacion_service=cotizacion_service,
        )

    # ------------------------------ CRUD Genero ------------------------------
    def alta_genero(self, genero: Genero) -> Genero:
        return self.genero_service.alta_genero(genero)

    def modificar_genero(self, genero: Genero) -> Genero:
        return self.genero_service.modificar_genero(genero)

    def eliminar_genero(self, id: int) -> bool:
        return self.genero_service.eliminar_genero(id)

    def listar_generos(self) -> List[Genero]:
        return self.genero_service.listar_generos()

    # --------------------------- CRUD Editorial ------------------------------
    def alta_editorial(self, editorial: Editorial) -> Editorial:
        return self.editorial_service.alta_editorial(editorial)

    def modificar_editorial(self, editorial: Editorial) -> Editorial:
        return self.editorial_service.modificar_editorial(editorial)

    def eliminar_editorial(self, id: int) -> bool:
        return self.editorial_service.eliminar_editorial(id)

    def listar_editoriales(self) -> List[Editorial]:
        return self.editorial_service.listar_editoriales()

    # ----------------------------- CRUD Moneda -------------------------------
    def alta_moneda(self, moneda: Moneda) -> Moneda:
        return self.moneda_service.alta_moneda(moneda)

    def modificar_moneda(self, moneda: Moneda) -> Moneda:
        return self.moneda_service.modificar_moneda(moneda)

    def eliminar_moneda(self, id: int) -> bool:
        return self.moneda_service.eliminar_moneda(id)

    def listar_monedas(self) -> List[Moneda]:
        return self.moneda_service.listar_monedas()

    # ------------------------ CRUD TipoCotizacion ----------------------------
    def alta_tipo_cotizacion(self, tipo: TipoCotizacion) -> TipoCotizacion:
        return self.tipo_cotizacion_service.alta_tipo_cotizacion(tipo)

    def modificar_tipo_cotizacion(self, tipo: TipoCotizacion) -> TipoCotizacion:
        return self.tipo_cotizacion_service.modificar_tipo_cotizacion(tipo)

    def eliminar_tipo_cotizacion(self, id: int) -> bool:
        return self.tipo_cotizacion_service.eliminar_tipo_cotizacion(id)

    def listar_tipos_cotizacion(self) -> List[TipoCotizacion]:
        return self.tipo_cotizacion_service.listar_tipos_cotizacion()

    # ------------------------------ CRUD Libro -------------------------------
    def alta_libro(self, libro: Libro) -> Libro:
        return self.libro_service.alta_libro(libro)

    def modificar_libro(self, libro: Libro) -> Libro:
        return self.libro_service.modificar_libro(libro)

    def eliminar_libro(self, id: int) -> bool:
        return self.libro_service.eliminar_libro(id)

    def listar_libros(self) -> List[Libro]:
        return self.libro_service.listar_libros()

    # ------------------------------ CRUD Precio ------------------------------
    def alta_precio(self, precio: Precio) -> Precio:
        return self.precio_service.alta_precio(precio)

    def modificar_precio(self, precio: Precio) -> Precio:
        return self.precio_service.modificar_precio(precio)

    def eliminar_precio(self, id: int) -> bool:
        return self.precio_service.eliminar_precio(id)

    def listar_precios(self) -> List[Precio]:
        return self.precio_service.listar_precios()

    # ------------------------------ CRUD Stock -------------------------------
    def alta_stock(self, stock: Stock) -> Stock:
        return self.stock_service.alta_stock(stock)

    def modificar_stock(self, stock: Stock) -> Stock:
        return self.stock_service.modificar_stock(stock)

    def eliminar_stock(self, libro_id: int) -> bool:
        return self.stock_service.eliminar_stock(libro_id)

    def listar_stock(self) -> List[Stock]:
        return self.stock_service.listar_stock()

    # ------------------------- CRUD CotizacionDolar --------------------------
    def alta_cotizacion(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        return self.cotizacion_service.alta_cotizacion(cotizacion)

    def modificar_cotizacion(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        return self.cotizacion_service.modificar_cotizacion(cotizacion)

    def eliminar_cotizacion(self, tipo_id: int, fecha: date) -> bool:
        return self.cotizacion_service.eliminar_cotizacion(tipo_id, fecha)

    def listar_cotizaciones(
        self, tipo_id: Optional[int] = None
    ) -> List[CotizacionDolar]:
        return self.cotizacion_service.listar_cotizaciones(tipo_id)

    # ------------------------------- Reportes --------------------------------
    def reporte_stock_bajo(self, minimo: int = 5) -> List[Stock]:
        """Libros cuyo stock es menor o igual al mínimo indicado."""
        return [s for s in self.stock_service.listar_stock() if s.cantidad <= minimo]

    def reporte_libros_por_genero(self) -> Dict[str, List[Libro]]:
        """Agrupa los libros del catálogo por nombre de género."""
        salida: Dict[str, List[Libro]] = {}
        for libro in self.libro_service.listar_libros():
            nombre = libro.genero.nombre
            salida.setdefault(nombre, []).append(libro)
        return salida

    def cotizacion_hoy(self, tipo_id: int) -> Optional[float]:
        """Valor de la cotización del día actual para el tipo indicado."""
        item = self.cotizacion_service.obtener_cotizacion(tipo_id, date.today())
        return None if item is None else item.valor
