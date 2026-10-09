"""Entidades del dominio del sistema Book Manager.

Cada entidad encapsula sus atributos y valida sus invariantes mediante
atributos protegidos, propiedades y setters, aplicando herencia y relaciones entre objetos.
"""
from __future__ import annotations

from datetime import date
from typing import Any, Dict


class EntidadBase:
    """Clase base que encapsula el identificador de cada entidad."""

    def __init__(self, id: int) -> None:
        if id <= 0:
            raise ValueError("El id debe ser mayor a cero")
        self._id = id

    @property
    def id(self) -> int:
        """Identificador único de la entidad (solo lectura)."""
        return self._id

    def to_dict(self) -> Dict[str, Any]:
        """Representación de la entidad como diccionario."""
        raise NotImplementedError()


class EntidadNombrada(EntidadBase):
    """Entidad base con nombre encapsulado y validado."""

    def __init__(self, id: int, nombre: str) -> None:
        super().__init__(id)
        self.nombre = nombre

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        valor = valor.strip()
        if not valor:
            raise ValueError("El nombre no puede ser vacío")
        self._nombre = valor

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "nombre": self.nombre}

    def __str__(self) -> str:
        return f"ID={self.id} Nombre={self.nombre}"


class Genero(EntidadNombrada):
    """Categoría literaria a la que pertenece un libro."""


class Editorial(EntidadNombrada):
    """Proveedor/distribuidora que provee los libros a la librería."""


class TipoCotizacion(EntidadNombrada):
    """Tipo de cotización del dólar (Oficial, Blue, MEP, etc.)."""


class Moneda(EntidadBase):
    """Moneda en la que se puede expresar un precio (ARS, USD, etc.)."""

    def __init__(self, id: int, codigo: str, descripcion: str) -> None:
        super().__init__(id)
        self.codigo = codigo
        self.descripcion = descripcion

    @property
    def codigo(self) -> str:
        return self._codigo

    @codigo.setter
    def codigo(self, valor: str) -> None:
        valor = valor.strip().upper()
        if len(valor) != 3 or not valor.isalpha():
            raise ValueError("El código de moneda debe tener 3 letras")
        self._codigo = valor

    @property
    def descripcion(self) -> str:
        return self._descripcion

    @descripcion.setter
    def descripcion(self, valor: str) -> None:
        valor = valor.strip()
        if not valor:
            raise ValueError("La descripción no puede ser vacía")
        self._descripcion = valor

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "codigo": self.codigo,
            "descripcion": self.descripcion,
        }

    def __str__(self) -> str:
        return f"ID={self.id} Código={self.codigo} Descripción={self.descripcion}"


class Libro(EntidadBase):
    """Cada título del catálogo de la librería."""

    def __init__(
        self,
        id: int,
        isbn: str,
        titulo: str,
        autor: str,
        editorial: Editorial,
        genero: Genero,
    ) -> None:
        super().__init__(id)
        self.isbn = isbn
        self.titulo = titulo
        self.autor = autor
        self.editorial = editorial
        self.genero = genero

    @property
    def isbn(self) -> str:
        return self._isbn

    @isbn.setter
    def isbn(self, valor: str) -> None:
        valor = valor.strip()
        if not valor:
            raise ValueError("El ISBN no puede ser vacío")
        self._isbn = valor

    @property
    def titulo(self) -> str:
        return self._titulo

    @titulo.setter
    def titulo(self, valor: str) -> None:
        valor = valor.strip()
        if not valor:
            raise ValueError("El título no puede ser vacío")
        self._titulo = valor

    @property
    def autor(self) -> str:
        return self._autor

    @autor.setter
    def autor(self, valor: str) -> None:
        valor = valor.strip()
        if not valor:
            raise ValueError("El autor no puede ser vacío")
        self._autor = valor

    @property
    def editorial(self) -> Editorial:
        return self._editorial

    @editorial.setter
    def editorial(self, valor: Editorial) -> None:
        if not isinstance(valor, Editorial):
            raise TypeError("La editorial debe ser una instancia de Editorial")
        self._editorial = valor

    @property
    def genero(self) -> Genero:
        return self._genero

    @genero.setter
    def genero(self, valor: Genero) -> None:
        if not isinstance(valor, Genero):
            raise TypeError("El género debe ser una instancia de Genero")
        self._genero = valor

    @property
    def editorial_id(self) -> int:
        return self._editorial.id

    @property
    def genero_id(self) -> int:
        return self._genero.id

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "isbn": self.isbn,
            "titulo": self.titulo,
            "autor": self.autor,
            "editorial_id": self.editorial.id,
            "editorial": self.editorial.nombre,
            "genero_id": self.genero.id,
            "genero": self.genero.nombre,
        }

    def __str__(self) -> str:
        return (
            f"[{self.id}] {self.titulo} - {self.autor} "
            f"(ISBN: {self.isbn}, Editorial: {self.editorial.nombre}, Género: {self.genero.nombre})"
        )


class Precio(EntidadBase):
    """Valor monetario asociado a un libro en una moneda determinada."""

    def __init__(self, id: int, libro: Libro, moneda: Moneda, monto: float) -> None:
        super().__init__(id)
        self.libro = libro
        self.moneda = moneda
        self.monto = monto

    @property
    def libro(self) -> Libro:
        return self._libro

    @libro.setter
    def libro(self, valor: Libro) -> None:
        if not isinstance(valor, Libro):
            raise TypeError("El libro debe ser una instancia de Libro")
        self._libro = valor

    @property
    def moneda(self) -> Moneda:
        return self._moneda

    @moneda.setter
    def moneda(self, valor: Moneda) -> None:
        if not isinstance(valor, Moneda):
            raise TypeError("La moneda debe ser una instancia de Moneda")
        self._moneda = valor

    @property
    def libro_id(self) -> int:
        return self._libro.id

    @property
    def moneda_id(self) -> int:
        return self._moneda.id

    @property
    def monto(self) -> float:
        return self._monto

    @monto.setter
    def monto(self, valor: float) -> None:
        if valor < 0:
            raise ValueError("El monto no puede ser negativo")
        self._monto = float(valor)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "libro_id": self.libro.id,
            "libro": self.libro.titulo,
            "moneda_id": self.moneda.id,
            "moneda": self.moneda.codigo,
            "monto": self.monto,
        }

    def __str__(self) -> str:
        return (
            f"ID={self.id} Libro={self.libro.titulo} "
            f"Moneda={self.moneda.codigo} Monto={self.monto:.2f}"
        )


class Stock:
    """Cantidad disponible de cada libro."""

    def __init__(self, libro: Libro, cantidad: int) -> None:
        self.libro = libro
        self.cantidad = cantidad

    @property
    def libro(self) -> Libro:
        return self._libro

    @libro.setter
    def libro(self, valor: Libro) -> None:
        if not isinstance(valor, Libro):
            raise TypeError("El libro debe ser una instancia de Libro")
        self._libro = valor

    @property
    def libro_id(self) -> int:
        return self._libro.id

    @property
    def cantidad(self) -> int:
        return self._cantidad

    @cantidad.setter
    def cantidad(self, valor: int) -> None:
        if not isinstance(valor, int) or valor < 0:
            raise ValueError("La cantidad debe ser un entero no negativo")
        self._cantidad = valor

    def to_dict(self) -> Dict[str, Any]:
        return {
            "libro_id": self.libro.id,
            "libro": self.libro.titulo,
            "cantidad": self.cantidad,
        }

    def __str__(self) -> str:
        return f"Libro ID={self.libro.id} ({self.libro.titulo}) - Stock={self.cantidad}"


class CotizacionDolar:
    """Registro histórico de cotización por tipo y fecha."""

    def __init__(self, tipo: TipoCotizacion, fecha: date, valor: float) -> None:
        self.tipo = tipo
        self.fecha = fecha
        self.valor = valor

    @property
    def tipo(self) -> TipoCotizacion:
        return self._tipo

    @tipo.setter
    def tipo(self, valor: TipoCotizacion) -> None:
        if not isinstance(valor, TipoCotizacion):
            raise TypeError("El tipo debe ser una instancia de TipoCotizacion")
        self._tipo = valor

    @property
    def tipo_id(self) -> int:
        return self._tipo.id

    @property
    def fecha(self) -> date:
        return self._fecha

    @fecha.setter
    def fecha(self, valor: date) -> None:
        if not isinstance(valor, date):
            raise TypeError("La fecha debe ser una instancia de date")
        self._fecha = valor

    @property
    def valor(self) -> float:
        return self._valor

    @valor.setter
    def valor(self, valor: float) -> None:
        if valor <= 0:
            raise ValueError("La cotización debe ser mayor a cero")
        self._valor = float(valor)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tipo_id": self.tipo.id,
            "tipo": self.tipo.nombre,
            "fecha": self.fecha.isoformat(),
            "valor": self.valor,
        }

    def __str__(self) -> str:
        return f"Tipo={self.tipo.nombre} Fecha={self.fecha.isoformat()} Valor=${self.valor:.2f}"
