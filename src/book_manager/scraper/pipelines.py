"""Pipelines del scraper de Cúspide (Sprint 3).

Los ítems pasan por una cadena de pipelines: :class:`ValidarLibroPipeline`
(prioridad 100) descarta las fichas sin precio o repetidas y
:class:`JsonLinesPipeline` (prioridad 300) persiste cada ítem válido en un
archivo JSON Lines (``.jl``) dentro de la carpeta ``reportes`` para su
posterior comparación de precios.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Set

from scrapy.crawler import Crawler
from scrapy.exceptions import DropItem


class ValidarLibroPipeline:
    """Pipeline que valida los ítems antes de guardarlos.

    Descarta (``DropItem``) las fichas sin precio válido y las que ya se
    procesaron, por ejemplo cuando dos búsquedas llegan a la misma ficha.
    """

    def __init__(self) -> None:
        """Inicializa el registro de URLs ya procesadas."""
        self.urls: Set[str] = set()

    def process_item(self, item: Any, spider: Any = None) -> Any:
        """Valida el ítem y lo devuelve si debe guardarse.

        Args:
            item (Any): Ítem extraído por el spider.
            spider (Any): Spider en ejecución (Scrapy < 2.13 lo pasa como argumento).

        Returns:
            Any: El mismo ítem, si es válido.

        Raises:
            DropItem: Si la ficha no tiene precio o ya fue procesada.
        """
        if not item.get("precio") or item["precio"] <= 0:
            raise DropItem(f"Ficha sin precio: {item.get('url')}")
        if item["url"] in self.urls:
            raise DropItem(f"Ficha repetida: {item['url']}")
        self.urls.add(item["url"])
        return item


class JsonLinesPipeline:
    """Pipeline que escribe cada ítem como una línea JSON en un archivo.

    El destino se define con el argumento ``output_path`` del spider; si no
    se indica se usa ``cuspide_resultados.jl`` en el directorio de trabajo.
    """

    def __init__(self) -> None:
        """Inicializa el pipeline sin archivo abierto."""
        self.crawler: Crawler
        self.file: Any

    @classmethod
    def from_crawler(cls, crawler: Crawler) -> "JsonLinesPipeline":
        """Crea el pipeline conservando una referencia al crawler.

        Args:
            crawler (Crawler): Instancia del crawler de Scrapy.

        Returns:
            JsonLinesPipeline: El pipeline listo para abrir el archivo.
        """
        pipeline = cls()
        pipeline.crawler = crawler
        return pipeline

    def open_spider(self, spider: Any = None) -> None:
        """Abre el archivo de salida al iniciar el spider.

        Args:
            spider (Any): Spider en ejecución (Scrapy < 2.13 lo pasa como argumento).
        """
        spider = spider or self.crawler.spider
        destino = getattr(spider, "output_path", "cuspide_resultados.jl")
        Path(destino).parent.mkdir(parents=True, exist_ok=True)
        self.file = open(destino, "w", encoding="utf-8")

    def process_item(self, item: Any, spider: Any = None) -> Any:
        """Escribe el ítem como una línea JSON y lo devuelve.

        Args:
            item (Any): Ítem extraído por el spider.
            spider (Any): Spider en ejecución (Scrapy < 2.13 lo pasa como argumento).

        Returns:
            Any: El mismo ítem (sin modificar).
        """
        self.file.write(json.dumps(dict(item), ensure_ascii=False) + "\n")
        return item

    def close_spider(self, spider: Any = None) -> None:
        """Cierra el archivo de salida al finalizar el spider.

        Args:
            spider (Any): Spider en ejecución (Scrapy < 2.13 lo pasa como argumento).
        """
        self.file.close()
