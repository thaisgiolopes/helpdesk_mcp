"""SQLite persistence for Helpdesk MCP."""

from __future__ import annotations

import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from seed import seed_database


PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_DB_PATH = PROJECT_ROOT / "data" / "helpdesk.db"
VALID_STATUSES = frozenset(
    {
        "aberto",
        "em_atendimento",
        "aguardando_cliente",
        "resolvido",
        "fechado",
    }
)


class ClienteNaoEncontradoError(LookupError):
    """Raised when a requested client ID does not exist."""


class ChamadoNaoEncontradoError(LookupError):
    """Raised when a requested ticket ID does not exist."""


def get_database_path() -> Path:
    """Return the configured database path, independent of the working directory."""
    configured_path = os.environ.get("HELPDESK_DB_PATH")
    if configured_path:
        return Path(configured_path).expanduser().resolve()
    return DEFAULT_DB_PATH


def connect(database_path: str | Path | None = None) -> sqlite3.Connection:
    """Open a connection and enforce SQLite foreign-key constraints."""
    path = Path(database_path) if database_path is not None else get_database_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def create_schema(connection: sqlite3.Connection) -> None:
    """Create missing tables without recreating or clearing existing tables."""
    status_sql = ", ".join(f"'{status}'" for status in sorted(VALID_STATUSES))
    connection.executescript(
        f"""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS chamados (
            id INTEGER PRIMARY KEY,
            cliente_id INTEGER NOT NULL,
            descricao TEXT NOT NULL,
            status TEXT NOT NULL CHECK (status IN ({status_sql})),
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (cliente_id) REFERENCES clientes (id)
        );
        """
    )


def initialize_database(database_path: str | Path | None = None) -> None:
    """Create missing schema and insert any missing demonstration records."""
    with connect(database_path) as connection:
        create_schema(connection)
        seed_database(connection)


def listar_chamados(status: str | None = None, database_path: str | Path | None = None) -> list[dict]:
    """Read tickets, newest first and with stable ID ordering for timestamp ties."""
    query = """
        SELECT id, cliente_id, descricao, status, created_at, updated_at
        FROM chamados
    """
    parameters: tuple[str, ...] = ()
    if status is not None:
        query += " WHERE status = ?"
        parameters = (status,)
    query += " ORDER BY created_at DESC, id ASC"

    with connect(database_path) as connection:
        rows = connection.execute(query, parameters).fetchall()
    return [dict(row) for row in rows]


def buscar_historico_cliente(
    cliente_id: int,
    database_path: str | Path | None = None,
) -> list[dict]:
    """Return a client's tickets, newest first, or raise if the client is unknown."""
    if type(cliente_id) is not int or cliente_id < 1:
        raise ValueError("cliente_id deve ser um inteiro positivo.")

    with connect(database_path) as connection:
        cliente = connection.execute(
            "SELECT 1 FROM clientes WHERE id = ?", (cliente_id,)
        ).fetchone()
        if cliente is None:
            raise ClienteNaoEncontradoError(
                f"Cliente não encontrado: {cliente_id}."
            )

        rows = connection.execute(
            """
            SELECT id, cliente_id, descricao, status, created_at, updated_at
            FROM chamados
            WHERE cliente_id = ?
            ORDER BY created_at DESC, id ASC
            """,
            (cliente_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def _utc_now() -> str:
    """Return the canonical UTC timestamp format used by the database."""
    return datetime.now(timezone.utc).replace(microsecond=0).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )


def atualizar_status(
    chamado_id: int,
    novo_status: str,
    database_path: str | Path | None = None,
) -> dict:
    """Update a ticket's current status atomically and return its current record."""
    if type(chamado_id) is not int or chamado_id < 1:
        raise ValueError("chamado_id deve ser um inteiro positivo.")
    if type(novo_status) is not str or novo_status not in VALID_STATUSES:
        allowed = ", ".join(sorted(VALID_STATUSES))
        raise ValueError(
            f"Status inválido: {novo_status!r}. Valores aceitos: {allowed}."
        )

    with connect(database_path) as connection:
        connection.execute("BEGIN IMMEDIATE")
        ticket = connection.execute(
            """
            SELECT id, cliente_id, descricao, status, created_at, updated_at
            FROM chamados
            WHERE id = ?
            """,
            (chamado_id,),
        ).fetchone()
        if ticket is None:
            raise ChamadoNaoEncontradoError(
                f"Chamado não encontrado: {chamado_id}."
            )

        if ticket["status"] == novo_status:
            return dict(ticket)

        connection.execute(
            "UPDATE chamados SET status = ?, updated_at = ? WHERE id = ?",
            (novo_status, _utc_now(), chamado_id),
        )
        updated_ticket = connection.execute(
            """
            SELECT id, cliente_id, descricao, status, created_at, updated_at
            FROM chamados
            WHERE id = ?
            """,
            (chamado_id,),
        ).fetchone()
        return dict(updated_ticket)
