"""Conexion a la base de datos del sistema Book Manager (PostgreSQL/Supabase).

Define la clase ``ConexionDB``, encargada de crear el engine de
SQLAlchemy, administrar las sesiones y crear las tablas del esquema.
La configuracion se lee del archivo ``.env`` (dotenv).

La URL de conexion es obligatoria y debe apuntar a una base PostgreSQL.
"""
from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Optional
from urllib.parse import urlsplit

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

RUTA_RAIZ = Path(__file__).resolve().parents[3]
RUTA_ENV = RUTA_RAIZ / ".env"


class ConexionDB:
    """Conexion con la base de datos relacional PostgreSQL (SQLAlchemy)."""

    def __init__(self, database_url: Optional[str] = None) -> None:
        """Crea el engine de conexion.

        Args:
            database_url (Optional[str]): URL SQLAlchemy a utilizar. Si no se
                indica, se lee ``DATABASE_URL`` del archivo ``.env``.

        Raises:
            ValueError: Si no se define ninguna URL de conexion.
        """
        load_dotenv(RUTA_ENV)
        url = database_url if database_url is not None else os.environ.get("DATABASE_URL", "")
        url = url.strip()
        if not url:
            raise ValueError(
                "DATABASE_URL no está definida. Configurá el archivo .env con la URL "
                "de PostgreSQL/Supabase (Session pooler, puerto 5432, sslmode=require)."
            )
        self._url = url
        self.engine: Engine = create_engine(url, pool_pre_ping=True)
        self.SessionFactory = sessionmaker(
            bind=self.engine, expire_on_commit=False, autoflush=False
        )

    @property
    def url(self) -> str:
        """URL del motor de conexion (con la clave enmascarada)."""
        partes = urlsplit(self._url)
        host = partes.hostname or ""
        puerto = f":{partes.port}" if partes.port else ""
        base = partes.path.lstrip("/") or "(base)"
        return f"{partes.scheme}://{host}{puerto}/{base}"

    def crear_tablas(self) -> None:
        """Crea todas las tablas definidas en los modelos si no existen."""
        from book_manager.models.models import Base

        Base.metadata.create_all(self.engine)

    # ---------------- Context manager de transacciones ----------------
    @contextmanager
    def session_scope(self) -> Iterator[Session]:
        """Administra la transaccion de una sesion.

        Confirma los cambios al salir con normalidad, revierte la
        transaccion si se propaga una excepcion y cierra la sesion.

        Yields:
            Iterator[Session]: Sesion de SQLAlchemy activa.
        """
        sesion: Session = self.SessionFactory()
        try:
            yield sesion
            sesion.commit()
        except Exception:
            sesion.rollback()
            raise
        finally:
            sesion.close()
