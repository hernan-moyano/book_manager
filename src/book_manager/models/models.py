"""Modelos ORM de las tablas del sistema Book Manager.

Define con SQLAlchemy las tablas relacionales, sus tipos de datos,
restricciones y relaciones, a partir de las cuales se crea el esquema
de la base de datos.
"""
from __future__ import annotations

from sqlalchemy import Column, Date, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Genero(Base):
    """Categoria literaria a la que pertenece un libro."""

    __tablename__ = "genero"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False, unique=True)

    def __repr__(self) -> str:
        return f"Genero(id={self.id}, nombre={self.nombre!r})"


class Editorial(Base):
    """Proveedor/distribuidora que provee los libros a la libreria."""

    __tablename__ = "editorial"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False, unique=True)

    def __repr__(self) -> str:
        return f"Editorial(id={self.id}, nombre={self.nombre!r})"


class Moneda(Base):
    """Moneda en la que se puede expresar un precio (ARS, USD, ...)."""

    __tablename__ = "moneda"

    id = Column(Integer, primary_key=True)
    codigo = Column(String(3), nullable=False, unique=True)
    descripcion = Column(String(100), nullable=False)

    def __repr__(self) -> str:
        return f"Moneda(id={self.id}, codigo={self.codigo!r})"


class TipoCotizacion(Base):
    """Tipo de cotizacion del dolar (Oficial, Blue, MEP, ...)."""

    __tablename__ = "tipo_cotizacion"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False, unique=True)

    def __repr__(self) -> str:
        return f"TipoCotizacion(id={self.id}, nombre={self.nombre!r})"


class Libro(Base):
    """Titulo del catalogo de la libreria."""

    __tablename__ = "libro"

    id = Column(Integer, primary_key=True)
    isbn = Column(String(20), nullable=False, unique=True)
    titulo = Column(String(200), nullable=False)
    autor = Column(String(120), nullable=False)
    editorial_id = Column(Integer, ForeignKey("editorial.id"), nullable=False)
    genero_id = Column(Integer, ForeignKey("genero.id"), nullable=False)

    editorial = relationship("Editorial", lazy="selectin")
    genero = relationship("Genero", lazy="selectin")

    def __repr__(self) -> str:
        return f"Libro(id={self.id}, titulo={self.titulo!r})"


class Precio(Base):
    """Monto de un libro expresado en una moneda determinada."""

    __tablename__ = "precio"

    id = Column(Integer, primary_key=True)
    libro_id = Column(Integer, ForeignKey("libro.id"), nullable=False)
    moneda_id = Column(Integer, ForeignKey("moneda.id"), nullable=False)
    monto = Column(Numeric(12, 2), nullable=False)

    libro = relationship("Libro", lazy="selectin")
    moneda = relationship("Moneda", lazy="selectin")

    def __repr__(self) -> str:
        return f"Precio(id={self.id}, libro_id={self.libro_id}, monto={self.monto})"


class Stock(Base):
    """Cantidad disponible de cada libro (clave primaria: libro_id)."""

    __tablename__ = "stock"

    libro_id = Column(Integer, ForeignKey("libro.id"), primary_key=True)
    cantidad = Column(Integer, nullable=False)

    libro = relationship("Libro", lazy="selectin")

    def __repr__(self) -> str:
        return f"Stock(libro_id={self.libro_id}, cantidad={self.cantidad})"


class CotizacionDolar(Base):
    """Historico de cotizacion del dolar por tipo y fecha."""

    __tablename__ = "cotizacion_dolar"

    tipo_id = Column(Integer, ForeignKey("tipo_cotizacion.id"), primary_key=True)
    fecha = Column(Date, primary_key=True)
    valor = Column(Numeric(12, 2), nullable=False)

    tipo = relationship("TipoCotizacion", lazy="selectin")

    def __repr__(self) -> str:
        return (
            f"CotizacionDolar(tipo_id={self.tipo_id}, "
            f"fecha={self.fecha.isoformat()}, valor={self.valor})"
        )
