"""Repositorios responsables de la persistencia de datos.

Se definen las interfaces (contratos) de cada repositorio,
sus implementaciones en memoria para tests y sus implementaciones
persistentes en archivos CSV que sincronizan cada operación a disco.
"""
from __future__ import annotations

import abc
import csv
import datetime
from pathlib import Path
from typing import Any, Dict, Generic, List, Optional, TypeVar

from book_manager.entities.entities import (
    CotizacionDolar,
    Editorial,
    EntidadBase,
    Genero,
    Libro,
    Moneda,
    Precio,
    Stock,
    TipoCotizacion,
)

T = TypeVar("T", bound=EntidadBase)


class IRepositorio(abc.ABC, Generic[T]):
    """Interfaz para repositorios que manejan entidades con operaciones CRUD básicas."""

    @abc.abstractmethod
    def crear(self, entidad: T) -> T:
        """Crea una nueva entidad en el repositorio.

        Args:
            entidad (T): La entidad a crear.

        Returns:
            T: La entidad creada.

        Raises:
            ValueError: Si ya existe una entidad con el mismo ID.
        """
        pass

    @abc.abstractmethod
    def leer_por_id(self, id: int) -> Optional[T]:
        """Lee una entidad del repositorio por su ID.

        Args:
            id (int): El ID de la entidad a leer.

        Returns:
            Optional[T]: La entidad si se encuentra, None en caso contrario.
        """
        pass

    @abc.abstractmethod
    def leer_todos(self) -> List[T]:
        """Lee todas las entidades del repositorio.

        Returns:
            List[T]: Una lista de todas las entidades.
        """
        pass

    @abc.abstractmethod
    def actualizar(self, entidad: T) -> T:
        """Actualiza una entidad existente en el repositorio.

        Args:
            entidad (T): La entidad a actualizar (debe tener un ID existente).

        Returns:
            T: La entidad actualizada.

        Raises:
            ValueError: Si no se encuentra la entidad para actualizar.
        """
        pass

    @abc.abstractmethod
    def eliminar(self, id: int) -> bool:
        """Elimina una entidad del repositorio por su ID.

        Args:
            id (int): El ID de la entidad a eliminar.

        Returns:
            bool: True si la entidad fue eliminada, False si no se encontró.
        """
        pass


class RepositorioEnMemoria(IRepositorio[T], Generic[T]):
    """Implementación en memoria del repositorio genérico (diccionario por ID)."""

    def __init__(self) -> None:
        self._data: Dict[int, T] = {}

    def crear(self, entidad: T) -> T:
        if entidad.id in self._data:
            raise ValueError(f"Ya existe una entidad con id={entidad.id}")
        self._data[entidad.id] = entidad
        return entidad

    def leer_por_id(self, id: int) -> Optional[T]:
        return self._data.get(id)

    def leer_todos(self) -> List[T]:
        return list(self._data.values())

    def actualizar(self, entidad: T) -> T:
        if entidad.id not in self._data:
            raise ValueError(f"No existe entidad con id={entidad.id}")
        self._data[entidad.id] = entidad
        return entidad

    def eliminar(self, id: int) -> bool:
        if id not in self._data:
            return False
        del self._data[id]
        return True


class IRepositorioStock(abc.ABC):
    """Interfaz para repositorios del tipo Stock."""

    @abc.abstractmethod
    def crear(self, stock: Stock) -> Stock:
        """Crea un nuevo registro de stock.

        Args:
            stock (Stock): El objeto Stock a crear.

        Returns:
            Stock: El objeto Stock creado.

        Raises:
            ValueError: Si ya existe un registro de stock para el mismo libro.
        """
        pass

    @abc.abstractmethod
    def leer_por_libro(self, libro_id: int) -> Optional[Stock]:
        """Lee un registro de stock por ID de libro.

        Args:
            libro_id (int): El ID del libro asociado al stock.

        Returns:
            Optional[Stock]: El objeto Stock si se encuentra, None en caso contrario.
        """
        pass

    @abc.abstractmethod
    def leer_todos(self) -> List[Stock]:
        """Lee todos los registros de stock."""
        pass

    @abc.abstractmethod
    def actualizar(self, stock: Stock) -> Stock:
        """Actualiza un registro de stock existente.

        Args:
            stock (Stock): El objeto Stock a actualizar (debe tener un libro_id existente).

        Returns:
            Stock: El objeto Stock actualizado.

        Raises:
            ValueError: Si no se encuentra el stock para actualizar.
        """
        pass

    @abc.abstractmethod
    def eliminar(self, libro_id: int) -> bool:
        """Elimina un registro de stock por ID de libro.

        Args:
            libro_id (int): El ID del libro asociado al stock a eliminar.

        Returns:
            bool: True si el stock fue eliminado, False si no se encontró.
        """
        pass


class RepositorioStockEnMemoria(IRepositorioStock):
    """Implementación en memoria del repositorio de Stock (clave: libro_id)."""

    def __init__(self) -> None:
        self._data: Dict[int, Stock] = {}

    def crear(self, stock: Stock) -> Stock:
        if stock.libro_id in self._data:
            raise ValueError(f"Ya existe stock para libro_id={stock.libro_id}")
        self._data[stock.libro_id] = stock
        return stock

    def leer_por_libro(self, libro_id: int) -> Optional[Stock]:
        return self._data.get(libro_id)

    def leer_todos(self) -> List[Stock]:
        return list(self._data.values())

    def actualizar(self, stock: Stock) -> Stock:
        if stock.libro_id not in self._data:
            raise ValueError(f"No existe stock para libro_id={stock.libro_id}")
        self._data[stock.libro_id] = stock
        return stock

    def eliminar(self, libro_id: int) -> bool:
        if libro_id not in self._data:
            return False
        del self._data[libro_id]
        return True


class IRepositorioCotizacionDolar(abc.ABC):
    """Interfaz para repositorios del tipo RepositorioCotizacionDolar."""

    @abc.abstractmethod
    def crear(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        """Crea una nueva cotización de dólar.

        Args:
            cotizacion (CotizacionDolar): El objeto CotizacionDolar a crear.

        Returns:
            CotizacionDolar: El objeto CotizacionDolar creado.

        Raises:
            ValueError: Si ya existe una cotización para el mismo tipo y fecha.
        """
        pass

    @abc.abstractmethod
    def leer_por_tipo_y_fecha(
        self, tipo_id: int, fecha: datetime.date
    ) -> Optional[CotizacionDolar]:
        """Lee una cotización de dólar por tipo y fecha.

        Args:
            tipo_id (int): El ID del tipo de cotización (e.g., 'Oficial', 'Blue').
            fecha (datetime.date): La fecha de la cotización.

        Returns:
            Optional[CotizacionDolar]: La cotización si se encuentra, None en caso contrario.
        """
        pass

    @abc.abstractmethod
    def leer_historico_por_tipo(self, tipo_id: int) -> List[CotizacionDolar]:
        """Lee el histórico de cotizaciones para un tipo específico.

        Args:
            tipo_id (int): El ID del tipo de cotización.

        Returns:
            List[CotizacionDolar]: Una lista de cotizaciones históricas para el tipo dado.
        """
        pass

    @abc.abstractmethod
    def leer_todos(self) -> List[CotizacionDolar]:
        """Lee todas las cotizaciones almacenadas."""
        pass

    @abc.abstractmethod
    def actualizar(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        """Actualiza una cotización de dólar existente.

        Args:
            cotizacion (CotizacionDolar): El objeto CotizacionDolar a actualizar.

        Returns:
            CotizacionDolar: El objeto CotizacionDolar actualizado.
        """
        pass

    @abc.abstractmethod
    def eliminar(self, tipo_id: int, fecha: datetime.date) -> bool:
        """Elimina una cotización de dólar por tipo y fecha.

        Args:
            tipo_id (int): El ID del tipo de cotización.
            fecha (datetime.date): La fecha de la cotización a eliminar.

        Returns:
            bool: True si la cotización fue eliminada, False si no se encontró.
        """
        pass


class RepositorioCotizacionDolarEnMemoria(IRepositorioCotizacionDolar):
    """Implementación en memoria del repositorio de cotizaciones (clave: tipo_id + fecha)."""

    def __init__(self) -> None:
        self._data: Dict[tuple, CotizacionDolar] = {}

    def _key(self, tipo_id: int, fecha: datetime.date) -> tuple:
        return (tipo_id, fecha.isoformat())

    def crear(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        key = self._key(cotizacion.tipo_id, cotizacion.fecha)
        if key in self._data:
            raise ValueError("Ya existe una cotización para el mismo tipo y fecha")
        self._data[key] = cotizacion
        return cotizacion

    def leer_por_tipo_y_fecha(
        self, tipo_id: int, fecha: datetime.date
    ) -> Optional[CotizacionDolar]:
        return self._data.get(self._key(tipo_id, fecha))

    def leer_historico_por_tipo(self, tipo_id: int) -> List[CotizacionDolar]:
        cotizaciones = [x for x in self._data.values() if x.tipo_id == tipo_id]
        return sorted(cotizaciones, key=lambda x: x.fecha)

    def leer_todos(self) -> List[CotizacionDolar]:
        return sorted(list(self._data.values()), key=lambda x: (x.tipo_id, x.fecha))

    def actualizar(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        key = self._key(cotizacion.tipo_id, cotizacion.fecha)
        if key not in self._data:
            raise ValueError("No existe la cotización solicitada")
        self._data[key] = cotizacion
        return cotizacion

    def eliminar(self, tipo_id: int, fecha: datetime.date) -> bool:
        key = self._key(tipo_id, fecha)
        if key not in self._data:
            return False
        del self._data[key]
        return True


# =============================================================================
# Implementaciones de Repositorios con Persistencia en Archivos CSV
# =============================================================================


class RepositorioCSVBase(IRepositorio[T], Generic[T]):
    """Repositorio base que sincroniza entidades con un archivo CSV en disco."""

    def __init__(self, ruta_archivo: str | Path, columnas: List[str]) -> None:
        self.ruta_archivo = Path(ruta_archivo)
        self.columnas = columnas
        self._data: Dict[int, T] = {}
        self._inicializar_archivo()
        self.recargar()

    def _inicializar_archivo(self) -> None:
        self.ruta_archivo.parent.mkdir(parents=True, exist_ok=True)
        if not self.ruta_archivo.exists():
            with open(self.ruta_archivo, "w", newline="", encoding="utf-8") as f:
                escritor = csv.DictWriter(f, fieldnames=self.columnas)
                escritor.writeheader()

    def _guardar_en_archivo(self) -> None:
        self.ruta_archivo.parent.mkdir(parents=True, exist_ok=True)
        with open(self.ruta_archivo, "w", newline="", encoding="utf-8") as f:
            escritor = csv.DictWriter(f, fieldnames=self.columnas)
            escritor.writeheader()
            for entidad in self._data.values():
                escritor.writerow(self._entidad_a_fila(entidad))

    def recargar(self) -> None:
        """Vuelve a leer el archivo CSV desde el disco."""
        self._data.clear()
        if not self.ruta_archivo.exists():
            return
        with open(self.ruta_archivo, "r", newline="", encoding="utf-8") as f:
            lector = csv.DictReader(f)
            for fila in lector:
                entidad = self._fila_a_entidad(fila)
                if entidad is not None:
                    self._data[entidad.id] = entidad

    @abc.abstractmethod
    def _fila_a_entidad(self, fila: Dict[str, str]) -> Optional[T]:
        """Convierte una fila del CSV en una instancia de entidad."""
        pass

    @abc.abstractmethod
    def _entidad_a_fila(self, entidad: T) -> Dict[str, Any]:
        """Convierte una entidad en un diccionario listo para escribir al CSV."""
        pass

    def crear(self, entidad: T) -> T:
        if entidad.id in self._data:
            raise ValueError(f"Ya existe una entidad con id={entidad.id}")
        self._data[entidad.id] = entidad
        self._guardar_en_archivo()
        return entidad

    def leer_por_id(self, id: int) -> Optional[T]:
        return self._data.get(id)

    def leer_todos(self) -> List[T]:
        return list(self._data.values())

    def actualizar(self, entidad: T) -> T:
        if entidad.id not in self._data:
            raise ValueError(f"No existe entidad con id={entidad.id}")
        self._data[entidad.id] = entidad
        self._guardar_en_archivo()
        return entidad

    def eliminar(self, id: int) -> bool:
        if id not in self._data:
            return False
        del self._data[id]
        self._guardar_en_archivo()
        return True


class RepositorioGeneroCSV(RepositorioCSVBase[Genero]):
    """Repositorio persistente en CSV para Géneros."""

    def __init__(self, ruta_archivo: str | Path) -> None:
        super().__init__(ruta_archivo, columnas=["id", "nombre"])

    def _fila_a_entidad(self, fila: Dict[str, str]) -> Optional[Genero]:
        return Genero(id=int(fila["id"]), nombre=fila["nombre"])

    def _entidad_a_fila(self, entidad: Genero) -> Dict[str, Any]:
        return {"id": entidad.id, "nombre": entidad.nombre}


class RepositorioEditorialCSV(RepositorioCSVBase[Editorial]):
    """Repositorio persistente en CSV para Editoriales."""

    def __init__(self, ruta_archivo: str | Path) -> None:
        super().__init__(ruta_archivo, columnas=["id", "nombre"])

    def _fila_a_entidad(self, fila: Dict[str, str]) -> Optional[Editorial]:
        return Editorial(id=int(fila["id"]), nombre=fila["nombre"])

    def _entidad_a_fila(self, entidad: Editorial) -> Dict[str, Any]:
        return {"id": entidad.id, "nombre": entidad.nombre}


class RepositorioMonedaCSV(RepositorioCSVBase[Moneda]):
    """Repositorio persistente en CSV para Monedas."""

    def __init__(self, ruta_archivo: str | Path) -> None:
        super().__init__(ruta_archivo, columnas=["id", "codigo", "descripcion"])

    def _fila_a_entidad(self, fila: Dict[str, str]) -> Optional[Moneda]:
        return Moneda(
            id=int(fila["id"]),
            codigo=fila["codigo"],
            descripcion=fila["descripcion"],
        )

    def _entidad_a_fila(self, entidad: Moneda) -> Dict[str, Any]:
        return {
            "id": entidad.id,
            "codigo": entidad.codigo,
            "descripcion": entidad.descripcion,
        }


class RepositorioTipoCotizacionCSV(RepositorioCSVBase[TipoCotizacion]):
    """Repositorio persistente en CSV para Tipos de Cotización."""

    def __init__(self, ruta_archivo: str | Path) -> None:
        super().__init__(ruta_archivo, columnas=["id", "nombre"])

    def _fila_a_entidad(self, fila: Dict[str, str]) -> Optional[TipoCotizacion]:
        return TipoCotizacion(id=int(fila["id"]), nombre=fila["nombre"])

    def _entidad_a_fila(self, entidad: TipoCotizacion) -> Dict[str, Any]:
        return {"id": entidad.id, "nombre": entidad.nombre}


class RepositorioLibroCSV(RepositorioCSVBase[Libro]):
    """Repositorio persistente en CSV para Libros (resuelve Editorial y Género)."""

    def __init__(
        self,
        ruta_archivo: str | Path,
        repo_editoriales: IRepositorio[Editorial],
        repo_generos: IRepositorio[Genero],
    ) -> None:
        self.repo_editoriales = repo_editoriales
        self.repo_generos = repo_generos
        super().__init__(
            ruta_archivo,
            columnas=["id", "isbn", "titulo", "autor", "editorial_id", "genero_id"],
        )

    def _fila_a_entidad(self, fila: Dict[str, str]) -> Optional[Libro]:
        editorial = self.repo_editoriales.leer_por_id(int(fila["editorial_id"]))
        genero = self.repo_generos.leer_por_id(int(fila["genero_id"]))
        if editorial is None or genero is None:
            return None
        return Libro(
            id=int(fila["id"]),
            isbn=fila["isbn"],
            titulo=fila["titulo"],
            autor=fila["autor"],
            editorial=editorial,
            genero=genero,
        )

    def _entidad_a_fila(self, entidad: Libro) -> Dict[str, Any]:
        return {
            "id": entidad.id,
            "isbn": entidad.isbn,
            "titulo": entidad.titulo,
            "autor": entidad.autor,
            "editorial_id": entidad.editorial.id,
            "genero_id": entidad.genero.id,
        }


class RepositorioPrecioCSV(RepositorioCSVBase[Precio]):
    """Repositorio persistente en CSV para Precios (resuelve Libro y Moneda)."""

    def __init__(
        self,
        ruta_archivo: str | Path,
        repo_libros: IRepositorio[Libro],
        repo_monedas: IRepositorio[Moneda],
    ) -> None:
        self.repo_libros = repo_libros
        self.repo_monedas = repo_monedas
        super().__init__(
            ruta_archivo,
            columnas=["id", "libro_id", "moneda_id", "monto"],
        )

    def _fila_a_entidad(self, fila: Dict[str, str]) -> Optional[Precio]:
        libro = self.repo_libros.leer_por_id(int(fila["libro_id"]))
        moneda = self.repo_monedas.leer_por_id(int(fila["moneda_id"]))
        if libro is None or moneda is None:
            return None
        return Precio(
            id=int(fila["id"]),
            libro=libro,
            moneda=moneda,
            monto=float(fila["monto"]),
        )

    def _entidad_a_fila(self, entidad: Precio) -> Dict[str, Any]:
        return {
            "id": entidad.id,
            "libro_id": entidad.libro.id,
            "moneda_id": entidad.moneda.id,
            "monto": entidad.monto,
        }


class RepositorioStockCSV(IRepositorioStock):
    """Repositorio persistente en CSV para Stock (resuelve Libro)."""

    def __init__(
        self, ruta_archivo: str | Path, repo_libros: IRepositorio[Libro]
    ) -> None:
        self.ruta_archivo = Path(ruta_archivo)
        self.repo_libros = repo_libros
        self.columnas = ["libro_id", "cantidad"]
        self._data: Dict[int, Stock] = {}
        self._inicializar_archivo()
        self.recargar()

    def _inicializar_archivo(self) -> None:
        self.ruta_archivo.parent.mkdir(parents=True, exist_ok=True)
        if not self.ruta_archivo.exists():
            with open(self.ruta_archivo, "w", newline="", encoding="utf-8") as f:
                escritor = csv.DictWriter(f, fieldnames=self.columnas)
                escritor.writeheader()

    def _guardar_en_archivo(self) -> None:
        self.ruta_archivo.parent.mkdir(parents=True, exist_ok=True)
        with open(self.ruta_archivo, "w", newline="", encoding="utf-8") as f:
            escritor = csv.DictWriter(f, fieldnames=self.columnas)
            escritor.writeheader()
            for s in self._data.values():
                escritor.writerow({"libro_id": s.libro.id, "cantidad": s.cantidad})

    def recargar(self) -> None:
        self._data.clear()
        if not self.ruta_archivo.exists():
            return
        with open(self.ruta_archivo, "r", newline="", encoding="utf-8") as f:
            lector = csv.DictReader(f)
            for fila in lector:
                libro = self.repo_libros.leer_por_id(int(fila["libro_id"]))
                if libro is not None:
                    self._data[libro.id] = Stock(libro=libro, cantidad=int(fila["cantidad"]))

    def crear(self, stock: Stock) -> Stock:
        if stock.libro_id in self._data:
            raise ValueError(f"Ya existe stock para libro_id={stock.libro_id}")
        self._data[stock.libro_id] = stock
        self._guardar_en_archivo()
        return stock

    def leer_por_libro(self, libro_id: int) -> Optional[Stock]:
        return self._data.get(libro_id)

    def leer_todos(self) -> List[Stock]:
        return list(self._data.values())

    def actualizar(self, stock: Stock) -> Stock:
        if stock.libro_id not in self._data:
            raise ValueError(f"No existe stock para libro_id={stock.libro_id}")
        self._data[stock.libro_id] = stock
        self._guardar_en_archivo()
        return stock

    def eliminar(self, libro_id: int) -> bool:
        if libro_id not in self._data:
            return False
        del self._data[libro_id]
        self._guardar_en_archivo()
        return True


class RepositorioCotizacionDolarCSV(IRepositorioCotizacionDolar):
    """Repositorio persistente en CSV para Cotizaciones de Dólar (resuelve TipoCotizacion)."""

    def __init__(
        self,
        ruta_archivo: str | Path,
        repo_tipos: IRepositorio[TipoCotizacion],
    ) -> None:
        self.ruta_archivo = Path(ruta_archivo)
        self.repo_tipos = repo_tipos
        self.columnas = ["tipo_id", "fecha", "valor"]
        self._data: Dict[tuple, CotizacionDolar] = {}
        self._inicializar_archivo()
        self.recargar()

    def _key(self, tipo_id: int, fecha: datetime.date) -> tuple:
        return (tipo_id, fecha.isoformat())

    def _inicializar_archivo(self) -> None:
        self.ruta_archivo.parent.mkdir(parents=True, exist_ok=True)
        if not self.ruta_archivo.exists():
            with open(self.ruta_archivo, "w", newline="", encoding="utf-8") as f:
                escritor = csv.DictWriter(f, fieldnames=self.columnas)
                escritor.writeheader()

    def _guardar_en_archivo(self) -> None:
        self.ruta_archivo.parent.mkdir(parents=True, exist_ok=True)
        with open(self.ruta_archivo, "w", newline="", encoding="utf-8") as f:
            escritor = csv.DictWriter(f, fieldnames=self.columnas)
            escritor.writeheader()
            for c in self._data.values():
                escritor.writerow(
                    {
                        "tipo_id": c.tipo.id,
                        "fecha": c.fecha.isoformat(),
                        "valor": c.valor,
                    }
                )

    def recargar(self) -> None:
        self._data.clear()
        if not self.ruta_archivo.exists():
            return
        with open(self.ruta_archivo, "r", newline="", encoding="utf-8") as f:
            lector = csv.DictReader(f)
            for fila in lector:
                tipo = self.repo_tipos.leer_por_id(int(fila["tipo_id"]))
                if tipo is not None:
                    fecha = datetime.date.fromisoformat(fila["fecha"])
                    valor = float(fila["valor"])
                    key = self._key(tipo.id, fecha)
                    self._data[key] = CotizacionDolar(tipo=tipo, fecha=fecha, valor=valor)

    def crear(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        key = self._key(cotizacion.tipo_id, cotizacion.fecha)
        if key in self._data:
            raise ValueError("Ya existe una cotización para el mismo tipo y fecha")
        self._data[key] = cotizacion
        self._guardar_en_archivo()
        return cotizacion

    def leer_por_tipo_y_fecha(
        self, tipo_id: int, fecha: datetime.date
    ) -> Optional[CotizacionDolar]:
        return self._data.get(self._key(tipo_id, fecha))

    def leer_historico_por_tipo(self, tipo_id: int) -> List[CotizacionDolar]:
        cotizaciones = [x for x in self._data.values() if x.tipo_id == tipo_id]
        return sorted(cotizaciones, key=lambda x: x.fecha)

    def leer_todos(self) -> List[CotizacionDolar]:
        return sorted(list(self._data.values()), key=lambda x: (x.tipo_id, x.fecha))

    def actualizar(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        key = self._key(cotizacion.tipo_id, cotizacion.fecha)
        if key not in self._data:
            raise ValueError("No existe la cotización solicitada")
        self._data[key] = cotizacion
        self._guardar_en_archivo()
        return cotizacion

    def eliminar(self, tipo_id: int, fecha: datetime.date) -> bool:
        key = self._key(tipo_id, fecha)
        if key not in self._data:
            return False
        del self._data[key]
        self._guardar_en_archivo()
        return True
