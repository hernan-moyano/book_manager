"""Spider de Cúspide (Sprint 3).

Define :class:`CuspideSpider`, que busca en el sitio de Cúspide los libros
del catálogo interno (y solo esos) y extrae de cada ficha el precio, la URL
de la imagen, las formas de pago y la descripción detallada. Cada búsqueda
se realiza por título y toma como máximo los primeros 10 resultados, de los
que solo se descargan las fichas cuyo título y autor coinciden con el
catálogo (en Cúspide hay libros homónimos de distintos autores). Si ninguna
ficha coincide, se hace una única búsqueda adicional por el ISBN normalizado.
"""
from __future__ import annotations

import re
import unicodedata
from datetime import datetime
from typing import Any, AsyncIterator, Dict, Iterable, List, Optional, Set
from urllib.parse import quote_plus

import scrapy

from book_manager.scraper.items import LibroCuspideItem, LibroCuspideLoader, limpiar_texto

MAX_RESULTADOS_POR_BUSQUEDA = 10
URL_BUSQUEDA = "https://cuspide.com/?s={termino}&post_type=product"


def normalizar_isbn(valor: Optional[str]) -> str:
    """Normaliza un ISBN quitando todo carácter que no sea dígito o ``X``.

    Args:
        valor (Optional[str]): ISBN en cualquier formato (con guiones o espacios).

    Returns:
        str: ISBN normalizado en mayúsculas (por ejemplo ``9789500700011``).
    """
    return re.sub(r"[^0-9Xx]", "", valor or "").upper()


def normalizar_titulo(valor: Optional[str]) -> Set[str]:
    """Devuelve el conjunto de palabras normalizadas de un texto.

    Quita acentos, pasa a minúsculas y separa en tokens alfanuméricos para
    comparar títulos y autores con tolerancia a diferencias de formato.

    Args:
        valor (Optional[str]): Texto a normalizar.

    Returns:
        Set[str]: Conjunto de palabras normalizadas.
    """
    texto = unicodedata.normalize("NFKD", valor or "")
    texto = "".join(caracter for caracter in texto if not unicodedata.combining(caracter))
    return set(re.findall(r"[a-z0-9]+", texto.casefold()))


def titulo_coincide(esperado: str, obtenido: Optional[str]) -> bool:
    """Indica si el título obtenido coincide razonablemente con el esperado.

    Se considera coincidencia cuando al menos el 80 % de las palabras del
    título buscado aparecen en el título de la ficha.

    Args:
        esperado (str): Título del catálogo interno.
        obtenido (Optional[str]): Título mostrado en Cúspide.

    Returns:
        bool: True si la coincidencia supera el umbral, False en caso contrario.
    """
    palabras_esperadas = normalizar_titulo(esperado)
    palabras_obtenidas = normalizar_titulo(obtenido)
    if not palabras_esperadas or not palabras_obtenidas:
        return False
    coincidencias = len(palabras_esperadas & palabras_obtenidas)
    return coincidencias / len(palabras_esperadas) >= 0.8


def autor_coincide(esperado: str, obtenido: Optional[str]) -> Optional[bool]:
    """Indica si el autor de Cúspide coincide con el del catálogo.

    Compara las palabras sin importar el orden, de modo que
    ``Gabriel García Márquez`` coincide con ``GARCIA MARQUEZ, GABRIEL``. Se
    ignoran las palabras de hasta dos letras (``de``, ``la``...).

    Args:
        esperado (str): Autor del catálogo interno.
        obtenido (Optional[str]): Autor informado por Cúspide.

    Returns:
        Optional[bool]: True o False según coincida, True si el catálogo no
            tiene autor, o None si Cúspide no informa el autor.
    """
    palabras_esperadas = {palabra for palabra in normalizar_titulo(esperado) if len(palabra) > 2}
    if not palabras_esperadas:
        return True
    palabras_obtenidas = normalizar_titulo(obtenido)
    if not palabras_obtenidas:
        return None
    coincidencias = len(palabras_esperadas & palabras_obtenidas)
    return coincidencias / len(palabras_esperadas) >= 0.66


def isbn_coincide(esperado: str, contenido: str) -> bool:
    """Indica si el ISBN normalizado aparece dentro del contenido de la página.

    Args:
        esperado (str): ISBN del catálogo interno.
        contenido (str): HTML/texto completo de la ficha.

    Returns:
        bool: True si algún candidato a ISBN de la página coincide.
    """
    candidatos = re.findall(r"(?<![0-9])(?:[0-9][ -]?){12}[0-9Xx](?![0-9])", contenido)
    return normalizar_isbn(esperado) in {normalizar_isbn(c) for c in candidatos}


def primer_css(response: scrapy.http.Response, *selectores: str) -> List[str]:
    """Devuelve los textos del primer selector CSS que encuentra resultados.

    Args:
        response (scrapy.http.Response): Página de la ficha del libro.
        *selectores (str): Selectores CSS en orden de preferencia.

    Returns:
        List[str]: Textos no vacíos del primer selector con coincidencias.
    """
    for selector in selectores:
        textos = [texto for texto in response.css(selector).getall() if texto.strip()]
        if textos:
            return textos
    return []


def formas_de_pago(response: scrapy.http.Response) -> List[str]:
    """Extrae las formas de pago del popup "Medios de pago" de la ficha.

    Args:
        response (scrapy.http.Response): Página de la ficha del libro.

    Returns:
        List[str]: Formas de pago sin repetir, en el orden en que aparecen.
    """
    formas: List[str] = []
    for item in response.css("div.pum[data-popmake*='metodos-de-pago'] li"):
        texto = limpiar_texto(" ".join(item.css("::text").getall())).lstrip("> ")
        if texto and texto not in formas:
            formas.append(texto)
    return formas


class CuspideSpider(scrapy.Spider):
    """Spider que obtiene de Cúspide los datos de los libros del catálogo.

    Recibe la lista de libros del catálogo interno (título, autor e ISBN) y,
    para cada uno, busca por título tomando como máximo los primeros 10
    resultados; solo si ninguna ficha coincide hace una búsqueda adicional
    por ISBN.
    """

    name = "cuspide"
    allowed_domains = ["cuspide.com", "www.cuspide.com"]
    custom_settings = {
        "ITEM_PIPELINES": {
            "book_manager.scraper.pipelines.ValidarLibroPipeline": 100,
            "book_manager.scraper.pipelines.JsonLinesPipeline": 300,
        },
        "ROBOTSTXT_OBEY": True,
        "DOWNLOAD_TIMEOUT": 20,
        "CONCURRENT_REQUESTS": 4,
        "CLOSESPIDER_TIMEOUT": 120,
        "RETRY_ENABLED": False,
        "USER_AGENT": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
        ),
    }

    def __init__(self, libros: Iterable[Dict[str, Any]] = (), *args: Any, **kwargs: Any) -> None:
        """Configura el spider con los libros del catálogo a buscar.

        Args:
            libros (Iterable[Dict[str, Any]]): Libros del catálogo interno con
                las claves ``titulo``, ``autor`` e ``isbn``.
            output_path (str): (kwarg) Ruta del archivo ``.jl`` de salida.
        """
        super().__init__(*args, **kwargs)
        self.libros = [
            {
                "titulo": str(libro.get("titulo", "")).strip(),
                "autor": str(libro.get("autor", "") or "").strip(),
                "isbn": normalizar_isbn(str(libro.get("isbn", ""))),
            }
            for libro in libros
            if str(libro.get("titulo", "")).strip()
        ]

    def _request_busqueda(self, libro: Dict[str, str], criterio: str) -> scrapy.Request:
        """Arma la petición de búsqueda de un libro por título o ISBN.

        Args:
            libro (Dict[str, str]): Libro del catálogo.
            criterio (str): ``titulo`` o ``isbn``.

        Returns:
            scrapy.Request: Petición de búsqueda al sitio de Cúspide.
        """
        termino = libro["titulo"] if criterio == "titulo" else libro["isbn"]
        return scrapy.Request(
            URL_BUSQUEDA.format(termino=quote_plus(termino)),
            callback=self.parse_resultados,
            cb_kwargs={"libro": libro, "criterio": criterio},
        )

    def start_requests(self) -> Iterable[scrapy.Request]:
        """Genera la búsqueda por título de cada libro del catálogo.

        Returns:
            Iterable[scrapy.Request]: Una petición de búsqueda por libro.
        """
        for libro in self.libros:
            yield self._request_busqueda(libro, "titulo")

    async def start(self) -> AsyncIterator[scrapy.Request]:
        """Punto de entrada de Scrapy >= 2.13 (reemplaza a ``start_requests``).

        Yields:
            AsyncIterator[scrapy.Request]: Las búsquedas de :meth:`start_requests`.
        """
        for request in self.start_requests():
            yield request

    def _candidatos(
        self, response: scrapy.http.Response, libro: Dict[str, str], criterio: str
    ) -> List[str]:
        """Filtra los primeros 10 resultados sin descargar sus fichas.

        Cada tarjeta de resultado informa el título y, en general, el autor:
        solo se siguen las que coinciden con el libro del catálogo. Una
        tarjeta sin autor se sigue para confirmarlo en la ficha. En la
        búsqueda por ISBN se siguen todas (el ISBN se valida en la ficha).

        Args:
            response (scrapy.http.Response): Página de resultados de búsqueda.
            libro (Dict[str, str]): Libro del catálogo.
            criterio (str): Criterio de búsqueda usado (``titulo`` o ``isbn``).

        Returns:
            List[str]: URLs de las fichas candidatas, sin repetir.
        """
        candidatos: List[str] = []
        for tarjeta in response.css("div.product-small.col")[:MAX_RESULTADOS_POR_BUSQUEDA]:
            enlace = tarjeta.css("a.woocommerce-LoopProduct-link::attr(href)").get()
            if not enlace:
                continue
            if criterio == "titulo":
                titulo_web = tarjeta.css("p.product-title a::text").get()
                autor_web = tarjeta.css("p.author-product-loop a::text").get()
                if not titulo_coincide(libro["titulo"], titulo_web):
                    continue
                if autor_coincide(libro["autor"], autor_web) is False:
                    continue
            candidatos.append(enlace)
        return list(dict.fromkeys(candidatos))

    def parse_resultados(
        self, response: scrapy.http.Response, libro: Dict[str, str], criterio: str
    ) -> Iterable[Any]:
        """Sigue las fichas candidatas de los primeros 10 resultados.

        Si ningún resultado de la búsqueda por título es candidato, dispara la
        búsqueda de respaldo por ISBN.

        Args:
            response (scrapy.http.Response): Página de resultados de búsqueda.
            libro (Dict[str, str]): Libro del catálogo.
            criterio (str): Criterio de búsqueda usado (``titulo`` o ``isbn``).

        Yields:
            Iterable[Any]: Peticiones a cada ficha candidata o la búsqueda por ISBN.
        """
        enlaces = self._candidatos(response, libro, criterio)
        if not enlaces:
            if criterio == "titulo" and libro["isbn"]:
                yield self._request_busqueda(libro, "isbn")
            return
        estado = {"pendientes": len(enlaces), "coincidio": False}
        for enlace in enlaces:
            yield response.follow(
                enlace,
                self.parse_libro,
                cb_kwargs={"libro": libro, "criterio": criterio, "estado": estado},
            )

    def parse_libro(
        self,
        response: scrapy.http.Response,
        libro: Dict[str, str],
        criterio: str,
        estado: Dict[str, Any],
    ) -> Iterable[Any]:
        """Extrae los datos de la ficha si corresponde al libro buscado.

        En la búsqueda por título se exige que el título coincida y que el
        autor quede confirmado en la ficha; si Cúspide no informa el autor, la
        ficha se descarta para no confundir libros homónimos.

        Args:
            response (scrapy.http.Response): Página de la ficha del libro.
            libro (Dict[str, str]): Libro del catálogo.
            criterio (str): Criterio de búsqueda usado.
            estado (Dict[str, Any]): Estado compartido de la búsqueda (para el
                respaldo por ISBN cuando ninguna ficha coincide).

        Yields:
            Iterable[Any]: El ítem extraído o la búsqueda de respaldo por ISBN.
        """
        titulo_web = limpiar_texto(
            response.css("h1.product_title::text, h1.product-title::text").get("")
        )
        autor_web = limpiar_texto(
            response.css("p.livriz-authors::text, a[href*='/autor/']::text").get("")
        )
        isbn_web = normalizar_isbn(response.css("span.sku::text").get(""))
        if criterio == "titulo":
            coincide = (
                titulo_coincide(libro["titulo"], titulo_web)
                and autor_coincide(libro["autor"], autor_web) is True
            )
        else:
            coincide = isbn_web == libro["isbn"] or isbn_coincide(libro["isbn"], response.text)
        if coincide:
            loader = LibroCuspideLoader(item=LibroCuspideItem(), response=response)
            loader.add_value("titulo", libro["titulo"])
            loader.add_value("autor", libro["autor"])
            loader.add_value("isbn_catalogo", libro["isbn"])
            loader.add_value("criterio_busqueda", criterio)
            loader.add_value("titulo_web", titulo_web)
            loader.add_value("autor_web", autor_web)
            loader.add_value("isbn_web", isbn_web)
            loader.add_value("url", response.url)
            # Precio de la ficha (p.price; ins es el precio rebajado). El primer
            # span.woocommerce-Price-amount de la página es el carrito ($ 0,00).
            loader.add_value(
                "precio",
                primer_css(
                    response,
                    "p.price ins span.woocommerce-Price-amount bdi::text",
                    "p.price span.woocommerce-Price-amount bdi::text",
                    ".summary span.woocommerce-Price-amount bdi::text",
                ),
            )
            # Precio en dólares: "U$s <span>36,25</span>" debajo del precio en pesos.
            loader.add_xpath(
                "precio_usd",
                "//div[contains(@class, 'summary')]"
                "//span[starts-with(normalize-space(text()), 'U$s')]/span/text()",
            )
            # Imagen de portada: img.wp-post-image (CDN livriz).
            loader.add_css(
                "imagen_url",
                "img.wp-post-image::attr(src), "
                "img.wp-post-image::attr(data-src), "
                ".woocommerce-product-gallery__image img::attr(src)",
            )
            # Formas de pago: ítems del popup "Medios de pago" que abre la ficha.
            loader.add_value("formas_pago", formas_de_pago(response))
            # Descripción detallada: sinopsis livriz o pestaña de descripción.
            loader.add_value(
                "descripcion",
                primer_css(
                    response,
                    "p.livriz-text-synopsis ::text",
                    "#tab-description ::text",
                    ".woocommerce-Tabs-panel--description ::text",
                ),
            )
            loader.add_value("fecha_extraccion", datetime.now().isoformat(timespec="seconds"))
            item = loader.load_item()
            if item.get("precio"):
                estado["coincidio"] = True
                yield item
        estado["pendientes"] -= 1
        if (
            estado["pendientes"] == 0
            and not estado["coincidio"]
            and criterio == "titulo"
            and libro["isbn"]
        ):
            yield self._request_busqueda(libro, "isbn")
