"""Punto de entrada del sistema Book Manager."""
from __future__ import annotations

from book_manager.database.connection import ConexionDB
from book_manager.migrations.migrations import migrar_datos
from book_manager.preload_data.preload_data import (
    RUTA_CSV_POR_DEFECTO,
    generar_csv_demo,
)
from book_manager.services.services import LibreriaService
from book_manager.ui.console import ConsolaLibreria

RUTA_SQL_POR_DEFECTO = RUTA_CSV_POR_DEFECTO.parent / "sql"


def crear_app(import_default_data: bool = True) -> LibreriaService:
    """Crea la aplicación: conecta a la base de datos y carga los datos iniciales.

    Args:
        import_default_data (bool): Migra los CSV a la base de datos si está vacía.

    Returns:
        LibreriaService: El servicio de la librería listo para usar.
    """
    conexion = ConexionDB()
    conexion.crear_tablas()
    if import_default_data:
        if not any(RUTA_CSV_POR_DEFECTO.glob("*.csv")):
            generar_csv_demo(str(RUTA_CSV_POR_DEFECTO))
        migrar_datos(str(RUTA_CSV_POR_DEFECTO), str(RUTA_SQL_POR_DEFECTO), conexion)
    return LibreriaService.crear_con_base_de_datos(conexion)


def main(import_default_data: bool = True, interactive: bool = True) -> None:
    """Inicia la aplicación.

    ``interactive=False`` permite validar el notebook con "Ejecutar todo"
    sin bloquear la ejecución esperando entradas del usuario. La función no
    devuelve ningún objeto para que su ejecución en el notebook no imprima
    la representación del servicio al final de la salida.

    Args:
        import_default_data (bool): Migra los CSV a la base de datos si está
            vacía.
        interactive (bool): Si es True arranca la consola interactiva.
    """
    service = crear_app(import_default_data=import_default_data)
    if interactive:
        ConsolaLibreria(service).ejecutar()


if __name__ == "__main__":
    main(import_default_data=True, interactive=True)
