from __future__ import annotations

import asyncio
import os
import sqlite3
import sys
from pathlib import Path

from fastmcp import Client
from fastmcp.client.transports import StdioTransport
import pytest

from database import initialize_database
from server import mcp


STATUSES = ["aberto", "em_atendimento", "aguardando_cliente", "resolvido", "fechado"]
PROJECT_ROOT = Path(__file__).resolve().parents[1]


async def run_mcp_checks():
    async with Client(mcp) as client:
        tools = await client.list_tools()
        tool_names = {tool.name for tool in tools}
        assert "listar_chamados" in tool_names
        assert "buscar_historico_cliente" in tool_names

        result = await client.call_tool("listar_chamados", {}, raise_on_error=False)
        assert not result.is_error
        tickets = result.data
        assert len(tickets) == 6
        assert set(tickets[0]) == {
            "id", "cliente_id", "descricao", "status", "created_at", "updated_at"
        }
        expected_order = sorted(tickets, key=lambda item: item["id"])
        expected_order.sort(key=lambda item: item["created_at"], reverse=True)
        assert [item["id"] for item in tickets] == [item["id"] for item in expected_order]

        result = await client.call_tool(
            "listar_chamados", {"status": None}, raise_on_error=False
        )
        assert not result.is_error
        assert len(result.data) == 6

        for status in STATUSES:
            result = await client.call_tool(
                "listar_chamados", {"status": status}, raise_on_error=False
            )
            assert not result.is_error
            assert all(item["status"] == status for item in result.data)

        invalid = await client.call_tool(
            "listar_chamados", {"status": "ABERTO"}, raise_on_error=False
        )
        assert invalid.is_error
        assert "Status inválido" in invalid.content[0].text
        for status in ("", "   ", "desconhecido"):
            result = await client.call_tool(
                "listar_chamados", {"status": status}, raise_on_error=False
            )
            assert result.is_error
            assert "Status inválido" in result.content[0].text


def test_tool_is_discoverable_and_works_through_mcp_client(tmp_path, monkeypatch):
    database_path = tmp_path / "helpdesk.db"
    initialize_database(database_path)
    monkeypatch.setenv("HELPDESK_DB_PATH", str(database_path))
    asyncio.run(run_mcp_checks())


def test_tool_returns_empty_list_for_empty_database_through_mcp_client(tmp_path, monkeypatch):
    database_path = tmp_path / "helpdesk.db"
    initialize_database(database_path)
    with sqlite3.connect(database_path) as connection:
        connection.execute("DELETE FROM chamados")
    monkeypatch.setenv("HELPDESK_DB_PATH", str(database_path))

    async def run_empty_check():
        async with Client(mcp) as client:
            result = await client.call_tool(
                "listar_chamados", {"status": "aberto"}, raise_on_error=False
            )
            assert not result.is_error
            assert result.data == []

    asyncio.run(run_empty_check())


def test_tool_is_invokable_by_mcp_client_over_stdio(tmp_path):
    database_path = tmp_path / "helpdesk.db"
    env = {**os.environ, "HELPDESK_DB_PATH": str(database_path)}
    transport = StdioTransport(
        command=sys.executable,
        args=[str(PROJECT_ROOT / "server.py")],
        env=env,
        cwd=str(PROJECT_ROOT),
        log_file=tmp_path / "server.stderr.log",
    )

    async def run_stdio_check():
        async with Client(
            transport, timeout=10, init_timeout=10, mode="legacy"
        ) as client:
            tools = await client.list_tools()
            tool_names = {tool.name for tool in tools}
            assert "listar_chamados" in tool_names
            assert "buscar_historico_cliente" in tool_names
            result = await client.call_tool(
                "listar_chamados", {"status": "aberto"}, raise_on_error=False
            )
            assert not result.is_error
            assert result.data
            assert all(ticket["status"] == "aberto" for ticket in result.data)
            history = await client.call_tool(
                "buscar_historico_cliente", {"cliente_id": 1}, raise_on_error=False
            )
            assert not history.is_error
            assert all(ticket["cliente_id"] == 1 for ticket in history.data)

    asyncio.run(run_stdio_check())
