from __future__ import annotations

import asyncio
import sqlite3

import pytest
from fastmcp import Client

from server.database import (
    ClienteNaoEncontradoError,
    buscar_historico_cliente,
    connect,
    create_schema,
    initialize_database,
)
from server.server import mcp


EXPECTED_FIELDS = {
    "id",
    "cliente_id",
    "descricao",
    "status",
    "created_at",
    "updated_at",
}


def test_database_history_filters_by_client_and_orders_deterministically(tmp_path):
    database_path = tmp_path / "helpdesk.db"
    with connect(database_path) as connection:
        create_schema(connection)
        connection.executemany(
            "INSERT INTO clientes (id, nome, email) VALUES (?, ?, ?)",
            [
                (1, "Cliente 1", "c1@example.test"),
                (2, "Cliente 2", "c2@example.test"),
            ],
        )
        connection.executemany(
            """INSERT INTO chamados
               (id, cliente_id, descricao, status, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            [
                (10, 1, "empate", "aberto", "2026-01-02T00:00:00Z", "2026-01-02T00:00:00Z"),
                (3, 1, "empate", "resolvido", "2026-01-02T00:00:00Z", "2026-01-02T00:00:00Z"),
                (8, 1, "mais recente", "fechado", "2026-01-03T00:00:00Z", "2026-01-03T00:00:00Z"),
                (4, 2, "outro cliente", "aberto", "2026-01-04T00:00:00Z", "2026-01-04T00:00:00Z"),
            ],
        )

    tickets = buscar_historico_cliente(1, database_path)

    assert [ticket["id"] for ticket in tickets] == [8, 3, 10]
    assert all(ticket["cliente_id"] == 1 for ticket in tickets)
    assert all(set(ticket) == EXPECTED_FIELDS for ticket in tickets)


def test_database_history_distinguishes_empty_history_from_unknown_client(tmp_path):
    database_path = tmp_path / "helpdesk.db"
    with connect(database_path) as connection:
        create_schema(connection)
        connection.execute(
            "INSERT INTO clientes (id, nome, email) VALUES (1, 'Cliente 1', 'c1@example.test')"
        )

    assert buscar_historico_cliente(1, database_path) == []
    with pytest.raises(ClienteNaoEncontradoError, match="Cliente não encontrado: 2"):
        buscar_historico_cliente(2, database_path)


@pytest.mark.parametrize("cliente_id", [None, True, False, 0, -1, 1.5, "1"])
def test_database_history_rejects_invalid_client_ids(tmp_path, cliente_id):
    with pytest.raises(ValueError, match="inteiro positivo"):
        buscar_historico_cliente(cliente_id, tmp_path / "helpdesk.db")


def test_database_history_does_not_modify_records(tmp_path):
    database_path = tmp_path / "helpdesk.db"
    initialize_database(database_path)
    with connect(database_path) as connection:
        before_clients = connection.execute(
            "SELECT id, nome, email FROM clientes ORDER BY id"
        ).fetchall()
        before_tickets = connection.execute(
            "SELECT id, cliente_id, descricao, status, created_at, updated_at "
            "FROM chamados ORDER BY id"
        ).fetchall()

    buscar_historico_cliente(1, database_path)

    with connect(database_path) as connection:
        after_clients = connection.execute(
            "SELECT id, nome, email FROM clientes ORDER BY id"
        ).fetchall()
        after_tickets = connection.execute(
            "SELECT id, cliente_id, descricao, status, created_at, updated_at "
            "FROM chamados ORDER BY id"
        ).fetchall()
    assert [tuple(row) for row in before_clients] == [tuple(row) for row in after_clients]
    assert [tuple(row) for row in before_tickets] == [tuple(row) for row in after_tickets]


def test_database_history_propagates_sqlite_errors(tmp_path):
    path_that_is_a_directory = tmp_path / "database-directory"
    path_that_is_a_directory.mkdir()
    with pytest.raises(sqlite3.OperationalError):
        buscar_historico_cliente(1, path_that_is_a_directory)


def test_history_tool_contract_through_mcp_client(tmp_path, monkeypatch):
    database_path = tmp_path / "helpdesk.db"
    initialize_database(database_path)
    with connect(database_path) as connection:
        connection.execute(
            "INSERT INTO clientes (id, nome, email) VALUES (50, 'Sem chamados', 'c50@example.test')"
        )
    monkeypatch.setenv("HELPDESK_DB_PATH", str(database_path))

    async def run_checks():
        async with Client(mcp) as client:
            tools = {tool.name for tool in await client.list_tools()}
            assert {"listar_chamados", "buscar_historico_cliente"} <= tools

            result = await client.call_tool(
                "buscar_historico_cliente", {"cliente_id": 1}, raise_on_error=False
            )
            assert not result.is_error
            assert all(ticket["cliente_id"] == 1 for ticket in result.data)
            assert [ticket["id"] for ticket in result.data] == [1001, 1003]
            assert all(set(ticket) == EXPECTED_FIELDS for ticket in result.data)

            empty = await client.call_tool(
                "buscar_historico_cliente", {"cliente_id": 50}, raise_on_error=False
            )
            assert not empty.is_error
            assert empty.data == []

            missing = await client.call_tool(
                "buscar_historico_cliente", {"cliente_id": 9999}, raise_on_error=False
            )
            assert missing.is_error
            assert "Cliente não encontrado" in missing.content[0].text

            invalid_inputs = [
                {},
                {"cliente_id": None},
                {"cliente_id": True},
                {"cliente_id": "1"},
                {"cliente_id": 1.5},
                {"cliente_id": 0},
                {"cliente_id": -1},
            ]
            for arguments in invalid_inputs:
                invalid = await client.call_tool(
                    "buscar_historico_cliente", arguments, raise_on_error=False
                )
                assert invalid.is_error, arguments

    asyncio.run(run_checks())
