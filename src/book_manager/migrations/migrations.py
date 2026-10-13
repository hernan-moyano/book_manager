"""Migracion de datos de los CSV del Sprint 1 a la base de datos.

Lee los archivos CSV de ``migrations/csv``, genera los archivos SQL con
las sentencias de insercion en ``migrations/sql`` y puebla las tablas de
la base de datos respetando el orden de sus relaciones.
"""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, List, Optional

from sqlalchemy import text

from book_manager.database.connection import ConexionDB

COLUMNAS_POR_TABLA: Dict[str, List[str]] = {
    "genero": ["id", "nombre"],
    "editorial": ["id", "nombre"],
    "moneda": ["id", "codigo", "descripcion"],
    "tipo_cotizacion": ["id", "nombre"],
    "libro": ["id", "isbn", "titulo", "autor", "editorial_id", "genero_id"],
    "precio": ["id", "libro_id", "moneda_id", "monto"],
    "stock": ["libro_id", "cantidad"],
    "cotizacion_dolar": ["tipo_id", "fecha", "valor"],
}

COLUMNAS_ENTERAS = {"id", "editorial_id", "genero_id", "libro_id", "moneda_id",
                    "tipo_id", "cantidad"}
COLUMNAS_DECIMALES = {"monto", "valor"}


def _leer_csv(ruta: Path) -> List[Dict[str, str]]:
    """Lee un archivo CSV y devuelve sus filas como diccionarios."""
    if not ruta.exists():
        raise FileNotFoundError(f"No existe el archivo de origen: {ruta}")
    with open(ruta, "r", newline="", encoding="utf-8") as archivo:
        return list(csv.DictReader(archivo))


def _literal(columna: str, valor: str) -> str:
    """Convierte el valor del CSV en un literal SQL seguro."""
    if columna in COLUMNAS_ENTERAS:
        return str(int(valor))
    if columna in COLUMNAS_DECIMALES:
        return str(float(valor))
    return "'" + valor.replace("'", "''") + "'"


def _sentencia_insert(tabla: str, fila: Dict[str, str]) -> str:
    """Arma la sentencia INSERT de una fila para la tabla indicada."""
    columnas = COLUMNAS_POR_TABLA[tabla]
    valores = ", ".join(_literal(columna, fila[columna]) for columna in columnas)
    return f"INSERT INTO {tabla} ({', '.join(columnas)}) VALUES ({valores});"


def _base_vacia(conexion: ConexionDB) -> bool:
    """Indica si la tabla principal de la base de datos no tiene filas."""
    with conexion.engine.connect() as conn:
        total = conn.execute(text("SELECT COUNT(*) FROM genero")).scalar()
    return not total


def migrar_datos(
    carpeta_csvs: str,
    carpeta_sqls: str,
    conexion: Optional[ConexionDB] = None,
    solo_si_vacia: bool = True,
) -> None:
    """Funcion encargada de la migracion de datos de csv a sql.

    Se encarga de leer los archivos csv y crear los archivos sql
    para la insercion en la base de datos.

    Args:
        carpeta_csvs (str): Carpeta donde se encuentran los archivos csv de origen.
        carpeta_sqls (str): Carpeta donde se deben guardar los archivos sql generados.
        conexion (Optional[ConexionDB]): Conexion existente a reutilizar. Si no se
            indica se crea una nueva con la configuracion del archivo ``.env``.
        solo_si_vacia (bool): Omite la insercion en la base si ya hay datos.
    """
    origen = Path(carpeta_csvs)
    destino = Path(carpeta_sqls)
    destino.mkdir(parents=True, exist_ok=True)

    sentencias: Dict[str, List[str]] = {}
    for tabla, columnas in COLUMNAS_POR_TABLA.items():
        filas = _leer_csv(origen / f"{tabla}.csv")
        sentencias[tabla] = [_sentencia_insert(tabla, fila) for fila in filas]
        ruta_sql = destino / f"{tabla}.sql"
        ruta_sql.write_text("\n".join(sentencias[tabla]) + "\n", encoding="utf-8")
        print(f"SQL generado: {ruta_sql.name} ({len(filas)} inserciones)")

    if conexion is None:
        conexion = ConexionDB()
    conexion.crear_tablas()

    if solo_si_vacia and not _base_vacia(conexion):
        print("La base de datos ya contiene datos: se omiten las inserciones.")
        return

    total = 0
    with conexion.engine.begin() as conn:
        for tabla in COLUMNAS_POR_TABLA:
            for sentencia in sentencias[tabla]:
                conn.execute(text(sentencia))
                total += 1
        if conn.dialect.name == "postgresql":
            _reajustar_secuencias(conn)
    print(f"Migracion completada: {total} registros insertados en la base de datos.")


def _reajustar_secuencias(conn) -> None:
    """Sincroniza las secuencias (SERIAL) de las tablas con ``id`` explícito.

    Al insertar identificadores explícitos desde el CSV, la secuencia de
    PostgreSQL queda por detrás del máximo actual. Se reajusta con ``setval``
    para evitar colisiones en próximas inserciones.
    """
    for tabla, columnas in COLUMNAS_POR_TABLA.items():
        if "id" not in columnas:
            continue
        conn.execute(
            text(
                "SELECT setval(pg_get_serial_sequence('{tabla}', 'id'), "
                "COALESCE((SELECT MAX(id) FROM {tabla}), 1))".format(tabla=tabla)
            )
        )
