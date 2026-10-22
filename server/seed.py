"""Stable fictitious records used to demonstrate the first project phase."""

from __future__ import annotations

import sqlite3


CLIENTES = (
    (1, "Ana Souza", "ana.souza@example.test"),
    (2, "Bruno Lima", "bruno.lima@example.test"),
    (3, "Carla Nunes", "carla.nunes@example.test"),
)

CHAMADOS = (
    (1001, 1, "Notebook não conecta ao Wi-Fi", "aberto", "2026-10-20T13:00:00Z", "2026-10-20T13:00:00Z"),
    (1002, 2, "Acesso ao sistema bloqueado", "em_atendimento", "2026-10-19T15:30:00Z", "2026-10-20T09:15:00Z"),
    (1003, 1, "Solicitação de instalação de software", "aguardando_cliente", "2026-10-18T11:45:00Z", "2026-10-19T10:00:00Z"),
    (1004, 3, "Impressora com falha na fila", "resolvido", "2026-10-17T14:20:00Z", "2026-10-18T16:40:00Z"),
    (1005, 2, "Dúvida sobre acesso remoto", "fechado", "2026-10-16T08:10:00Z", "2026-10-17T12:25:00Z"),
    (1006, 3, "Monitor sem sinal de vídeo", "aberto", "2026-10-15T09:00:00Z", "2026-10-15T09:00:00Z"),
)


def seed_database(connection: sqlite3.Connection) -> None:
    """Seed once; later server starts preserve even deleted or edited seed rows."""
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS app_metadata (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
        """
    )
    seeded = connection.execute(
        "SELECT 1 FROM app_metadata WHERE key = 'initial_demo_data_v1'"
    ).fetchone()
    if seeded:
        return

    connection.executemany(
        "INSERT INTO clientes (id, nome, email) VALUES (?, ?, ?) ON CONFLICT DO NOTHING",
        CLIENTES,
    )
    connection.executemany(
        """
        INSERT INTO chamados (id, cliente_id, descricao, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT DO NOTHING
        """,
        CHAMADOS,
    )
    connection.execute(
        "INSERT INTO app_metadata (key, value) VALUES ('initial_demo_data_v1', 'complete')"
    )
