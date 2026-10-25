[Ejercicio 05 - Sprint 3]
- Reporte Excel reportes/reporte_comparacion_precios.xlsx con Libro, Precio interno, Precio web, Diferencia y Fecha de extraccion.

[Ejercicio 04 - Sprint 3]
- ServicioComparacionPrecios compara cada precio interno con el precio web en su misma moneda (ARS o USD).
- Generacion de reportes/alertas_precios.csv en cada ejecucion con los libros que superan la diferencia ingresada.
- Si Cuspide tiene varias ediciones del libro se usa la de titulo exacto y, entre ellas, la mas barata.
- La fecha del reporte es la fecha de extraccion registrada por el scraper.

[Ejercicio 03 - Sprint 3]
- CuspideSpider busca solo los libros del catalogo, por titulo (maximo 10 resultados) con respaldo unico por ISBN.
- Filtro por titulo y autor en la pagina de resultados: solo se descargan las fichas candidatas y el autor se confirma en la ficha (libros homonimos).
- Extraccion de precio en pesos y en dolares, url de la imagen, formas de pago y descripcion detallada de cada ficha.
- ItemLoader (LibroCuspideLoader) con procesadores de limpieza y conversion de precio, y fecha de extraccion en cada item.
- Cadena de pipelines: ValidarLibroPipeline descarta fichas sin precio o repetidas y JsonLinesPipeline guarda reportes/cuspide_resultados.jl.
- Ejecucion del spider en un subproceso (runner.py) para no chocar con el reactor de Twisted en Colab.

[Ejercicio 02 - Sprint 3]
- Funcion cargar_datos_desde_sql que ejecuta los archivos migrations/sql/<tabla>.sql en una transaccion.
- Respeta el orden de las relaciones, omite la carga si la base ya tiene datos y reajusta las secuencias en PostgreSQL.

[Ejercicio 01 - Sprint 3]
- Rama Sprint_3 creada a partir de Sprint_2; estructura scraper/ (spiders, items, pipelines) y reportes/.
- requirements.txt con Scrapy, itemloaders, pandas y openpyxl.
- README.md actualizado con el objetivo y el contexto del Sprint 3.
- Exclusion de cuspide_resultados.jl (salida cruda del scraper) en .gitignore.

[Correcciones de observaciones - Sprint 2]
- Ej 01: se quito del repositorio el .env con credenciales (queda solo .env.example)
  y se restauro su exclusion en .gitignore.
- Ej 04: relaciones ORM bidireccionales con back_populates (editorial.libros,
  genero.libros, libro.precios, libro.stock, moneda.precios, tipo.cotizaciones).
- Ej 07: la URL de la API es obligatoria desde .env (sin valor por defecto en el
  codigo); CotizacionDolar guarda valor de compra y de venta (entidad, modelo ORM,
  migracion, CSV y SQL); se capturan los errores de red de la API sin cortar el programa.
- Ej 08: el listado bimonetario permite elegir el tipo de cotizacion e informa el
  tipo, la fecha y el valor aplicados; la demo usa las opciones 10, 11 y 12.
- Ej 06: la ejecucion del notebook muestra un listado y un alta/modificacion de
  cada uno de los 8 modelos.
- main() ya no devuelve el servicio (no imprime <LibreriaService at ...> en el notebook).
- Docstrings PEP 257 (Args/Returns/Raises) en todos los modulos.

[Ejercicio 08 - Sprint 2]
- Menu para obtener las cotizaciones por API desde la consola.
- Menu de precios bimonetarios en pesos y en la moneda seleccionada, con tipo de
  cotizacion elegible y cotizacion aplicada informada.
- Menu para exportar los precios a CSV en todos los tipos de moneda.

[Ejercicio 07 - Sprint 2]
- ServicioCotizacionDolar.obtener_cotizaciones para buscar, descargar y registrar
  cotizaciones (valor de compra y de venta), con URL obligatoria desde .env y
  manejo controlado de errores de red.
- Archivo .env.example con la URL de la API del dolar.

[Ejercicio 06 - Sprint 2]
- Repositorios reimplementados sobre SQLAlchemy conservando las interfaces CRUD.
- Servicios y main adaptados para operar unicamente contra la base de datos.

[Ejercicio 05 - Sprint 2]
- Migracion de los CSV del Sprint 1 a la base de datos con la funcion migrar_datos.
- Generacion de los archivos .sql con las sentencias de insercion en migrations/sql.

[Ejercicio 04 - Sprint 2]
- Modelos ORM de las ocho tablas con sus tipos de datos, claves primarias y foraneas.
- Relaciones entre libros, editoriales, generos, monedas y cotizaciones.

[Ejercicio 03 - Sprint 2]
- Context manager session_scope para transacciones (commit, rollback y cierre).

[Ejercicio 02 - Sprint 2]
- Clase ConexionDB con engine de SQLAlchemy, lectura del .env y PostgreSQL (Supabase).

[Ejercicio 01 - Sprint 2]
- Creacion de la estructura del Sprint 2 (database, models y migrations/sql).
- Actualizacion de requirements.txt con SQLAlchemy, psycopg2-binary, python-dotenv y requests.
- Actualizacion de README.md con el objetivo y el contexto del Sprint 2 (PostgreSQL/Supabase).
- Exclusion del archivo .env (credenciales) y del export de precios en .gitignore.

[Ejercicio 07]
- Creacion de main.py como punto de entrada del sistema.
- Carga automatica de datos CSV y modo no interactivo para validar el notebook con Ejecutar todo.

[Ejercicio 06]
- Implementacion de la interfaz de consola (CLI) con menus CRUD para las ocho entidades.
- Menu de reportes integrado a la consola.

[Ejercicio 05]
- Generacion de los archivos CSV de migracion en migrations/csv con 10 registros por entidad (libreria estandar csv).
- Implementacion de la importacion de datos desde CSV al servicio respetando el orden de las relaciones.

[Ejercicio 04]
- Implementacion de LibreriaService con la logica de negocio de cada operacion CRUD.
- Validacion de relaciones entre entidades (libro-editorial/genero, precio-libro/moneda, stock-libro, cotizacion-tipo).
- Reportes: stock bajo, libros por genero y cotizacion del dia.

[Ejercicio 03]
- Definicion de las interfaces de repositorio (IRepositorio, IRepositorioStock, IRepositorioCotizacionDolar) con abc y Generic.
- Implementacion de los repositorios en memoria con el CRUD completo de cada entidad.

[Ejercicio 02]
- Definicion de las ocho clases entidad (Libro, Genero, Editorial, Moneda, TipoCotizacion, Precio, Stock, CotizacionDolar).
- Aplicacion de encapsulamiento con atributos privados, propiedades y validaciones.
- Uso de dataclasses, type hints y herencia desde una clase base comun.

[Ejercicio 01]
- Inicializacion y configuracion de la herramienta de versionado en la rama Sprint_1.
- Creacion de la estructura de directorios del proyecto (entities, repositories, services, preload_data, migrations/csv, ui).
- Creacion de README.md con el sprint, el objetivo y la introduccion/contexto.
- Creacion de requirements.txt (solo libreria estandar).

