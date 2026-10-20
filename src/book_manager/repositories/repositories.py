"""Repositorios responsables de la persistencia de datos.

Se definen las interfaces (contratos) de cada repositorio y sus
implementaciones sobre la base de datos PostgreSQL con SQLAlchemy, con
el CRUD completo de cada entidad. Cada operacion abre y cierra su propia
transaccion mediante ``ConexionDB.session_scope``.

Las entidades del dominio se relacionan por objeto (no por id): al leer
una fila se reconstruye la entidad completa con sus objetos asociados.
"""
from __future__ import annotations

import abc
import datetime
from typing import Callable, Generic, List, Optional, TypeVar

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from book_manager.database.connection import ConexionDB
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
from book_manager.models import models as modelos

T = TypeVar("T", bound=EntidadBase)


def _libro_entidad(fila: modelos.Libro) -> Libro:
    """Convierte una fila ORM de libro en una entidad ``Libro`` por objeto."""
    return Libro(
        fila.id,
        fila.isbn,
        fila.titulo,
        fila.autor,
        Editorial(fila.editorial.id, fila.editorial.nombre),
        Genero(fila.genero.id, fila.genero.nombre),
    )


def _tipo_entidad(fila: modelos.TipoCotizacion) -> TipoCotizacion:
    """Convierte una fila ORM de tipo de cotizacion en su entidad."""
    return TipoCotizacion(fila.id, fila.nombre)


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


class RepositorioSQL(IRepositorio[T], Generic[T]):
    """Implementación genérica del repositorio sobre la base de datos."""

    def __init__(
        self,
        conexion: ConexionDB,
        modelo: type,
        a_modelo: Callable[[T], object],
        a_entidad: Callable[[object], T],
    ) -> None:
        """Guarda la conexión y las funciones de conversión entidad <-> fila.

        Args:
            conexion (ConexionDB): Conexión con la base de datos.
            modelo (type): Clase ORM de SQLAlchemy de la tabla.
            a_modelo (Callable[[T], object]): Convierte la entidad en una fila.
            a_entidad (Callable[[object], T]): Convierte la fila en la entidad.
        """
        self._conexion = conexion
        self._modelo = modelo
        self._a_modelo = a_modelo
        self._a_entidad = a_entidad

    @property
    def _columna_clave(self) -> object:
        """Primera columna de la clave primaria (usada como orden por defecto)."""
        return list(self._modelo.__table__.primary_key.columns)[0]

    def crear(self, entidad: T) -> T:
        if self.leer_por_id(entidad.id) is not None:
            raise ValueError(f"Ya existe una entidad con id={entidad.id}")
        try:
            with self._conexion.session_scope() as sesion:
                sesion.add(self._a_modelo(entidad))
        except IntegrityError as exc:
            raise ValueError("Viola una restricción de la base de datos") from exc
        return entidad

    def leer_por_id(self, id: int) -> Optional[T]:
        with self._conexion.session_scope() as sesion:
            fila = sesion.get(self._modelo, id)
            return None if fila is None else self._a_entidad(fila)

    def leer_todos(self) -> List[T]:
        with self._conexion.session_scope() as sesion:
            consulta = select(self._modelo).order_by(self._columna_clave)
            filas = sesion.execute(consulta).scalars().all()
            return [self._a_entidad(fila) for fila in filas]

    def actualizar(self, entidad: T) -> T:
        with self._conexion.session_scope() as sesion:
            fila = sesion.get(self._modelo, entidad.id)
            if fila is None:
                raise ValueError(f"No existe entidad con id={entidad.id}")
            nueva_fila = self._a_modelo(entidad)
            for columna in self._modelo.__table__.columns.keys():
                setattr(fila, columna, getattr(nueva_fila, columna))
        return entidad

    def eliminar(self, id: int) -> bool:
        with self._conexion.session_scope() as sesion:
            fila = sesion.get(self._modelo, id)
            if fila is None:
                return False
            sesion.delete(fila)
        return True


class RepositorioGenerosSQL(RepositorioSQL[Genero]):
    """Repositorio SQL de los géneros."""

    def __init__(self, conexion: ConexionDB) -> None:
        super().__init__(
            conexion,
            modelos.Genero,
            lambda genero: modelos.Genero(id=genero.id, nombre=genero.nombre),
            lambda fila: Genero(fila.id, fila.nombre),
        )


class RepositorioEditorialesSQL(RepositorioSQL[Editorial]):
    """Repositorio SQL de las editoriales."""

    def __init__(self, conexion: ConexionDB) -> None:
        super().__init__(
            conexion,
            modelos.Editorial,
            lambda editorial: modelos.Editorial(id=editorial.id, nombre=editorial.nombre),
            lambda fila: Editorial(fila.id, fila.nombre),
        )


class RepositorioMonedasSQL(RepositorioSQL[Moneda]):
    """Repositorio SQL de las monedas."""

    def __init__(self, conexion: ConexionDB) -> None:
        super().__init__(
            conexion,
            modelos.Moneda,
            lambda moneda: modelos.Moneda(
                id=moneda.id, codigo=moneda.codigo, descripcion=moneda.descripcion
            ),
            lambda fila: Moneda(fila.id, fila.codigo, fila.descripcion),
        )


class RepositorioTiposCotizacionSQL(RepositorioSQL[TipoCotizacion]):
    """Repositorio SQL de los tipos de cotización."""

    def __init__(self, conexion: ConexionDB) -> None:
        super().__init__(
            conexion,
            modelos.TipoCotizacion,
            lambda tipo: modelos.TipoCotizacion(id=tipo.id, nombre=tipo.nombre),
            lambda fila: TipoCotizacion(fila.id, fila.nombre),
        )


class RepositorioLibrosSQL(RepositorioSQL[Libro]):
    """Repositorio SQL de los libros (reconstruye editorial y género por objeto)."""

    def __init__(self, conexion: ConexionDB) -> None:
        super().__init__(
            conexion,
            modelos.Libro,
            lambda libro: modelos.Libro(
                id=libro.id,
                isbn=libro.isbn,
                titulo=libro.titulo,
                autor=libro.autor,
                editorial_id=libro.editorial_id,
                genero_id=libro.genero_id,
            ),
            _libro_entidad,
        )


class RepositorioPreciosSQL(RepositorioSQL[Precio]):
    """Repositorio SQL de los precios (reconstruye libro y moneda por objeto)."""

    def __init__(self, conexion: ConexionDB) -> None:
        super().__init__(
            conexion,
            modelos.Precio,
            lambda precio: modelos.Precio(
                id=precio.id,
                libro_id=precio.libro_id,
                moneda_id=precio.moneda_id,
                monto=precio.monto,
            ),
            lambda fila: Precio(
                fila.id,
                _libro_entidad(fila.libro),
                Moneda(fila.moneda.id, fila.moneda.codigo, fila.moneda.descripcion),
                float(fila.monto),
            ),
        )


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
        """Lee todos los registros de stock.

        Returns:
            List[Stock]: Una lista con todo el stock.
        """
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


class RepositorioStockSQL(IRepositorioStock):
    """Implementación SQL del repositorio de Stock (clave primaria: libro_id)."""

    def __init__(self, conexion: ConexionDB) -> None:
        self._conexion = conexion

    @staticmethod
    def _a_entidad(fila: modelos.Stock) -> Stock:
        return Stock(_libro_entidad(fila.libro), fila.cantidad)

    def crear(self, stock: Stock) -> Stock:
        if self.leer_por_libro(stock.libro_id) is not None:
            raise ValueError(f"Ya existe stock para libro_id={stock.libro_id}")
        with self._conexion.session_scope() as sesion:
            sesion.add(modelos.Stock(libro_id=stock.libro_id, cantidad=stock.cantidad))
        return stock

    def leer_por_libro(self, libro_id: int) -> Optional[Stock]:
        with self._conexion.session_scope() as sesion:
            fila = sesion.get(modelos.Stock, libro_id)
            return None if fila is None else self._a_entidad(fila)

    def leer_todos(self) -> List[Stock]:
        with self._conexion.session_scope() as sesion:
            consulta = select(modelos.Stock).order_by(modelos.Stock.libro_id)
            filas = sesion.execute(consulta).scalars().all()
            return [self._a_entidad(fila) for fila in filas]

    def actualizar(self, stock: Stock) -> Stock:
        with self._conexion.session_scope() as sesion:
            fila = sesion.get(modelos.Stock, stock.libro_id)
            if fila is None:
                raise ValueError(f"No existe stock para libro_id={stock.libro_id}")
            fila.cantidad = stock.cantidad
        return stock

    def eliminar(self, libro_id: int) -> bool:
        with self._conexion.session_scope() as sesion:
            fila = sesion.get(modelos.Stock, libro_id)
            if fila is None:
                return False
            sesion.delete(fila)
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
        """Lee todas las cotizaciones registradas.

        Returns:
            List[CotizacionDolar]: Una lista con todas las cotizaciones.
        """
        pass

    @abc.abstractmethod
    def actualizar(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        """Actualiza una cotización de dólar existente.

        Args:
            cotizacion (CotizacionDolar): El objeto CotizacionDolar a actualizar.

        Returns:
            CotizacionDolar: El objeto CotizacionDolar actualizado.

        Raises:
            ValueError: Si no se encuentra la cotización para actualizar.
        """
        pass

    @abc.abstractmethod
    def eliminar(self, tipo_id: int, fecha: datetime.date) -> bool:
        """Elimina una cotización de dólar por tipo y fecha.

        Args:
            tipo_id (int): El ID del tipo de cotización.
            fecha (datetime.date): La fecha de la cotización.

        Returns:
            bool: True si la cotización fue eliminada, False si no se encontró.
        """
        pass


class RepositorioCotizacionDolarSQL(IRepositorioCotizacionDolar):
    """Implementación SQL del repositorio de cotizaciones (clave: tipo_id + fecha)."""

    def __init__(self, conexion: ConexionDB) -> None:
        self._conexion = conexion

    @staticmethod
    def _a_modelo(cotizacion: CotizacionDolar) -> modelos.CotizacionDolar:
        return modelos.CotizacionDolar(
            tipo_id=cotizacion.tipo_id,
            fecha=cotizacion.fecha,
            valor_compra=cotizacion.valor_compra,
            valor_venta=cotizacion.valor_venta,
        )

    @staticmethod
    def _a_entidad(fila: modelos.CotizacionDolar) -> CotizacionDolar:
        return CotizacionDolar(
            _tipo_entidad(fila.tipo),
            fila.fecha,
            float(fila.valor_compra),
            float(fila.valor_venta),
        )

    def crear(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        if self.leer_por_tipo_y_fecha(cotizacion.tipo_id, cotizacion.fecha) is not None:
            raise ValueError("Ya existe una cotización para el mismo tipo y fecha")
        with self._conexion.session_scope() as sesion:
            sesion.add(self._a_modelo(cotizacion))
        return cotizacion

    def leer_por_tipo_y_fecha(
        self, tipo_id: int, fecha: datetime.date
    ) -> Optional[CotizacionDolar]:
        with self._conexion.session_scope() as sesion:
            fila = sesion.get(modelos.CotizacionDolar, (tipo_id, fecha))
            return None if fila is None else self._a_entidad(fila)

    def leer_historico_por_tipo(self, tipo_id: int) -> List[CotizacionDolar]:
        with self._conexion.session_scope() as sesion:
            consulta = (
                select(modelos.CotizacionDolar)
                .where(modelos.CotizacionDolar.tipo_id == tipo_id)
                .order_by(modelos.CotizacionDolar.fecha)
            )
            filas = sesion.execute(consulta).scalars().all()
            return [self._a_entidad(fila) for fila in filas]

    def leer_todos(self) -> List[CotizacionDolar]:
        with self._conexion.session_scope() as sesion:
            consulta = select(modelos.CotizacionDolar).order_by(
                modelos.CotizacionDolar.tipo_id, modelos.CotizacionDolar.fecha
            )
            filas = sesion.execute(consulta).scalars().all()
            return [self._a_entidad(fila) for fila in filas]

    def actualizar(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        with self._conexion.session_scope() as sesion:
            fila = sesion.get(modelos.CotizacionDolar, (cotizacion.tipo_id, cotizacion.fecha))
            if fila is None:
                raise ValueError("No existe la cotización solicitada")
            fila.valor_compra = cotizacion.valor_compra
            fila.valor_venta = cotizacion.valor_venta
        return cotizacion

    def eliminar(self, tipo_id: int, fecha: datetime.date) -> bool:
        with self._conexion.session_scope() as sesion:
            fila = sesion.get(modelos.CotizacionDolar, (tipo_id, fecha))
            if fila is None:
                return False
            sesion.delete(fila)
        return True
