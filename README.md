# Book Manager - Sprint 2

## Objetivo

Consolidar las bases de manejo de bases de datos relacionales, normalización, conexión segura y carga inicial, migrando la persistencia en archivos del Sprint 1 a una base de datos PostgreSQL alojada en Supabase mediante SQLAlchemy, e incorporando consultas a APIs externas.

## Introducción y contexto

En la segunda entrega se amplía el alcance de la aplicación de consola (CLI) desarrollada en el Sprint 1: todos los datos que vivían en archivos CSV pasan a persistir en una base de datos relacional PostgreSQL (proyecto de [Supabase](https://supabase.com/)). Para ello se utiliza el ORM [SQLAlchemy](https://www.sqlalchemy.org/) junto con el driver `psycopg2`, definiendo tablas con sus tipos de datos y relaciones, un contexto de transacciones y una migración que genera las sentencias SQL de inserción a partir de los CSV originales. La conexión se realiza por el Session pooler de Supabase (puerto 5432, `sslmode=require`) y la URL se lee desde la variable de entorno `DATABASE_URL` del archivo `.env` (no versionado). Además, el sistema consulta una API externa de cotizaciones del dólar para registrar valores actualizados y ofrecer reportes de precios bimonetarios y su exportación a CSV.

## Configuración

1. Instalar las dependencias: `pip install -r requirements.txt`.
2. Copiar `.env.example` a `.env` y completar `DATABASE_URL` con la cadena del Session pooler de Supabase (PostgreSQL) y `API_URL` con la URL de la API de cotizaciones del dólar. **El `.env` no se versiona** (está en `.gitignore`); solo se publica `.env.example`.
3. Ejecutar la aplicación: `python -m book_manager.main` (con `PYTHONPATH=src`).

## Decisiones de diseño relevantes

- **Relaciones bidireccionales**: los modelos ORM declaran `back_populates`, de modo que se puede navegar de una editorial a sus libros (`editorial.libros`), de un libro a sus precios (`libro.precios`) y su stock (`libro.stock`), de una moneda a sus precios y de un tipo de cotización a su histórico (`tipo.cotizaciones`).
- **Cotizaciones compra/venta**: cada registro de `CotizacionDolar` conserva los dos valores que informa la API (`valor_compra` y `valor_venta`); el valor de venta se usa como referencia de conversión.
- **Configuración obligatoria**: la URL de la API no tiene valor por defecto en el código: si `API_URL` falta en el `.env`, se informa el error sin usar un valor hardcodeado. Los errores de red (sin conexión, timeout) se capturan y muestran sin cortar el programa.
- **Precios bimonetarios**: el listado permite elegir el tipo de cotización a aplicar e informa en el encabezado el tipo, la fecha y el valor usados en la conversión.

