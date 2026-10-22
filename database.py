"""SQLite persistence for Helpdesk MCP."""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path

from seed import seed_database


PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_DB_PATH = PROJECT_ROOT / "data" / "helpdesk.db"


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
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS chamados (
            id INTEGER PRIMARY KEY,
            cliente_id INTEGER NOT NULL,
            descricao TEXT NOT NULL,
            status TEXT NOT NULL CHECK (
                status IN (
                    'aberto', 'em_atendimento', 'aguardando_cliente',
                    'resolvido', 'fechado'
                )
            ),
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
