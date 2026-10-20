"""Modelos ORM de las tablas del sistema Book Manager.

Define con SQLAlchemy las tablas relacionales, sus tipos de datos,
restricciones y relaciones bidireccionales (``back_populates``), a partir
de las cuales se crea el esquema de la base de datos. Las relaciones
permiten navegar en ambos sentidos: por ejemplo, de un libro a sus
precios (``libro.precios``) y de un precio a su libro (``precio.libro``),
o de un tipo de cotización a su histórico (``tipo.cotizaciones``).
"""
from __future__ import annotations

from sqlalchemy import Column, Date, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Genero(Base):
    """Categoria literaria a la que pertenece un libro.

    Attributes:
        libros (list[Libro]): Libros asociados al género (navegación inversa).
    """

    __tablename__ = "genero"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False, unique=True)

    libros = relationship("Libro", back_populates="genero")

    def __repr__(self) -> str:
        return f"Genero(id={self.id}, nombre={self.nombre!r})"


class Editorial(Base):
    """Proveedor/distribuidora que provee los libros a la libreria.

    Attributes:
        libros (list[Libro]): Libros asociados a la editorial (navegación inversa).
    """

    __tablename__ = "editorial"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False, unique=True)

    libros = relationship("Libro", back_populates="editorial")

    def __repr__(self) -> str:
        return f"Editorial(id={self.id}, nombre={self.nombre!r})"


class Moneda(Base):
    """Moneda en la que se puede expresar un precio (ARS, USD, ...).

    Attributes:
        precios (list[Precio]): Precios expresados en la moneda (navegación inversa).
    """

    __tablename__ = "moneda"

    id = Column(Integer, primary_key=True)
    codigo = Column(String(3), nullable=False, unique=True)
    descripcion = Column(String(100), nullable=False)

    precios = relationship("Precio", back_populates="moneda")

    def __repr__(self) -> str:
        return f"Moneda(id={self.id}, codigo={self.codigo!r})"


class TipoCotizacion(Base):
    """Tipo de cotizacion del dolar (Oficial, Blue, MEP, ...).

    Attributes:
        cotizaciones (list[CotizacionDolar]): Histórico de cotizaciones del
            tipo (navegación inversa).
    """

    __tablename__ = "tipo_cotizacion"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False, unique=True)

    cotizaciones = relationship("CotizacionDolar", back_populates="tipo")

    def __repr__(self) -> str:
        return f"TipoCotizacion(id={self.id}, nombre={self.nombre!r})"


class Libro(Base):
    """Titulo del catalogo de la libreria.

    Attributes:
        editorial (Editorial): Editorial del libro.
        genero (Genero): Género del libro.
        precios (list[Precio]): Precios del libro en las distintas monedas.
        stock (Optional[Stock]): Registro de stock del libro (uno a uno).
    """

    __tablename__ = "libro"

    id = Column(Integer, primary_key=True)
    isbn = Column(String(20), nullable=False, unique=True)
    titulo = Column(String(200), nullable=False)
    autor = Column(String(120), nullable=False)
    editorial_id = Column(Integer, ForeignKey("editorial.id"), nullable=False)
    genero_id = Column(Integer, ForeignKey("genero.id"), nullable=False)

    editorial = relationship("Editorial", back_populates="libros", lazy="selectin")
    genero = relationship("Genero", back_populates="libros", lazy="selectin")
    precios = relationship("Precio", back_populates="libro")
    stock = relationship("Stock", back_populates="libro", uselist=False)

    def __repr__(self) -> str:
        return f"Libro(id={self.id}, titulo={self.titulo!r})"


class Precio(Base):
    """Monto de un libro expresado en una moneda determinada.

    Attributes:
        libro (Libro): Libro al que pertenece el precio.
        moneda (Moneda): Moneda en la que se expresa el monto.
    """

    __tablename__ = "precio"

    id = Column(Integer, primary_key=True)
    libro_id = Column(Integer, ForeignKey("libro.id"), nullable=False)
    moneda_id = Column(Integer, ForeignKey("moneda.id"), nullable=False)
    monto = Column(Numeric(12, 2), nullable=False)

    libro = relationship("Libro", back_populates="precios", lazy="selectin")
    moneda = relationship("Moneda", back_populates="precios", lazy="selectin")

    def __repr__(self) -> str:
        return f"Precio(id={self.id}, libro_id={self.libro_id}, monto={self.monto})"


class Stock(Base):
    """Cantidad disponible de cada libro (clave primaria: libro_id).

    Attributes:
        libro (Libro): Libro al que pertenece el registro de stock.
    """

    __tablename__ = "stock"

    libro_id = Column(Integer, ForeignKey("libro.id"), primary_key=True)
    cantidad = Column(Integer, nullable=False)

    libro = relationship("Libro", back_populates="stock", lazy="selectin")

    def __repr__(self) -> str:
        return f"Stock(libro_id={self.libro_id}, cantidad={self.cantidad})"


class CotizacionDolar(Base):
    """Historico de cotizacion del dolar por tipo y fecha.

    Registra los valores de compra y de venta informados por la API del
    dólar para cada tipo de cotización y fecha.

    Attributes:
        tipo (TipoCotizacion): Tipo de cotización al que pertenece el registro.
    """

    __tablename__ = "cotizacion_dolar"

    tipo_id = Column(Integer, ForeignKey("tipo_cotizacion.id"), primary_key=True)
    fecha = Column(Date, primary_key=True)
    valor_compra = Column(Numeric(12, 2), nullable=False)
    valor_venta = Column(Numeric(12, 2), nullable=False)

    tipo = relationship("TipoCotizacion", back_populates="cotizaciones", lazy="selectin")

    def __repr__(self) -> str:
        return (
            f"CotizacionDolar(tipo_id={self.tipo_id}, "
            f"fecha={self.fecha.isoformat()}, "
            f"compra={self.valor_compra}, venta={self.valor_venta})"
        )
