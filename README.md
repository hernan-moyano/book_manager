# Book Manager - Sprint 3

## Objetivo

Descargar y obtener datos de la web para trabajar con ellos: consultar los precios de un competidor con venta online ([Cúspide](https://www.cuspide.com/)) para los libros del catálogo propio, compararlos con los precios internos, generar alertas y reportes, y auditar todas las operaciones del sistema.

## Introducción y contexto

La tercera entrega parte del último push del Sprint 2 (persistencia en PostgreSQL/Supabase con SQLAlchemy y consulta de la API del dólar) y le agrega web scraping con [Scrapy](https://scrapy.org/). El spider `CuspideSpider` busca en Cúspide **solo los libros del catálogo interno**, tomando como máximo los 10 primeros resultados de cada búsqueda por título, y extrae el precio, la URL de la imagen, las formas de pago y la descripción detallada usando `ItemLoader` y un pipeline que guarda los resultados en JSON Lines. Con esos datos el sistema compara el precio interno con el precio web, genera un CSV de alertas según la diferencia porcentual que ingresa el usuario y un reporte Excel con la comparación. Además, un decorador registra cada operación en la tabla `auditoria` (acción, fecha y detalles), que puede consultarse desde el menú.

## Configuración

1. Instalar las dependencias: `pip install -r requirements.txt`.
2. Copiar `.env.example` a `.env` y completar `DATABASE_URL` con la cadena del Session pooler de Supabase (PostgreSQL) y `API_URL` con la URL de la API de cotizaciones del dólar. **El `.env` no se versiona** (está en `.gitignore`); solo se publica `.env.example`.
3. Ejecutar la aplicación: `python -m book_manager.main` (con `PYTHONPATH=src`).

## Opciones del Sprint 3

- **13. Ejecutar scraping**: pide la diferencia porcentual de alerta, consulta Cúspide y genera `reportes/alertas_precios.csv`.
- **14. Generar reporte**: genera `reportes/reporte_comparacion_precios.xlsx` con Libro, Precio interno, Precio web, Diferencia y Fecha de extracción.
- **15. Ver historial de auditoría**: lista las operaciones registradas, de la más reciente a la más antigua.

## Decisiones de diseño relevantes

- **Scraping en subproceso**: el spider se ejecuta con `scraper/runner.py` en un proceso de Python aparte, con su propio reactor de Twisted, para que funcione igual en Colab/Jupyter, en consola y en Windows.
- **Búsqueda acotada al catálogo**: cada libro se busca por título y, de los 10 primeros resultados, solo se descargan las fichas cuyo título (80 % de las palabras) y autor coinciden con el catálogo, ya que en Cúspide hay libros homónimos de distintos autores. El autor se vuelve a confirmar en la ficha. Si ninguna ficha coincide, se hace una única búsqueda de respaldo por el ISBN normalizado.
- **Pipelines en cadena**: `ValidarLibroPipeline` descarta las fichas sin precio o repetidas y `JsonLinesPipeline` guarda las válidas; cada ítem registra su fecha de extracción, que es la que muestra el reporte.
- **Precio web del competidor**: si Cúspide tiene varias ediciones del mismo libro, se compara contra la de título exacto y, entre ellas, la más barata.
- **Auditoría por decorador**: `habilitar_auditoria` envuelve con `auditar` las operaciones de alta, modificación, baja, reportes y exportación de `LibreriaService`; el scraping y el reporte Excel se registran desde la consola. Solo se audita la operación si terminó sin errores.
- **Carga desde SQL**: `cargar_datos_desde_sql` ejecuta los archivos `.sql` generados en la migración del Sprint 2, en una única transacción.
- **Relaciones bidireccionales y cotizaciones compra/venta** (Sprint 2): se mantienen los `back_populates` de los modelos y los dos valores de la API del dólar.
