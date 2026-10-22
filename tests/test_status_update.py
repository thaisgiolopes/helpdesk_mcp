from __future__ import annotations

import asyncio
import sqlite3

import pytest
from fastmcp import Client

import database
from database import (
    ChamadoNaoEncontradoError,
    atualizar_status,
    buscar_historico_cliente,
    connect,
    initialize_database,
    listar_chamados,
)
from server import mcp


EXPECTED_FIELDS = {
    "id",
    "cliente_id",
    "descricao",
    "status",
    "created_at",
    "updated_at",
}


@pytest.mark.parametrize("status", sorted(database.VALID_STATUSES))
def test_database_updates_to_every_allowed_status(tmp_path, monkeypatch, status):
    database_path = tmp_path / "helpdesk.db"
    initialize_database(database_path)
    monkeypatch.setattr(database, "_utc_now", lambda: "2026-10-22T12:34:56Z")

    ticket = atualizar_status(1001, status, database_path)

    assert ticket["status"] == status
    assert ticket["updated_at"] == (
        "2026-10-20T13:00:00Z" if status == "aberto" else "2026-10-22T12:34:56Z"
    )
    assert set(ticket) == EXPECTED_FIELDS


def test_update_preserves_immutable_ticket_fields(tmp_path, monkeypatch):
    database_path = tmp_path / "helpdesk.db"
    initialize_database(database_path)
    before = next(
        ticket for ticket in listar_chamados(database_path=database_path)
        if ticket["id"] == 1001
    )
    monkeypatch.setattr(database, "_utc_now", lambda: "2026-10-22T12:34:56Z")

    updated = atualizar_status(1001, "em_atendimento", database_path)

    assert updated["status"] == "em_atendimento"
    assert updated["updated_at"] == "2026-10-22T12:34:56Z"
    for field in ("id", "cliente_id", "descricao", "created_at"):
        assert updated[field] == before[field]


def test_repeating_current_status_is_successful_noop(tmp_path, monkeypatch):
    database_path = tmp_path / "helpdesk.db"
    initialize_database(database_path)
    before = next(
        ticket for ticket in listar_chamados(database_path=database_path)
        if ticket["id"] == 1001
    )

    def unexpected_clock_call():
        pytest.fail("_utc_now não deve ser chamado quando o status não muda")

    monkeypatch.setattr(database, "_utc_now", unexpected_clock_call)
    result = atualizar_status(1001, "aberto", database_path)

    assert result == before


def test_update_missing_ticket_raises_domain_error_without_inserting(tmp_path):
    database_path = tmp_path / "helpdesk.db"
    initialize_database(database_path)
    before = listar_chamados(database_path=database_path)

    with pytest.raises(ChamadoNaoEncontradoError, match="Chamado não encontrado: 9999"):
        atualizar_status(9999, "fechado", database_path)

    assert listar_chamados(database_path=database_path) == before


@pytest.mark.parametrize("chamado_id", [None, True, False, 0, -1, 1.5, "1001"])
def test_update_rejects_invalid_ticket_ids(tmp_path, chamado_id):
    with pytest.raises(ValueError, match="chamado_id deve ser um inteiro positivo"):
        atualizar_status(chamado_id, "fechado", tmp_path / "helpdesk.db")


@pytest.mark.parametrize(
    "status", [None, True, 1, 1.5, "", "   ", "ABERTO", "desconhecido"]
)
def test_update_rejects_invalid_status_values(tmp_path, status):
    with pytest.raises(ValueError, match="Status inválido"):
        atualizar_status(1001, status, tmp_path / "helpdesk.db")


def test_update_rolls_back_sqlite_failure_and_preserves_record(tmp_path, monkeypatch):
    database_path = tmp_path / "helpdesk.db"
    initialize_database(database_path)
    before = next(
        ticket for ticket in listar_chamados(database_path=database_path)
        if ticket["id"] == 1001
    )
    with connect(database_path) as connection:
        connection.execute(
            """CREATE TRIGGER reject_ticket_update
               BEFORE UPDATE ON chamados
               BEGIN SELECT RAISE(ABORT, 'simulated update failure'); END"""
        )
    monkeypatch.setattr(database, "_utc_now", lambda: "2026-10-22T12:34:56Z")

    with pytest.raises(sqlite3.IntegrityError, match="simulated update failure"):
        atualizar_status(1001, "em_atendimento", database_path)

    after = next(
        ticket for ticket in listar_chamados(database_path=database_path)
        if ticket["id"] == 1001
    )
    assert after == before


def test_update_propagates_real_sqlite_access_error(tmp_path):
    path_that_is_a_directory = tmp_path / "database-directory"
    path_that_is_a_directory.mkdir()

    with pytest.raises(sqlite3.OperationalError):
        atualizar_status(1, "fechado", path_that_is_a_directory)


def test_update_persists_and_is_visible_in_existing_queries(tmp_path, monkeypatch):
    database_path = tmp_path / "helpdesk.db"
    initialize_database(database_path)
    monkeypatch.setattr(database, "_utc_now", lambda: "2026-10-22T12:34:56Z")

    atualizar_status(1001, "resolvido", database_path)

    with connect(database_path) as connection:
        persisted = connection.execute(
            "SELECT status, updated_at FROM chamados WHERE id = 1001"
        ).fetchone()
    listed = next(
        ticket for ticket in listar_chamados(database_path=database_path)
        if ticket["id"] == 1001
    )
    history = next(
        ticket for ticket in buscar_historico_cliente(1, database_path)
        if ticket["id"] == 1001
    )
    assert tuple(persisted) == ("resolvido", "2026-10-22T12:34:56Z")
    assert listed["status"] == history["status"] == "resolvido"
    assert listed["updated_at"] == history["updated_at"] == persisted["updated_at"]


def test_update_does_not_create_status_transition_history(tmp_path):
    database_path = tmp_path / "helpdesk.db"
    initialize_database(database_path)

    atualizar_status(1001, "em_atendimento", database_path)
    atualizar_status(1001, "resolvido", database_path)

    with connect(database_path) as connection:
        tables = {
            row["name"]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
    assert tables == {"clientes", "chamados", "app_metadata"}


def test_update_tool_contract_through_mcp_client(tmp_path, monkeypatch):
    database_path = tmp_path / "helpdesk.db"
    initialize_database(database_path)
    monkeypatch.setenv("HELPDESK_DB_PATH", str(database_path))

    async def run_checks():
        async with Client(mcp) as client:
            tool_names = {tool.name for tool in await client.list_tools()}
            assert {
                "listar_chamados",
                "buscar_historico_cliente",
                "atualizar_status",
            } <= tool_names

            changed = await client.call_tool(
                "atualizar_status",
                {"chamado_id": 1001, "novo_status": "em_atendimento"},
                raise_on_error=False,
            )
            assert not changed.is_error
            assert changed.data["status"] == "em_atendimento"
            assert set(changed.data) == EXPECTED_FIELDS

            listed = await client.call_tool(
                "listar_chamados", {}, raise_on_error=False
            )
            assert not listed.is_error
            listed_ticket = next(item for item in listed.data if item["id"] == 1001)
            assert listed_ticket["status"] == "em_atendimento"

            history = await client.call_tool(
                "buscar_historico_cliente", {"cliente_id": 1}, raise_on_error=False
            )
            assert not history.is_error
            history_ticket = next(item for item in history.data if item["id"] == 1001)
            assert history_ticket["status"] == "em_atendimento"

            repeated = await client.call_tool(
                "atualizar_status",
                {"chamado_id": 1001, "novo_status": "em_atendimento"},
                raise_on_error=False,
            )
            assert not repeated.is_error
            assert repeated.data == changed.data

            missing = await client.call_tool(
                "atualizar_status",
                {"chamado_id": 9999, "novo_status": "fechado"},
                raise_on_error=False,
            )
            assert missing.is_error
            assert "Chamado não encontrado" in missing.content[0].text

            invalid_inputs = [
                {},
                {"chamado_id": None, "novo_status": "fechado"},
                {"chamado_id": True, "novo_status": "fechado"},
                {"chamado_id": 1.5, "novo_status": "fechado"},
                {"chamado_id": 1001, "novo_status": None},
                {"chamado_id": 1001, "novo_status": "ABERTO"},
            ]
            for arguments in invalid_inputs:
                invalid = await client.call_tool(
                    "atualizar_status", arguments, raise_on_error=False
                )
                assert invalid.is_error, arguments

    asyncio.run(run_checks())
