"""Interfaz de consola (CLI) del sistema Book Manager.

Cada menú opera directamente sobre los servicios de la librería,
permitiendo listar, dar de alta, modificar y borrar cada entidad
con validación robusta y manejo de errores ante datos mal ingresados.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path
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
from book_manager.scraper.runner import ejecutar_scraping
from book_manager.services.auditoria import historial_auditoria, registrar_auditoria
from book_manager.services.comparacion import ServicioComparacionPrecios
from book_manager.services.services import LibreriaService, ServicioCotizacionDolar

RUTA_REPORTES = Path(__file__).resolve().parent.parent / "reportes"


class ConsolaLibreria:
    """Menús de consola para operar el CRUD de cada entidad del sistema."""

    def __init__(self, service: LibreriaService) -> None:
        """Inyecta el servicio de la librería que operan los menús.

        Args:
            service (LibreriaService): Servicio orquestador del dominio.
        """
        self.service = service

    # --------------------------- Utilidades de E/S ---------------------------
    def _leer_int(self, texto: str) -> int:
        """Lee un entero por consola reintentando de forma segura ante errores.

        Args:
            texto (str): Mensaje a mostrar al usuario.

        Returns:
            int: El entero ingresado.
        """
        while True:
            valor = input(texto).strip()
            try:
                return int(valor)
            except ValueError:
                print("Entrada inválida: debe ingresar un número entero.")

    def _leer_float(self, texto: str) -> float:
        """Lee un flotante por consola reintentando de forma segura ante errores.

        Args:
            texto (str): Mensaje a mostrar al usuario.

        Returns:
            float: El número ingresado.
        """
        while True:
            valor = input(texto).strip()
            try:
                return float(valor)
            except ValueError:
                print("Entrada inválida: debe ingresar un número decimal válido.")

    def _leer_fecha(self, texto: str) -> date:
        """Lee una fecha en formato YYYY-MM-DD reintentando de forma segura.

        Args:
            texto (str): Mensaje a mostrar al usuario.

        Returns:
            date: La fecha ingresada.
        """
        while True:
            valor = input(texto).strip()
            try:
                return date.fromisoformat(valor)
            except ValueError:
                print("Formato de fecha inválido. Ingrese una fecha válida con formato AAAA-MM-DD.")

    def _pausa(self) -> None:
        """Detiene la salida hasta que el usuario presione Enter."""
        input("\nEnter para continuar...")

    def _listar(self, nombre: str, items: List[object]) -> None:
        """Imprime un listado con título, o un aviso si está vacío.

        Args:
            nombre (str): Título del listado.
            items (List[object]): Elementos a imprimir (uno por línea).
        """
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
        """Ejecuta el ciclo del menú CRUD genérico de una entidad.

        Captura los errores de validación (``ValueError``/``TypeError``) de
        las operaciones para que un dato mal ingresado no corte el programa.

        Args:
            titulo (str): Nombre de la entidad mostrado en el menú.
            crear_cb (Callable[[], object]): Operación de alta.
            actualizar_cb (Callable[[], object]): Operación de modificación.
            eliminar_cb (Callable[[], object]): Operación de borrado.
            listar_cb (Callable[[], List[object]]): Operación de listado.
        """
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
        """Menú CRUD de géneros literarios."""
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
        """Menú CRUD de editoriales."""
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
        """Menú CRUD de monedas."""
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
        """Menú CRUD de tipos de cotización."""
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
        """Arma un libro a partir de los datos ingresados por el usuario.

        Args:
            id_existente (int | None): ID a reutilizar en una modificación;
                si es None se solicita por consola.

        Returns:
            Libro: El libro construido con su editorial y género por objeto.

        Raises:
            ValueError: Si la editorial o el género indicados no existen.
        """
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
        """Menú CRUD de libros."""
        self._menu_crud_basico(
            "Libros",
            lambda: self.service.alta_libro(self._construir_libro_desde_input()),
            lambda: self.service.modificar_libro(self._construir_libro_desde_input()),
            lambda: self.service.eliminar_libro(self._leer_int("ID: ")),
            self.service.listar_libros,
        )

    def _construir_precio_desde_input(self, id_existente: int | None = None) -> Precio:
        """Arma un precio a partir de los datos ingresados por el usuario.

        Args:
            id_existente (int | None): ID a reutilizar en una modificación;
                si es None se solicita por consola.

        Returns:
            Precio: El precio construido con su libro y moneda por objeto.

        Raises:
            ValueError: Si el libro o la moneda indicados no existen.
        """
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
        """Menú CRUD de precios."""
        self._menu_crud_basico(
            "Precios",
            lambda: self.service.alta_precio(self._construir_precio_desde_input()),
            lambda: self.service.modificar_precio(self._construir_precio_desde_input()),
            lambda: self.service.eliminar_precio(self._leer_int("ID: ")),
            self.service.listar_precios,
        )

    def _construir_stock_desde_input(self) -> Stock:
        """Arma un registro de stock a partir de los datos ingresados.

        Returns:
            Stock: El stock construido con su libro por objeto.

        Raises:
            ValueError: Si el libro indicado no existe.
        """
        libro_id = self._leer_int("Libro ID: ")
        libro = self.service.libro_service.obtener_libro(libro_id)
        if libro is None:
            raise ValueError(f"No existe el libro con ID {libro_id}")
        cantidad = self._leer_int("Cantidad: ")
        return Stock(libro=libro, cantidad=cantidad)

    def menu_stock(self) -> None:
        """Menú CRUD de stock."""
        self._menu_crud_basico(
            "Stock",
            lambda: self.service.alta_stock(self._construir_stock_desde_input()),
            lambda: self.service.modificar_stock(self._construir_stock_desde_input()),
            lambda: self.service.eliminar_stock(self._leer_int("Libro ID: ")),
            self.service.listar_stock,
        )

    def _construir_cotizacion_desde_input(self) -> CotizacionDolar:
        """Arma una cotización a partir de los datos ingresados por el usuario.

        Returns:
            CotizacionDolar: La cotización construida y validada.

        Raises:
            ValueError: Si el tipo de cotización indicado no existe.
        """
        tipo_id = self._leer_int("Tipo ID: ")
        tipo = self.service.tipo_cotizacion_service.obtener_tipo_cotizacion(tipo_id)
        if tipo is None:
            raise ValueError(f"No existe el tipo de cotización con ID {tipo_id}")
        fecha = self._leer_fecha("Fecha (YYYY-MM-DD): ")
        valor_compra = self._leer_float("Valor de compra: ")
        valor_venta = self._leer_float("Valor de venta: ")
        return CotizacionDolar(
            tipo=tipo,
            fecha=fecha,
            valor_compra=valor_compra,
            valor_venta=valor_venta,
        )

    def menu_cotizaciones(self) -> None:
        """Menú CRUD de cotizaciones del dólar."""
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
        """Menú de reportes: stock bajo y libros agrupados por género."""
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

    # --------------------- Menús de cotizaciones y precios -------------------
    def menu_cotizaciones_api(self) -> None:
        """Descarga las cotizaciones del dólar desde la API y las registra.

        Captura los errores de configuración, red y formato de la API para
        que un fallo externo no interrumpa la ejecución del programa.
        """
        try:
            cotizaciones = ServicioCotizacionDolar(self.service).obtener_cotizaciones()
        except ValueError as exc:
            print(f"Error al obtener las cotizaciones: {exc}")
            self._pausa()
            return
        self._listar("Cotizaciones descargadas", cotizaciones)
        self._pausa()

    def _elegir_tipo_cotizacion(self) -> int | None:
        """Muestra los tipos de cotización disponibles y deja elegir uno.

        Returns:
            int | None: El ID del tipo elegido, o None si se presiona Enter
                para usar el tipo 'Oficial'.

        Raises:
            ValueError: Si el ID elegido no corresponde a un tipo existente.
        """
        tipos = self.service.listar_tipos_cotizacion()
        print("\nTipos de cotización disponibles:")
        for tipo in tipos:
            print(f"  [{tipo.id}] {tipo.nombre}")
        entrada = input("Tipo de cotización a aplicar (Enter = Oficial): ").strip()
        if not entrada:
            return None
        tipo_id = int(entrada)
        if self.service.tipo_cotizacion_service.obtener_tipo_cotizacion(tipo_id) is None:
            raise ValueError(f"No existe el tipo de cotización con ID {tipo_id}")
        return tipo_id

    def menu_precios_bimonetarios(self) -> None:
        """Muestra los precios de los libros en pesos y en la moneda elegida.

        Permite elegir el tipo de cotización usado en la conversión e informa
        en el encabezado qué tipo, fecha y valor se aplicaron.
        """
        try:
            moneda = input("Código de moneda (ej: USD): ").strip()
            tipo_id = self._elegir_tipo_cotizacion()
            filas = self.service.listar_precios_bimonetarios(moneda, tipo_id)
        except (ValueError, TypeError) as exc:
            print(f"Error: {exc}")
            self._pausa()
            return

        cot_tipo = filas[0]["cotizacion_tipo"] if filas else None
        cot_fecha = filas[0]["cotizacion_fecha"] if filas else None
        cot_valor = filas[0]["cotizacion_valor"] if filas else None
        print("\n--- Precios bimonetarios (ARS / otra moneda) ---")
        if cot_tipo is not None:
            print(
                f"Cotización aplicada: {cot_tipo} del {cot_fecha} "
                f"(venta ${cot_valor:.2f})"
            )
        else:
            print("Cotización aplicada: ninguna disponible (sin conversión)")
        for fila in filas:
            libro = fila["libro"]
            monto_ars = fila["monto_ars"]
            monto_moneda = fila["monto_moneda"]
            print(
                f"[{libro.id}] {libro.titulo} | "
                f"ARS {monto_ars if monto_ars is not None else '-'} | "
                f"{fila['moneda']} {monto_moneda if monto_moneda is not None else '-'}"
            )
        self._pausa()

    def menu_exportar_precios(self) -> None:
        """Exporta la lista de precios de todos los tipos de moneda a CSV."""
        ruta = input("Ruta del archivo CSV (Enter para la predeterminada): ").strip()
        destino = self.service.exportar_precios_csv(ruta or None)
        print(f"Precios exportados a: {destino}")
        self._pausa()

    # ---------------------- Menús del Sprint 3 (scraping) --------------------
    def menu_ejecutar_scraping(self) -> None:
        """Ejecuta el scraper de Cúspide y genera el CSV de alertas.

        Solicita la diferencia porcentual de alerta, busca los libros del
        catálogo por título y autor (con respaldo por ISBN), compara los precios
        internos con los obtenidos y guarda el archivo de alertas. El spider
        corre en un subproceso (:func:`ejecutar_scraping`) para no chocar con
        el reactor de Twisted del entorno (Colab/Jupyter o consola).
        """
        porcentaje = self._leer_float("Diferencia porcentual para alertar: ")
        salida = RUTA_REPORTES / "cuspide_resultados.jl"
        if salida.exists():
            salida.unlink()

        libros = [
            {"titulo": libro.titulo, "autor": libro.autor, "isbn": libro.isbn}
            for libro in self.service.listar_libros()
        ]
        if not libros:
            print("No hay libros cargados para consultar en Cúspide.")
            self._pausa()
            return
        print(f"Se buscarán {len(libros)} libros por título y autor, con ISBN como respaldo.")

        codigo = ejecutar_scraping(libros, salida)
        if codigo != 0 or not salida.exists():
            print(f"El scraping no generó resultados (código de salida {codigo}).")
            self._pausa()
            return

        comparador = ServicioComparacionPrecios(self.service, RUTA_REPORTES)
        resultados = comparador.leer_resultados(salida)
        self._comparacion_sprint3 = comparador.comparar(resultados, porcentaje)
        ruta_alertas = comparador.guardar_alertas_csv(self._comparacion_sprint3)
        alertas = sum(1 for fila in self._comparacion_sprint3 if fila["Alerta"])
        print(
            f"Libros encontrados: {len(self._comparacion_sprint3)} | "
            f"Alertas (>= {porcentaje}%): {alertas}"
        )
        print(f"Alertas generadas en: {ruta_alertas}")
        self._auditar(
            "ejecutar_scraping",
            f"libros={len(libros)}; encontrados={len(resultados)}; "
            f"porcentaje_alerta={porcentaje}; alertas={alertas}; archivo={ruta_alertas}",
        )
        self._pausa()

    def menu_generar_reporte_sprint3(self) -> None:
        """Genera el reporte Excel con la comparación de precios del scraping."""
        filas = getattr(self, "_comparacion_sprint3", [])
        if filas:
            ruta = ServicioComparacionPrecios(self.service, RUTA_REPORTES).generar_excel(filas)
            print(f"Reporte generado en: {ruta}")
            self._auditar("generar_reporte", f"filas={len(filas)}; archivo={ruta}")
        else:
            print("Ejecute primero el scraping para obtener resultados.")
        self._pausa()

    def menu_historial_auditoria(self) -> None:
        """Muestra el historial de operaciones auditadas del sistema."""
        conexion = self.service.conexion
        if conexion is None:
            print("La auditoría no está disponible: el servicio no tiene conexión.")
            self._pausa()
            return
        self._listar("Historial de auditoría", historial_auditoria(conexion))
        self._pausa()

    def _auditar(self, accion: str, detalles: str) -> None:
        """Registra en la auditoría una operación que no pasa por la fachada.

        Args:
            accion (str): Nombre de la acción a registrar.
            detalles (str): Descripción de la operación realizada.
        """
        if self.service.conexion is not None:
            registrar_auditoria(self.service.conexion, accion, detalles)

    # ------------------------------ Menú principal ---------------------------
    def ejecutar(self) -> None:
        """Ejecuta el ciclo del menú principal hasta que el usuario salga."""
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
            print("10. Obtener cotizaciones por API")
            print("11. Precios bimonetarios")
            print("12. Exportar precios a CSV")
            print("13. Ejecutar scraping")
            print("14. Generar reporte")
            print("15. Ver historial de auditoría")
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
            elif opcion == "10":
                self.menu_cotizaciones_api()
            elif opcion == "11":
                self.menu_precios_bimonetarios()
            elif opcion == "12":
                self.menu_exportar_precios()
            elif opcion == "13":
                self.menu_ejecutar_scraping()
            elif opcion == "14":
                self.menu_generar_reporte_sprint3()
            elif opcion == "15":
                self.menu_historial_auditoria()
            elif opcion == "0":
                print("Saliendo...")
                break
            else:
                print("Opción inválida")
