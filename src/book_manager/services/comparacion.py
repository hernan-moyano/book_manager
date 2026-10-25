"""Comparación de precios internos con los obtenidos del scraper (Sprint 3).

Define :class:`ServicioComparacionPrecios`, que cruza los resultados del
scraper de Cúspide con el catálogo interno, calcula la diferencia de
precios y genera el archivo de alertas CSV (Ejercicio 04) dentro de la
carpeta ``reportes``.
"""
from __future__ import annotations

import csv
import json
import re
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

CAMPOS_ALERTAS = [
    "Libro",
    "Precio interno",
    "Precio web",
    "Diferencia",
    "Diferencia %",
    "Fecha de extracción",
    "Alerta",
]


def normalizar_isbn(valor: Optional[str]) -> str:
    """Normaliza un ISBN quitando todo carácter que no sea dígito o ``X``.

    Args:
        valor (Optional[str]): ISBN en cualquier formato.

    Returns:
        str: ISBN normalizado en mayúsculas.
    """
    return re.sub(r"[^0-9Xx]", "", valor or "").upper()


def normalizar_palabras(valor: Optional[str]) -> Set[str]:
    """Devuelve las palabras de un texto sin acentos y en minúsculas.

    Args:
        valor (Optional[str]): Texto a normalizar (por ejemplo, un título).

    Returns:
        Set[str]: Conjunto de palabras normalizadas.
    """
    texto = unicodedata.normalize("NFKD", valor or "")
    texto = "".join(caracter for caracter in texto if not unicodedata.combining(caracter))
    return set(re.findall(r"[a-z0-9]+", texto.casefold()))


class ServicioComparacionPrecios:
    """Servicio que compara el precio interno con el precio web y reporta.

    Recibe el servicio de la librería (para acceder al catálogo y a los
    precios internos en ARS) y la carpeta donde se escriben los reportes.
    """

    def __init__(self, libreria_service: Any, reportes_dir: "str | Path") -> None:
        """Inyecta el servicio de dominio y la carpeta de reportes.

        Args:
            libreria_service (Any): Servicio de la librería con
                ``listar_libros()`` y ``listar_precios()``.
            reportes_dir (str | Path): Carpeta destino de los reportes.
        """
        self.service = libreria_service
        self.reportes_dir = Path(reportes_dir)
        self.reportes_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _elegir_resultado(libro: Any, candidatos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Elige la ficha de Cúspide que representa al libro del catálogo.

        Cúspide puede tener varias ediciones del mismo libro: se prefieren las
        de título exacto (no "Practicando el poder del ahora" para "El poder
        del ahora") y, entre ellas, la oferta más barata.

        Args:
            libro (Any): Libro del catálogo interno.
            candidatos (List[Dict[str, Any]]): Ítems del scraper de ese libro.

        Returns:
            Dict[str, Any]: El ítem elegido.
        """
        palabras = normalizar_palabras(libro.titulo)
        exactos = [c for c in candidatos if normalizar_palabras(c.get("titulo_web")) == palabras]
        return min(exactos or candidatos, key=lambda candidato: float(candidato["precio"]))

    def comparar(
        self, resultados: List[Dict[str, Any]], porcentaje_alerta: float
    ) -> List[Dict[str, Any]]:
        """Cruza los resultados del scraper con el catálogo y calcula diferencias.

        Args:
            resultados (List[Dict[str, Any]]): Ítems extraídos por el scraper
                (con ``titulo``, ``isbn_catalogo`` y ``precio``).
            porcentaje_alerta (float): Diferencia porcentual (en valor
                absoluto) a partir de la cual se marca la alerta.

        Returns:
            List[Dict[str, Any]]: Una fila por libro del catálogo encontrado
                (elegida con :meth:`_elegir_resultado`) con las claves de
                ``CAMPOS_ALERTAS``.
        """
        precios = {
            precio.libro.id: float(precio.monto)
            for precio in self.service.listar_precios()
            if precio.moneda.codigo == "ARS"
        }
        catalogo = self.service.listar_libros()
        libros = {libro.titulo.casefold(): libro for libro in catalogo}
        libros_por_isbn = {normalizar_isbn(libro.isbn): libro for libro in catalogo}

        por_libro: Dict[int, Any] = {}
        for resultado in resultados:
            isbn = normalizar_isbn(str(resultado.get("isbn_catalogo", "")))
            libro = libros_por_isbn.get(isbn) or libros.get(
                str(resultado.get("titulo", "")).casefold()
            )
            if libro is None or not resultado.get("precio") or libro.id not in precios:
                continue
            por_libro.setdefault(libro.id, (libro, []))[1].append(resultado)

        filas: List[Dict[str, Any]] = []
        for libro, candidatos in por_libro.values():
            elegido = self._elegir_resultado(libro, candidatos)
            precio_web = float(elegido["precio"])
            fecha = elegido.get("fecha_extraccion") or datetime.now().isoformat(
                timespec="seconds"
            )
            interno = precios[libro.id]
            diferencia = precio_web - interno
            porcentaje = diferencia / interno * 100 if interno else 0.0
            filas.append(
                {
                    "Libro": libro.titulo,
                    "Precio interno": interno,
                    "Precio web": precio_web,
                    "Diferencia": diferencia,
                    "Diferencia %": porcentaje,
                    "Fecha de extracción": fecha,
                    "Alerta": abs(porcentaje) >= porcentaje_alerta,
                }
            )
        return filas

    def guardar_alertas_csv(self, filas: List[Dict[str, Any]]) -> Path:
        """Genera el CSV con las filas que superan la diferencia de alerta.

        Args:
            filas (List[Dict[str, Any]]): Filas producidas por :meth:`comparar`.

        Returns:
            Path: Ruta del archivo ``alertas_precios.csv`` generado.
        """
        ruta = self.reportes_dir / "alertas_precios.csv"
        with ruta.open("w", newline="", encoding="utf-8") as archivo:
            writer = csv.DictWriter(archivo, fieldnames=CAMPOS_ALERTAS)
            writer.writeheader()
            writer.writerows(fila for fila in filas if fila["Alerta"])
        return ruta

    @staticmethod
    def _elegir_resultado(libro: Any, candidatos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Elige la ficha de Cúspide que representa al libro del catálogo.

        Cúspide puede tener varias ediciones del mismo libro: se prefieren las
        de título exacto (no "Practicando el poder del ahora" para "El poder
        del ahora") y, entre ellas, la oferta más barata.

        Args:
            libro (Any): Libro del catálogo interno.
            candidatos (List[Dict[str, Any]]): Ítems del scraper de ese libro.

        Returns:
            Dict[str, Any]: El ítem elegido.
        """
        palabras = normalizar_palabras(libro.titulo)
        exactos = [c for c in candidatos if normalizar_palabras(c.get("titulo_web")) == palabras]
        return min(exactos or candidatos, key=lambda candidato: float(candidato["precio"]))

    def comparar(
        self, resultados: List[Dict[str, Any]], porcentaje_alerta: float
    ) -> List[Dict[str, Any]]:
        """Cruza los resultados del scraper con el catálogo y calcula diferencias.

        Args:
            resultados (List[Dict[str, Any]]): Ítems extraídos por el scraper
                (con ``titulo``, ``isbn_catalogo`` y ``precio``).
            porcentaje_alerta (float): Diferencia porcentual (en valor
                absoluto) a partir de la cual se marca la alerta.

        Returns:
            List[Dict[str, Any]]: Una fila por libro del catálogo encontrado
                (elegida con :meth:`_elegir_resultado`) con las claves de
                ``CAMPOS_ALERTAS``.
        """
        precios = {
            precio.libro.id: float(precio.monto)
            for precio in self.service.listar_precios()
            if precio.moneda.codigo == "ARS"
        }
        catalogo = self.service.listar_libros()
        libros = {libro.titulo.casefold(): libro for libro in catalogo}
        libros_por_isbn = {normalizar_isbn(libro.isbn): libro for libro in catalogo}

        por_libro: Dict[int, Any] = {}
        for resultado in resultados:
            isbn = normalizar_isbn(str(resultado.get("isbn_catalogo", "")))
            libro = libros_por_isbn.get(isbn) or libros.get(
                str(resultado.get("titulo", "")).casefold()
            )
            if libro is None or not resultado.get("precio") or libro.id not in precios:
                continue
            por_libro.setdefault(libro.id, (libro, []))[1].append(resultado)

        filas: List[Dict[str, Any]] = []
        for libro, candidatos in por_libro.values():
            elegido = self._elegir_resultado(libro, candidatos)
            precio_web = float(elegido["precio"])
            fecha = elegido.get("fecha_extraccion") or datetime.now().isoformat(
                timespec="seconds"
            )
            interno = precios[libro.id]
            diferencia = precio_web - interno
            porcentaje = diferencia / interno * 100 if interno else 0.0
            filas.append(
                {
                    "Libro": libro.titulo,
                    "Precio interno": interno,
                    "Precio web": precio_web,
                    "Diferencia": diferencia,
                    "Diferencia %": porcentaje,
                    "Fecha de extracción": fecha,
                    "Alerta": abs(porcentaje) >= porcentaje_alerta,
                }
            )
        return filas

    def guardar_alertas_csv(self, filas: List[Dict[str, Any]]) -> Path:
        """Genera el CSV con las filas que superan la diferencia de alerta.

        Args:
            filas (List[Dict[str, Any]]): Filas producidas por :meth:`comparar`.

        Returns:
            Path: Ruta del archivo ``alertas_precios.csv`` generado.
        """
        ruta = self.reportes_dir / "alertas_precios.csv"
        with ruta.open("w", newline="", encoding="utf-8") as archivo:
            writer = csv.DictWriter(archivo, fieldnames=CAMPOS_ALERTAS)
            writer.writeheader()
            writer.writerows(fila for fila in filas if fila["Alerta"])
        return ruta

    def generar_excel(self, filas: List[Dict[str, Any]]) -> Path:
        """Genera el reporte Excel con la comparación de precios.

        Columnas: Libro, Precio interno, Precio web, Diferencia y Fecha de
        extracción.

        Args:
            filas (List[Dict[str, Any]]): Filas producidas por :meth:`comparar`.

        Returns:
            Path: Ruta del archivo ``reporte_comparacion_precios.xlsx``.
        """
        ruta = self.reportes_dir / "reporte_comparacion_precios.xlsx"
        pd.DataFrame(filas, columns=COLUMNAS_EXCEL).to_excel(ruta, index=False)
        return ruta

    @staticmethod
    def leer_resultados(ruta: "str | Path") -> List[Dict[str, Any]]:
        """Lee los ítems JSON Lines escritos por el pipeline del scraper.

        Args:
            ruta (str | Path): Ruta del archivo ``.jl``.

        Returns:
            List[Dict[str, Any]]: Ítems extraídos.
        """
        with Path(ruta).open(encoding="utf-8") as archivo:
            return [json.loads(linea) for linea in archivo if linea.strip()]
