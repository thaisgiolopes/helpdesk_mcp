"""FastMCP stdio server exposing the first-phase ticket listing tool."""

from __future__ import annotations

from fastmcp import FastMCP

from database import initialize_database, listar_chamados as consultar_chamados


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


def main() -> None:
    initialize_database()
    mcp.run(transport="stdio", show_banner=False, log_level="ERROR")


if __name__ == "__main__":
    main()
