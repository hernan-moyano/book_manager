"""Auditoría persistente de las operaciones del sistema (Sprint 3).

Usa el modelo ORM :class:`~book_manager.models.models.Auditoria` (tabla
``auditoria`` con acción, fecha y detalles) y define el decorador
:func:`auditar` que registra cada operación, la función
:func:`habilitar_auditoria` que decora los métodos públicos de alta,
modificación, baja, reportes y exportación de la fachada ``LibreriaService``,
:func:`registrar_auditoria` para operaciones que no pasan por la fachada
(scraping y reporte Excel) y :func:`historial_auditoria` para consultar el
registro.
"""
from __future__ import annotations

from datetime import datetime
from functools import wraps
from typing import Any, Callable, List

from sqlalchemy import select

from book_manager.models.models import Auditoria, Base

PREFIJOS_AUDITADOS = ("alta_", "modificar_", "eliminar_", "reporte_", "exportar_")


def _describir(valor: Any) -> str:
    """Describe un valor para los detalles usando el ``__str__`` de las entidades.

    Args:
        valor (Any): Argumento o resultado de la operación auditada.

    Returns:
        str: Representación legible (las colecciones se describen elemento a elemento).
    """
    if isinstance(valor, (list, tuple)):
        return "[" + ", ".join(_describir(elemento) for elemento in valor) + "]"
    if isinstance(valor, dict):
        return "{" + ", ".join(f"{k}: {_describir(v)}" for k, v in valor.items()) + "}"
    if isinstance(valor, (str, int, float, bool, type(None))):
        return repr(valor)
    return str(valor)


def registrar_auditoria(conexion: Any, accion: str, detalles: str) -> None:
    """Inserta un registro en la tabla ``auditoria`` con la fecha actual.

    Args:
        conexion (Any): Conexión con la base de datos (``session_scope``).
        accion (str): Nombre de la acción a registrar.
        detalles (str): Descripción de la operación realizada.
    """
    with conexion.session_scope() as sesion:
        sesion.add(Auditoria(accion=accion, fecha=datetime.now(), detalles=detalles))


def auditar(accion: str, conexion: Any) -> Callable:
    """Decorador que registra en la base la operación ejecutada.

    Inserta una fila en la tabla ``auditoria`` con la acción, la fecha actual
    y los argumentos/resultado de la llamada, solo si la operación se
    completó sin excepciones.

    Args:
        accion (str): Nombre de la acción a registrar.
        conexion (Any): Conexión con la base de datos (``session_scope``).

    Returns:
        Callable: El decorador que envuelve la función original.
    """

    def decorador(funcion: Callable) -> Callable:
        @wraps(funcion)
        def envoltura(*args: Any, **kwargs: Any) -> Any:
            resultado = funcion(*args, **kwargs)
            registrar_auditoria(
                conexion,
                accion,
                f"args={_describir(args)}; kwargs={_describir(kwargs)}; "
                f"resultado={_describir(resultado)}",
            )
            return resultado

        return envoltura

    return decorador


def habilitar_auditoria(service: Any, conexion: Any) -> None:
    """Decora las operaciones públicas de la fachada con :func:`auditar`.

    Crea la tabla ``auditoria`` si no existe y envuelve cada método de la
    fachada cuyo nombre empiece con alguno de ``PREFIJOS_AUDITADOS`` (alta,
    modificación, baja, reportes y exportación).

    Args:
        service (Any): Fachada ``LibreriaService`` a auditar.
        conexion (Any): Conexión con la base de datos.
    """
    Base.metadata.create_all(conexion.engine, tables=[Auditoria.__table__])
    for nombre in dir(service):
        if nombre.startswith(PREFIJOS_AUDITADOS):
            metodo = getattr(service, nombre)
            if callable(metodo) and not getattr(metodo, "_auditado", False):
                decorado = auditar(nombre, conexion)(metodo)
                decorado._auditado = True  # type: ignore[attr-defined]
                setattr(service, nombre, decorado)


def historial_auditoria(conexion: Any) -> List[Auditoria]:
    """Devuelve el historial de auditorías ordenado de la más reciente a la más antigua.

    Args:
        conexion (Any): Conexión con la base de datos.

    Returns:
        List[Auditoria]: Registros de auditoría ordenados por fecha descendente.
    """
    with conexion.session_scope() as sesion:
        return list(
            sesion.execute(
                select(Auditoria).order_by(Auditoria.fecha.desc(), Auditoria.id.desc())
            ).scalars()
        )
