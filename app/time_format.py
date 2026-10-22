"""Formatação de timestamps persistidos em UTC para exibição em Brasília."""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo


BRASILIA = ZoneInfo("America/Sao_Paulo")


def formatar_horario_brasilia(timestamp_utc: str) -> str:
    """Converte o timestamp ISO 8601 UTC do banco para o horário de Brasília."""
    try:
        valor = datetime.fromisoformat(timestamp_utc.replace("Z", "+00:00"))
        return valor.astimezone(BRASILIA).strftime("%d/%m/%Y %H:%M:%S BRT")
    except (AttributeError, ValueError):
        return timestamp_utc
