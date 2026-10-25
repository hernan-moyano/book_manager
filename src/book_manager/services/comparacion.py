"""Comparación de precios internos con los obtenidos del scraper (Sprint 3).

Define :class:`ServicioComparacionPrecios`, que cruza los resultados del
scraper de Cúspide con el catálogo interno, calcula la diferencia de
precios, genera el archivo de alertas CSV (Ejercicio 04) y el reporte en
Excel (Ejercicio 05) dentro de la carpeta ``reportes``.

Cúspide publica cada libro en pesos y en dólares, por lo que cada precio
interno se compara en su propia moneda (ARS o USD).
"""
from __future__ import annotations

import csv
import json
import re
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import pandas as pd

# Moneda del precio interno -> campo del ítem del scraper con el precio web.
CAMPOS_PRECIO_WEB = {"ARS": "precio", "USD": "precio_usd"}

CAMPOS_ALERTAS = [
    "Libro",
    "Moneda",
    "Precio interno",
    "Precio web",
    "Diferencia",
    "Diferencia %",
    "Fecha de extracción",
    "Alerta",
]
COLUMNAS_EXCEL = ["Libro", "Moneda", "Precio interno", "Precio web", "Diferencia", "Fecha de extracción"]


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
    precios internos en ARS y USD) y la carpeta donde se escriben los reportes.
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
    def _elegir_resultado(
        libro: Any, candidatos: List[Dict[str, Any]], campo: str
    ) -> Optional[Dict[str, Any]]:
        """Elige la ficha de Cúspide que representa al libro en una moneda.

        Cúspide puede tener varias ediciones del mismo libro: se prefieren las
        de título exacto (no "Practicando el poder del ahora" para "El poder
        del ahora") y, entre ellas, la oferta más barata en esa moneda.

        Args:
            libro (Any): Libro del catálogo interno.
            candidatos (List[Dict[str, Any]]): Ítems del scraper de ese libro.
            campo (str): Campo del ítem con el precio web (``precio`` o
                ``precio_usd``).

        Returns:
            Optional[Dict[str, Any]]: El ítem elegido, o None si ninguna ficha
                informa el precio en esa moneda.
        """
        con_precio = [c for c in candidatos if c.get(campo)]
        palabras = normalizar_palabras(libro.titulo)
        exactos = [c for c in con_precio if normalizar_palabras(c.get("titulo_web")) == palabras]
        opciones = exactos or con_precio
        if not opciones:
            return None
        return min(opciones, key=lambda candidato: float(candidato[campo]))

    def comparar(
        self, resultados: List[Dict[str, Any]], porcentaje_alerta: float
    ) -> List[Dict[str, Any]]:
        """Cruza los resultados del scraper con el catálogo y calcula diferencias.

        Cada precio interno en ARS se compara con el precio web en pesos y
        cada precio interno en USD con el precio web en dólares.

        Args:
            resultados (List[Dict[str, Any]]): Ítems extraídos por el scraper
                (con ``titulo``, ``isbn_catalogo``, ``precio`` y ``precio_usd``).
            porcentaje_alerta (float): Diferencia porcentual (en valor
                absoluto) a partir de la cual se marca la alerta.

        Returns:
            List[Dict[str, Any]]: Una fila por libro y moneda comparables
                (elegida con :meth:`_elegir_resultado`) con las claves de
                ``CAMPOS_ALERTAS``.
        """
        precios: Dict[int, Dict[str, float]] = {}
        for precio in self.service.listar_precios():
            if precio.moneda.codigo in CAMPOS_PRECIO_WEB:
                precios.setdefault(precio.libro.id, {})[precio.moneda.codigo] = float(precio.monto)
        catalogo = self.service.listar_libros()
        libros = {libro.titulo.casefold(): libro for libro in catalogo}
        libros_por_isbn = {normalizar_isbn(libro.isbn): libro for libro in catalogo}

        por_libro: Dict[int, Any] = {}
        for resultado in resultados:
            isbn = normalizar_isbn(str(resultado.get("isbn_catalogo", "")))
            libro = libros_por_isbn.get(isbn) or libros.get(
                str(resultado.get("titulo", "")).casefold()
            )
            if libro is None or libro.id not in precios:
                continue
            por_libro.setdefault(libro.id, (libro, []))[1].append(resultado)

        filas: List[Dict[str, Any]] = []
        for libro, candidatos in por_libro.values():
            for moneda, interno in precios[libro.id].items():
                campo = CAMPOS_PRECIO_WEB[moneda]
                elegido = self._elegir_resultado(libro, candidatos, campo)
                if elegido is None:
                    continue
                precio_web = float(elegido[campo])
                fecha = elegido.get("fecha_extraccion") or datetime.now().isoformat(
                    timespec="seconds"
                )
                diferencia = precio_web - interno
                porcentaje = diferencia / interno * 100 if interno else 0.0
                filas.append(
                    {
                        "Libro": libro.titulo,
                        "Moneda": moneda,
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

        Columnas: Libro, Moneda, Precio interno, Precio web, Diferencia y
        Fecha de extracción.

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
