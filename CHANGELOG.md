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

