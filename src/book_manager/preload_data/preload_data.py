"""Precarga de datos del sistema Book Manager.

Genera los archivos CSV de migración (mínimo 10 registros por entidad)
dentro de la carpeta ``migrations/csv`` y permite importarlos al servicio.
Se utiliza únicamente la librería estándar ``csv``.
"""
from __future__ import annotations

import csv
from datetime import date, timedelta
from pathlib import Path
from typing import Dict, List

from book_manager.entities.entities import (
    CotizacionDolar,
    Editorial,
    Genero,
    Libro,
    Moneda,
    Precio,
    Stock,
    TipoCotizacion,
)
from book_manager.services.services import LibreriaService

RUTA_CSV_POR_DEFECTO = Path(__file__).resolve().parent.parent / "migrations" / "csv"

CSV_POR_ENTIDAD = {
    "genero": "genero.csv",
    "editorial": "editorial.csv",
    "moneda": "moneda.csv",
    "tipo_cotizacion": "tipo_cotizacion.csv",
    "libro": "libro.csv",
    "precio": "precio.csv",
    "stock": "stock.csv",
    "cotizacion_dolar": "cotizacion_dolar.csv",
}


def _escribir_csv(path: Path, filas: List[Dict[str, object]]) -> None:
    """Escribe una lista de diccionarios como archivo CSV con encabezado."""
    with open(path, "w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=list(filas[0].keys()))
        escritor.writeheader()
        escritor.writerows(filas)


def _leer_csv(path: Path) -> List[Dict[str, str]]:
    """Lee un archivo CSV y devuelve sus filas como diccionarios."""
    with open(path, "r", newline="", encoding="utf-8") as archivo:
        return list(csv.DictReader(archivo))


def generar_csv_demo(base_dir: str = str(RUTA_CSV_POR_DEFECTO)) -> Path:
    """Genera los CSV de datos iniciales (10 registros por entidad)."""
    base_path = Path(base_dir)
    base_path.mkdir(parents=True, exist_ok=True)

    generos = [
        {"id": 1, "nombre": "Novela"},
        {"id": 2, "nombre": "Ensayo"},
        {"id": 3, "nombre": "Infantil"},
        {"id": 4, "nombre": "Técnico"},
        {"id": 5, "nombre": "Ciencia Ficción"},
        {"id": 6, "nombre": "Historia"},
        {"id": 7, "nombre": "Biografía"},
        {"id": 8, "nombre": "Poesía"},
        {"id": 9, "nombre": "Policial"},
        {"id": 10, "nombre": "Autoayuda"},
    ]
    editoriales = [
        {"id": 1, "nombre": "Sudamericana"},
        {"id": 2, "nombre": "Planeta"},
        {"id": 3, "nombre": "Penguin Random House"},
        {"id": 4, "nombre": "Siglo XXI"},
        {"id": 5, "nombre": "Anagrama"},
        {"id": 6, "nombre": "Alfaguara"},
        {"id": 7, "nombre": "Emecé"},
        {"id": 8, "nombre": "Paidós"},
        {"id": 9, "nombre": "Debolsillo"},
        {"id": 10, "nombre": "El Ateneo"},
    ]
    monedas = [
        {"id": 1, "codigo": "ARS", "descripcion": "Peso argentino"},
        {"id": 2, "codigo": "USD", "descripcion": "Dólar estadounidense"},
        {"id": 3, "codigo": "EUR", "descripcion": "Euro"},
        {"id": 4, "codigo": "BRL", "descripcion": "Real brasileiro"},
        {"id": 5, "codigo": "UYU", "descripcion": "Peso uruguayo"},
        {"id": 6, "codigo": "CLP", "descripcion": "Peso chileno"},
        {"id": 7, "codigo": "GBP", "descripcion": "Libra esterlina"},
        {"id": 8, "codigo": "MXN", "descripcion": "Peso mexicano"},
        {"id": 9, "codigo": "COP", "descripcion": "Peso colombiano"},
        {"id": 10, "codigo": "PEN", "descripcion": "Sol peruano"},
    ]
    tipos_cotizacion = [
        {"id": 1, "nombre": "Oficial"},
        {"id": 2, "nombre": "Blue"},
        {"id": 3, "nombre": "MEP"},
        {"id": 4, "nombre": "CCL"},
        {"id": 5, "nombre": "Tarjeta"},
        {"id": 6, "nombre": "Cripto"},
        {"id": 7, "nombre": "Mayorista"},
        {"id": 8, "nombre": "Turista"},
        {"id": 9, "nombre": "Bolsa"},
        {"id": 10, "nombre": "Futuro"},
    ]
    libros = [
        {"id": 1, "isbn": "978-950-07-0001-1", "titulo": "Cien años de soledad", "autor": "Gabriel García Márquez", "editorial_id": 1, "genero_id": 1},
        {"id": 2, "isbn": "978-950-07-0002-2", "titulo": "El Aleph", "autor": "Jorge Luis Borges", "editorial_id": 7, "genero_id": 1},
        {"id": 3, "isbn": "978-950-07-0003-3", "titulo": "Sobre héroes y tumbas", "autor": "Ernesto Sabato", "editorial_id": 1, "genero_id": 2},
        {"id": 4, "isbn": "978-950-07-0004-4", "titulo": "Python para todos", "autor": "Raúl González Duque", "editorial_id": 4, "genero_id": 4},
        {"id": 5, "isbn": "978-950-07-0005-5", "titulo": "Fundación", "autor": "Isaac Asimov", "editorial_id": 9, "genero_id": 5},
        {"id": 6, "isbn": "978-950-07-0006-6", "titulo": "Breve historia del tiempo", "autor": "Stephen Hawking", "editorial_id": 2, "genero_id": 6},
        {"id": 7, "isbn": "978-950-07-0007-7", "titulo": "Steve Jobs", "autor": "Walter Isaacson", "editorial_id": 3, "genero_id": 7},
        {"id": 8, "isbn": "978-950-07-0008-8", "titulo": "Poesía completa", "autor": "Alejandra Pizarnik", "editorial_id": 5, "genero_id": 8},
        {"id": 9, "isbn": "978-950-07-0009-9", "titulo": "La sombra del viento", "autor": "Carlos Ruiz Zafón", "editorial_id": 2, "genero_id": 9},
        {"id": 10, "isbn": "978-950-07-0010-0", "titulo": "El poder del ahora", "autor": "Eckhart Tolle", "editorial_id": 8, "genero_id": 10},
    ]
    precios = [
        {"id": 1, "libro_id": 1, "moneda_id": 1, "monto": 12500.0},
        {"id": 2, "libro_id": 2, "moneda_id": 1, "monto": 11200.0},
        {"id": 3, "libro_id": 3, "moneda_id": 2, "monto": 18.5},
        {"id": 4, "libro_id": 4, "moneda_id": 1, "monto": 22000.0},
        {"id": 5, "libro_id": 5, "moneda_id": 2, "monto": 15.0},
        {"id": 6, "libro_id": 6, "moneda_id": 1, "monto": 19800.0},
        {"id": 7, "libro_id": 7, "moneda_id": 2, "monto": 24.9},
        {"id": 8, "libro_id": 8, "moneda_id": 1, "monto": 14300.0},
        {"id": 9, "libro_id": 9, "moneda_id": 2, "monto": 21.0},
        {"id": 10, "libro_id": 10, "moneda_id": 1, "monto": 16750.0},
    ]
    stock = [
        {"libro_id": 1, "cantidad": 12},
        {"libro_id": 2, "cantidad": 8},
        {"libro_id": 3, "cantidad": 4},
        {"libro_id": 4, "cantidad": 15},
        {"libro_id": 5, "cantidad": 6},
        {"libro_id": 6, "cantidad": 9},
        {"libro_id": 7, "cantidad": 3},
        {"libro_id": 8, "cantidad": 11},
        {"libro_id": 9, "cantidad": 5},
        {"libro_id": 10, "cantidad": 14},
    ]
    hoy = date.today()
    cotizaciones = [
        {"tipo_id": i, "fecha": (hoy - timedelta(days=i - 1)).isoformat(), "valor": float(900 + (i - 1) * 12)}
        for i in range(1, 11)
    ]

    _escribir_csv(base_path / "genero.csv", generos)
    _escribir_csv(base_path / "editorial.csv", editoriales)
    _escribir_csv(base_path / "moneda.csv", monedas)
    _escribir_csv(base_path / "tipo_cotizacion.csv", tipos_cotizacion)
    _escribir_csv(base_path / "libro.csv", libros)
    _escribir_csv(base_path / "precio.csv", precios)
    _escribir_csv(base_path / "stock.csv", stock)
    _escribir_csv(base_path / "cotizacion_dolar.csv", cotizaciones)

    return base_path


def cargar_datos_desde_csv(
    service: LibreriaService, base_dir: str = str(RUTA_CSV_POR_DEFECTO)
) -> None:
    """Importa al servicio los datos de los CSV en el orden de sus relaciones."""
    base = Path(base_dir)

    for row in _leer_csv(base / "genero.csv"):
        g_id = int(row["id"])
        if service.genero_service.obtener_genero(g_id) is None:
            service.alta_genero(Genero(g_id, row["nombre"]))

    for row in _leer_csv(base / "editorial.csv"):
        e_id = int(row["id"])
        if service.editorial_service.obtener_editorial(e_id) is None:
            service.alta_editorial(Editorial(e_id, row["nombre"]))

    for row in _leer_csv(base / "moneda.csv"):
        m_id = int(row["id"])
        if service.moneda_service.obtener_moneda(m_id) is None:
            service.alta_moneda(Moneda(m_id, row["codigo"], row["descripcion"]))

    for row in _leer_csv(base / "tipo_cotizacion.csv"):
        t_id = int(row["id"])
        if service.tipo_cotizacion_service.obtener_tipo_cotizacion(t_id) is None:
            service.alta_tipo_cotizacion(TipoCotizacion(t_id, row["nombre"]))

    for row in _leer_csv(base / "libro.csv"):
        l_id = int(row["id"])
        if service.libro_service.obtener_libro(l_id) is None:
            editorial = service.editorial_service.obtener_editorial(int(row["editorial_id"]))
            genero = service.genero_service.obtener_genero(int(row["genero_id"]))
            if editorial and genero:
                service.alta_libro(
                    Libro(
                        l_id,
                        row["isbn"],
                        row["titulo"],
                        row["autor"],
                        editorial,
                        genero,
                    )
                )

    for row in _leer_csv(base / "precio.csv"):
        p_id = int(row["id"])
        if service.precio_service.obtener_precio(p_id) is None:
            libro = service.libro_service.obtener_libro(int(row["libro_id"]))
            moneda = service.moneda_service.obtener_moneda(int(row["moneda_id"]))
            if libro and moneda:
                service.alta_precio(
                    Precio(
                        p_id,
                        libro,
                        moneda,
                        float(row["monto"]),
                    )
                )

    for row in _leer_csv(base / "stock.csv"):
        libro_id = int(row["libro_id"])
        if service.stock_service.obtener_stock(libro_id) is None:
            libro = service.libro_service.obtener_libro(libro_id)
            if libro:
                service.alta_stock(Stock(libro, int(row["cantidad"])))

    for row in _leer_csv(base / "cotizacion_dolar.csv"):
        tipo_id = int(row["tipo_id"])
        f_date = date.fromisoformat(row["fecha"])
        if service.cotizacion_service.obtener_cotizacion(tipo_id, f_date) is None:
            tipo = service.tipo_cotizacion_service.obtener_tipo_cotizacion(tipo_id)
            if tipo:
                service.alta_cotizacion(
                    CotizacionDolar(
                        tipo,
                        f_date,
                        float(row["valor"]),
                    )
                )
