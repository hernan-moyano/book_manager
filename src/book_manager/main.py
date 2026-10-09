"""Punto de entrada del sistema Book Manager."""
from __future__ import annotations

from pathlib import Path

from book_manager.preload_data.preload_data import (
    RUTA_CSV_POR_DEFECTO,
    cargar_datos_desde_csv,
    generar_csv_demo,
)
from book_manager.services.services import LibreriaService
from book_manager.ui.console import ConsolaLibreria


def crear_app(
    import_default_data: bool = True, base_dir: Path | str = RUTA_CSV_POR_DEFECTO
) -> LibreriaService:
    """Crea la aplicación con persistencia en archivos CSV y precarga inicial opcional."""
    base_path = Path(base_dir)
    if import_default_data:
        generar_csv_demo(str(base_path))

    service = LibreriaService.crear_con_archivos_csv(base_dir=base_path)

    if import_default_data:
        cargar_datos_desde_csv(service, str(base_path))

    return service


def main(
    import_default_data: bool = True, interactive: bool = True
) -> None:
    """Inicia la aplicación.

    ``interactive=False`` permite validar el notebook con "Ejecutar todo"
    sin bloquear la ejecución esperando entradas del usuario.
    """
    service = crear_app(import_default_data=import_default_data)
    if interactive:
        ConsolaLibreria(service).ejecutar()


if __name__ == "__main__":
    main(import_default_data=True, interactive=True)
