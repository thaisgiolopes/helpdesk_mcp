from __future__ import annotations

import sqlite3

import pytest

from database import connect, create_schema, initialize_database, listar_chamados
from seed import CHAMADOS


EXPECTED_FIELDS = {
    "id",
    "cliente_id",
    "descricao",
    "status",
    "created_at",
    "updated_at",
}


def test_initialize_creates_schema_and_stable_fictional_records(tmp_path):
    database_path = tmp_path / "nested" / "helpdesk.db"
    initialize_database(database_path)

    first_listing = listar_chamados(database_path=database_path)
    assert len(first_listing) == len(CHAMADOS)
    assert {"aberto", "em_atendimento", "aguardando_cliente", "resolvido", "fechado"} <= {
        ticket["status"] for ticket in first_listing
    }
    assert all(set(ticket) == EXPECTED_FIELDS for ticket in first_listing)
    assert len({ticket["cliente_id"] for ticket in first_listing}) > 1
    assert database_path.exists()


def test_initialize_is_idempotent_and_preserves_edits_and_deletions(tmp_path):
    database_path = tmp_path / "helpdesk.db"
    initialize_database(database_path)
    with connect(database_path) as connection:
        connection.execute(
            "UPDATE chamados SET descricao = 'edição mantida', status = 'fechado' WHERE id = 1001"
        )
        connection.execute("DELETE FROM chamados WHERE id = 1002")
        connection.execute(
            "INSERT INTO clientes (id, nome, email) VALUES (50, 'Cliente novo', 'novo@example.test')"
        )
        connection.execute(
            """INSERT INTO chamados
               (id, cliente_id, descricao, status, created_at, updated_at)
               VALUES (2050, 50, 'Registro do usuário', 'aberto', '2026-10-21T10:00:00Z',
                       '2026-10-21T10:00:00Z')"""
        )

    initialize_database(database_path)
    initialize_database(database_path)
    results = {ticket["id"]: ticket for ticket in listar_chamados(database_path=database_path)}
    assert results[1001]["descricao"] == "edição mantida"
    assert results[1001]["status"] == "fechado"
    assert 1002 not in results
    assert results[2050]["descricao"] == "Registro do usuário"
    assert len(results) == len(CHAMADOS)


def test_query_order_and_status_filter_are_deterministic(tmp_path):
    database_path = tmp_path / "helpdesk.db"
    with connect(database_path) as connection:
        create_schema(connection)
        connection.executemany(
            "INSERT INTO clientes (id, nome, email) VALUES (?, ?, ?)",
            [(1, "Cliente 1", "c1@example.test"), (2, "Cliente 2", "c2@example.test")],
        )
        connection.executemany(
            """INSERT INTO chamados
               (id, cliente_id, descricao, status, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            [
                (8, 1, "empate", "aberto", "2026-01-02T00:00:00Z", "2026-01-02T00:00:00Z"),
                (3, 2, "empate", "aberto", "2026-01-02T00:00:00Z", "2026-01-02T00:00:00Z"),
                (4, 1, "mais recente", "resolvido", "2026-01-03T00:00:00Z", "2026-01-03T00:00:00Z"),
            ],
        )

    assert [ticket["id"] for ticket in listar_chamados(database_path=database_path)] == [4, 3, 8]
    assert [ticket["id"] for ticket in listar_chamados("aberto", database_path)] == [3, 8]
    assert listar_chamados("fechado", database_path) == []


def test_query_does_not_modify_database(tmp_path):
    database_path = tmp_path / "helpdesk.db"
    initialize_database(database_path)
    with connect(database_path) as connection:
        before = connection.execute(
            "SELECT id, cliente_id, descricao, status, created_at, updated_at FROM chamados ORDER BY id"
        ).fetchall()

    listar_chamados(database_path=database_path)

    with connect(database_path) as connection:
        after = connection.execute(
            "SELECT id, cliente_id, descricao, status, created_at, updated_at FROM chamados ORDER BY id"
        ).fetchall()
    assert [tuple(row) for row in before] == [tuple(row) for row in after]


def test_real_sqlite_errors_are_not_converted_to_empty_list(tmp_path):
    path_that_is_a_directory = tmp_path / "database-directory"
    path_that_is_a_directory.mkdir()
    with pytest.raises(sqlite3.OperationalError):
        listar_chamados(database_path=path_that_is_a_directory)
