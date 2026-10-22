"""FastMCP stdio server exposing the first two Helpdesk tools."""

from __future__ import annotations

from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

from database import (
    ClienteNaoEncontradoError,
    buscar_historico_cliente as consultar_historico_cliente,
    initialize_database,
    listar_chamados as consultar_chamados,
)


VALID_STATUSES = {
    "aberto",
    "em_atendimento",
    "aguardando_cliente",
    "resolvido",
    "fechado",
}

mcp = FastMCP("Helpdesk MCP")


@mcp.tool()
async def listar_chamados(status: str | None = None) -> list[dict]:
    """Lista chamados por data de criação, opcionalmente filtrados por status.

    Args:
        status: Um status aceito ou nulo para listar todos.
    """
    if status is not None and status not in VALID_STATUSES:
        allowed = ", ".join(sorted(VALID_STATUSES))
        raise ValueError(f"Status inválido: {status!r}. Valores aceitos: {allowed}.")
    return consultar_chamados(status)


@mcp.tool()
async def buscar_historico_cliente(
    cliente_id: Annotated[int, Field(strict=True, gt=0)],
) -> list[dict]:
    """Busca os chamados vinculados a um cliente existente.

    Args:
        cliente_id: Identificador inteiro positivo do cliente.
    """
    try:
        return consultar_historico_cliente(cliente_id)
    except ClienteNaoEncontradoError as error:
        raise ValueError(str(error)) from None


def main() -> None:
    initialize_database()
    mcp.run(transport="stdio", show_banner=False, log_level="ERROR")


if __name__ == "__main__":
    main()
