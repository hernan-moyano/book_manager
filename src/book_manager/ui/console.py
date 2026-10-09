"""Interfaz de consola (CLI) del sistema Book Manager.

Cada menú opera directamente sobre los servicios de la librería,
permitiendo listar, dar de alta, modificar y borrar cada entidad
con validación robusta y manejo de errores ante datos mal ingresados.
"""
from __future__ import annotations

from datetime import date
from typing import Callable, List

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


class ConsolaLibreria:
    """Menús de consola para operar el CRUD de cada entidad del sistema."""

    def __init__(self, service: LibreriaService) -> None:
        self.service = service

    # --------------------------- Utilidades de E/S ---------------------------
    def _leer_int(self, texto: str) -> int:
        """Lee un entero por consola reintentando de forma segura ante errores."""
        while True:
            valor = input(texto).strip()
            try:
                return int(valor)
            except ValueError:
                print("Entrada inválida: debe ingresar un número entero.")

    def _leer_float(self, texto: str) -> float:
        """Lee un flotante por consola reintentando de forma segura ante errores."""
        while True:
            valor = input(texto).strip()
            try:
                return float(valor)
            except ValueError:
                print("Entrada inválida: debe ingresar un número decimal válido.")

    def _leer_fecha(self, texto: str) -> date:
        """Lee una fecha en formato YYYY-MM-DD reintentando de forma segura."""
        while True:
            valor = input(texto).strip()
            try:
                return date.fromisoformat(valor)
            except ValueError:
                print("Formato de fecha inválido. Ingrese una fecha válida con formato AAAA-MM-DD.")

    def _pausa(self) -> None:
        input("\nEnter para continuar...")

    def _listar(self, nombre: str, items: List[object]) -> None:
        print(f"\n--- {nombre} ---")
        if not items:
            print("Sin registros")
            return
        for item in items:
            print(item)

    # --------------------------- Menú CRUD genérico --------------------------
    def _menu_crud_basico(
        self,
        titulo: str,
        crear_cb: Callable[[], object],
        actualizar_cb: Callable[[], object],
        eliminar_cb: Callable[[], object],
        listar_cb: Callable[[], List[object]],
    ) -> None:
        while True:
            print(f"\n{titulo}: 1-Listar 2-Alta 3-Modificar 4-Borrar 0-Volver")
            op = input("Opción: ").strip()
            try:
                if op == "1":
                    self._listar(titulo, listar_cb())
                    self._pausa()
                elif op == "2":
                    crear_cb()
                    print("Alta exitosa")
                    self._pausa()
                elif op == "3":
                    actualizar_cb()
                    print("Modificación exitosa")
                    self._pausa()
                elif op == "4":
                    eliminado = eliminar_cb()
                    print("Borrado exitoso" if eliminado else "No se encontró el registro")
                    self._pausa()
                elif op == "0":
                    return
                else:
                    print("Opción inválida")
            except (ValueError, TypeError) as exc:
                print(f"Error: {exc}")
                self._pausa()

    # ---------------------------- Menús por entidad --------------------------
    def menu_generos(self) -> None:
        self._menu_crud_basico(
            "Géneros",
            lambda: self.service.alta_genero(
                Genero(self._leer_int("ID: "), input("Nombre: "))
            ),
            lambda: self.service.modificar_genero(
                Genero(self._leer_int("ID: "), input("Nombre: "))
            ),
            lambda: self.service.eliminar_genero(self._leer_int("ID: ")),
            self.service.listar_generos,
        )

    def menu_editoriales(self) -> None:
        self._menu_crud_basico(
            "Editoriales",
            lambda: self.service.alta_editorial(
                Editorial(self._leer_int("ID: "), input("Nombre: "))
            ),
            lambda: self.service.modificar_editorial(
                Editorial(self._leer_int("ID: "), input("Nombre: "))
            ),
            lambda: self.service.eliminar_editorial(self._leer_int("ID: ")),
            self.service.listar_editoriales,
        )

    def menu_monedas(self) -> None:
        self._menu_crud_basico(
            "Monedas",
            lambda: self.service.alta_moneda(
                Moneda(
                    self._leer_int("ID: "),
                    input("Código (3 letras): "),
                    input("Descripción: "),
                )
            ),
            lambda: self.service.modificar_moneda(
                Moneda(
                    self._leer_int("ID: "),
                    input("Código (3 letras): "),
                    input("Descripción: "),
                )
            ),
            lambda: self.service.eliminar_moneda(self._leer_int("ID: ")),
            self.service.listar_monedas,
        )

    def menu_tipos_cotizacion(self) -> None:
        self._menu_crud_basico(
            "Tipos de cotización",
            lambda: self.service.alta_tipo_cotizacion(
                TipoCotizacion(self._leer_int("ID: "), input("Nombre: "))
            ),
            lambda: self.service.modificar_tipo_cotizacion(
                TipoCotizacion(self._leer_int("ID: "), input("Nombre: "))
            ),
            lambda: self.service.eliminar_tipo_cotizacion(self._leer_int("ID: ")),
            self.service.listar_tipos_cotizacion,
        )

    def _construir_libro_desde_input(self, id_existente: int | None = None) -> Libro:
        libro_id = id_existente if id_existente is not None else self._leer_int("ID: ")
        isbn = input("ISBN: ").strip()
        titulo = input("Título: ").strip()
        autor = input("Autor: ").strip()
        editorial_id = self._leer_int("Editorial ID: ")
        editorial = self.service.editorial_service.obtener_editorial(editorial_id)
        if editorial is None:
            raise ValueError(f"No existe la editorial con ID {editorial_id}")
        genero_id = self._leer_int("Género ID: ")
        genero = self.service.genero_service.obtener_genero(genero_id)
        if genero is None:
            raise ValueError(f"No existe el género con ID {genero_id}")
        return Libro(
            id=libro_id,
            isbn=isbn,
            titulo=titulo,
            autor=autor,
            editorial=editorial,
            genero=genero,
        )

    def menu_libros(self) -> None:
        self._menu_crud_basico(
            "Libros",
            lambda: self.service.alta_libro(self._construir_libro_desde_input()),
            lambda: self.service.modificar_libro(self._construir_libro_desde_input()),
            lambda: self.service.eliminar_libro(self._leer_int("ID: ")),
            self.service.listar_libros,
        )

    def _construir_precio_desde_input(self, id_existente: int | None = None) -> Precio:
        precio_id = id_existente if id_existente is not None else self._leer_int("ID: ")
        libro_id = self._leer_int("Libro ID: ")
        libro = self.service.libro_service.obtener_libro(libro_id)
        if libro is None:
            raise ValueError(f"No existe el libro con ID {libro_id}")
        moneda_id = self._leer_int("Moneda ID: ")
        moneda = self.service.moneda_service.obtener_moneda(moneda_id)
        if moneda is None:
            raise ValueError(f"No existe la moneda con ID {moneda_id}")
        monto = self._leer_float("Monto: ")
        return Precio(id=precio_id, libro=libro, moneda=moneda, monto=monto)

    def menu_precios(self) -> None:
        self._menu_crud_basico(
            "Precios",
            lambda: self.service.alta_precio(self._construir_precio_desde_input()),
            lambda: self.service.modificar_precio(self._construir_precio_desde_input()),
            lambda: self.service.eliminar_precio(self._leer_int("ID: ")),
            self.service.listar_precios,
        )

    def _construir_stock_desde_input(self) -> Stock:
        libro_id = self._leer_int("Libro ID: ")
        libro = self.service.libro_service.obtener_libro(libro_id)
        if libro is None:
            raise ValueError(f"No existe el libro con ID {libro_id}")
        cantidad = self._leer_int("Cantidad: ")
        return Stock(libro=libro, cantidad=cantidad)

    def menu_stock(self) -> None:
        self._menu_crud_basico(
            "Stock",
            lambda: self.service.alta_stock(self._construir_stock_desde_input()),
            lambda: self.service.modificar_stock(self._construir_stock_desde_input()),
            lambda: self.service.eliminar_stock(self._leer_int("Libro ID: ")),
            self.service.listar_stock,
        )

    def _construir_cotizacion_desde_input(self) -> CotizacionDolar:
        tipo_id = self._leer_int("Tipo ID: ")
        tipo = self.service.tipo_cotizacion_service.obtener_tipo_cotizacion(tipo_id)
        if tipo is None:
            raise ValueError(f"No existe el tipo de cotización con ID {tipo_id}")
        fecha = self._leer_fecha("Fecha (YYYY-MM-DD): ")
        valor = self._leer_float("Valor: ")
        return CotizacionDolar(tipo=tipo, fecha=fecha, valor=valor)

    def menu_cotizaciones(self) -> None:
        self._menu_crud_basico(
            "Cotizaciones",
            lambda: self.service.alta_cotizacion(
                self._construir_cotizacion_desde_input()
            ),
            lambda: self.service.modificar_cotizacion(
                self._construir_cotizacion_desde_input()
            ),
            lambda: self.service.eliminar_cotizacion(
                self._leer_int("Tipo ID: "),
                self._leer_fecha("Fecha (YYYY-MM-DD): "),
            ),
            self.service.listar_cotizaciones,
        )

    def menu_reportes(self) -> None:
        while True:
            print("\n--- Reportes ---")
            print("1. Stock bajo")
            print("2. Libros agrupados por género")
            print("0. Volver")
            op = input("Opción: ").strip()
            try:
                if op == "1":
                    minimo = self._leer_int("Mínimo de stock: ")
                    items = self.service.reporte_stock_bajo(minimo=minimo)
                    self._listar(f"Libros con stock <= {minimo}", items)
                    self._pausa()
                elif op == "2":
                    reporte = self.service.reporte_libros_por_genero()
                    print("\n--- Libros por género ---")
                    if not reporte:
                        print("Sin libros cargados")
                    for genero, libros in reporte.items():
                        print(f"\n{genero}:")
                        for libro in libros:
                            print(f"  - {libro.titulo} ({libro.autor})")
                    self._pausa()
                elif op == "0":
                    return
                else:
                    print("Opción inválida")
            except (ValueError, TypeError) as exc:
                print(f"Error: {exc}")
                self._pausa()

    # ------------------------------ Menú principal ---------------------------
    def ejecutar(self) -> None:
        while True:
            print("\n=== Book Manager ===")
            print("1. Géneros")
            print("2. Editoriales")
            print("3. Monedas")
            print("4. Tipos de cotización")
            print("5. Libros")
            print("6. Precios")
            print("7. Stock")
            print("8. Cotizaciones")
            print("9. Reportes")
            print("0. Salir")

            opcion = input("Seleccionar opción: ").strip()
            if opcion == "1":
                self.menu_generos()
            elif opcion == "2":
                self.menu_editoriales()
            elif opcion == "3":
                self.menu_monedas()
            elif opcion == "4":
                self.menu_tipos_cotizacion()
            elif opcion == "5":
                self.menu_libros()
            elif opcion == "6":
                self.menu_precios()
            elif opcion == "7":
                self.menu_stock()
            elif opcion == "8":
                self.menu_cotizaciones()
            elif opcion == "9":
                self.menu_reportes()
            elif opcion == "0":
                print("Saliendo...")
                break
            else:
                print("Opción inválida")
