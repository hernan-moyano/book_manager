"""Ítems y loaders del scraper de Cúspide (Sprint 3).

Define :class:`LibroCuspideItem` con los campos a extraer de cada ficha de
libro y :class:`LibroCuspideLoader`, el ``ItemLoader`` con los procesadores
de entrada/salida que normalizan los valores (limpieza de texto y
conversión de precio).
"""
from __future__ import annotations

import re
from typing import Optional

import scrapy
from itemloaders.processors import Join, MapCompose, TakeFirst
from scrapy.loader import ItemLoader


def limpiar_texto(valor: str) -> str:
    """Normaliza un texto colapsando los espacios en blanco.

    Args:
        valor (str): Texto crudo extraído del HTML.

    Returns:
        str: Texto sin espacios redundantes ni saltos de línea.
    """
    return " ".join((valor or "").split())


def convertir_precio(valor: str) -> Optional[float]:
    """Convierte un precio en formato argentino a ``float``.

    Quita los separadores de miles y usa el punto como separador decimal
    (por ejemplo ``$ 12.500,50`` -> ``12500.5``).

    Args:
        valor (str): Precio en formato de texto tal como aparece en la web.

    Returns:
        Optional[float]: El valor numérico, o None si no es convertible.
    """
    limpio = re.sub(r"[^0-9,.-]", "", valor or "").replace(".", "").replace(",", ".")
    try:
        return float(limpio)
    except ValueError:
        return None


class LibroCuspideItem(scrapy.Item):
    """Datos extraídos de la ficha de un libro en Cúspide.

    Fields:
        titulo: Título del libro según el catálogo interno.
        autor: Autor del libro según el catálogo interno.
        isbn_catalogo: ISBN normalizado del libro en el catálogo interno.
        criterio_busqueda: Criterio que produjo la coincidencia (``titulo`` o ``isbn``).
        titulo_web: Título informado por Cúspide.
        autor_web: Autor informado por Cúspide.
        isbn_web: ISBN informado por Cúspide.
        url: URL de la ficha del libro en Cúspide.
        precio: Precio de venta informado en la web (float).
        imagen_url: URL de la imagen de portada.
        formas_pago: Formas de pago y precio informadas en la ficha.
        descripcion: Descripción detallada del libro.
        fecha_extraccion: Fecha y hora en que se extrajo la ficha.
    """

    titulo = scrapy.Field()
    autor = scrapy.Field()
    isbn_catalogo = scrapy.Field()
    criterio_busqueda = scrapy.Field()
    titulo_web = scrapy.Field()
    autor_web = scrapy.Field()
    isbn_web = scrapy.Field()
    url = scrapy.Field()
    precio = scrapy.Field()
    imagen_url = scrapy.Field()
    formas_pago = scrapy.Field()
    descripcion = scrapy.Field()
    fecha_extraccion = scrapy.Field(serializer=str)


class LibroCuspideLoader(ItemLoader):
    """Loader de :class:`LibroCuspideItem` con procesadores de normalización."""

    default_input_processor = MapCompose(limpiar_texto)
    default_output_processor = TakeFirst()
    formas_pago_out = Join(" | ")
    descripcion_out = Join(" ")
    precio_in = MapCompose(limpiar_texto, convertir_precio)
