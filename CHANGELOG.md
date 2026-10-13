[Ejercicio 07 - Sprint 2]
- ServicioCotizacionDolar.obtener_cotizaciones para buscar, descargar y registrar cotizaciones.
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

