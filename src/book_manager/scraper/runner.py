"""Ejecutor del spider de Cúspide en un subproceso aislado (Sprint 3).

Ejecutar Scrapy dentro de un notebook o de un intérprete interactivo choca
con el reactor de Twisted ya instalado (asyncio de Jupyter). Para que el
scraping sea reproducible tanto en Windows como en Colab, el spider se
lanza en un subproceso de Python independiente con ``CrawlerProcess``,
que instala su propio reactor limpio.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, List

# Margen sobre el CLOSESPIDER_TIMEOUT del spider antes de cancelar el subproceso.
TIMEOUT_SUBPROCESO = 300


def ejecutar_scraping(libros: List[Dict[str, str]], salida: "str | Path") -> int:
    """Ejecuta el spider de Cúspide en un subproceso y escribe el ``.jl``.

    Args:
        libros (List[Dict[str, str]]): Libros del catálogo interno con las
            claves ``titulo`` e ``isbn``.
        salida (str | Path): Ruta del archivo JSON Lines de salida.

    Returns:
        int: Código de salida del subproceso (0 si el scraping terminó bien).
    """
    destino = Path(salida)
    destino.parent.mkdir(parents=True, exist_ok=True)

    # Serializar los libros a un archivo temporal para pasarlos al subproceso.
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    ) as tmp:
        json.dump(libros, tmp, ensure_ascii=False)
        ruta_libros = tmp.name

    # CrawlerProcess instala el reactor configurado por Scrapy (en Windows ya
    # elige el SelectorEventLoop); instalarlo a mano bloquea el spider. Los
    # timeouts y la concurrencia los define custom_settings del spider.
    script = "\n".join(
        [
            "import json, sys",
            "from scrapy.crawler import CrawlerProcess",
            "from scrapy.utils.project import get_project_settings",
            "from book_manager.scraper.spiders.cuspide_spider import CuspideSpider",
            "libros = json.load(open(sys.argv[1], encoding='utf-8'))",
            "s = get_project_settings()",
            "s.set('LOG_LEVEL', 'WARNING')",
            "p = CrawlerProcess(s)",
            "p.crawl(CuspideSpider, libros=libros, output_path=sys.argv[2])",
            "p.start()",
        ]
    )
    # Garantizar que el subproceso encuentre el paquete en src/.
    src = str(Path(__file__).resolve().parents[2])
    env = dict(os.environ)
    env["PYTHONPATH"] = src + os.pathsep + env.get("PYTHONPATH", "")
    env["PYTHONIOENCODING"] = "utf-8"
    try:
        resultado = subprocess.run(
            [sys.executable, "-c", script, ruta_libros, str(destino)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
            timeout=TIMEOUT_SUBPROCESO,
        )
    except subprocess.TimeoutExpired:
        print(f"El scraping superó los {TIMEOUT_SUBPROCESO} segundos y se canceló.")
        return 1
    finally:
        os.remove(ruta_libros)
    if resultado.stderr:
        # Mostrar las últimas líneas del log del scraper (crawls y errores).
        lineas = [linea for linea in resultado.stderr.splitlines() if linea.strip()]
        print("Log del scraper (últimas líneas):")
        for linea in lineas[-12:]:
            print("   ", linea)
    return resultado.returncode
