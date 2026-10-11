# Book Manager - Sprint 2

## Objetivo

Consolidar las bases de manejo de bases de datos relacionales, normalización, conexión segura y carga inicial, migrando la persistencia en archivos del Sprint 1 a una base de datos PostgreSQL alojada en Supabase mediante SQLAlchemy, e incorporando consultas a APIs externas.

## Introducción y contexto

En la segunda entrega se amplía el alcance de la aplicación de consola (CLI) desarrollada en el Sprint 1: todos los datos que vivían en archivos CSV pasan a persistir en una base de datos relacional PostgreSQL (proyecto de [Supabase](https://supabase.com/)). Para ello se utiliza el ORM [SQLAlchemy](https://www.sqlalchemy.org/) junto con el driver `psycopg2`, definiendo tablas con sus tipos de datos y relaciones, un contexto de transacciones y una migración que genera las sentencias SQL de inserción a partir de los CSV originales. La conexión se realiza por el Session pooler de Supabase (puerto 5432, `sslmode=require`) y la URL se lee desde la variable de entorno `DATABASE_URL` del archivo `.env` (no versionado). Además, el sistema consulta una API externa de cotizaciones del dólar para registrar valores actualizados y ofrecer reportes de precios bimonetarios y su exportación a CSV.

## Configuración

1. Instalar las dependencias: `pip install -r requirements.txt`.
2. Copiar `.env.example` a `.env` y completar `DATABASE_URL` con la cadena del Session pooler de Supabase (PostgreSQL).
3. Ejecutar la aplicación: `python -m book_manager.main` (con `PYTHONPATH=src`).

