"""Chat simples de helpdesk que chama as ferramentas pelo protocolo MCP."""

from __future__ import annotations

import asyncio
import os
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any

import streamlit as st
from fastmcp import Client
from fastmcp.client.transports import StdioTransport

try:
    from app.time_format import formatar_horario_brasilia
except ModuleNotFoundError:  # Streamlit também pode executar o arquivo como script
    from time_format import formatar_horario_brasilia


PROJECT_ROOT = Path(__file__).resolve().parents[1]
def normalizar(texto: str) -> str:
    sem_acentos = unicodedata.normalize("NFKD", texto)
    sem_acentos = "".join(char for char in sem_acentos if not unicodedata.combining(char))
    return re.sub(r"\s+", " ", sem_acentos.casefold()).strip()


def extrair_status(texto: str) -> str | None:
    texto = normalizar(texto).replace("_", " ")
    formas = {
        "aberto": ("aberto", "abertos", "aberta", "abertas"),
        "em_atendimento": ("em atendimento",),
        "aguardando_cliente": (
            "aguardando cliente",
            "aguardando o cliente",
        ),
        "resolvido": ("resolvido", "resolvidos", "resolvida", "resolvidas"),
        "fechado": ("fechado", "fechados", "fechada", "fechadas"),
    }
    for status, variantes in formas.items():
        if any(re.search(rf"\b{re.escape(forma)}\b", texto) for forma in variantes):
            return status
    return None


def interpretar_comando(mensagem: str) -> tuple[str, dict[str, Any]] | None:
    """Converte comandos de texto simples em uma chamada de ferramenta MCP."""
    texto = normalizar(mensagem).strip(" .!?;:")

    atualizar = re.search(
        r"\b(?:atualize|atualizar|mude|alterar|altere|troque)\s+"
        r"(?:o\s+)?chamado\s+(\d+)\s+(?:para|como)\s+(.+)$",
        texto,
    )
    if atualizar:
        status_texto = atualizar.group(2).strip(" .!?;:")
        status = extrair_status(status_texto) or status_texto.replace(" ", "_")
        return "atualizar_status", {
            "chamado_id": int(atualizar.group(1)),
            "novo_status": status,
        }

    historico = re.search(
        r"\b(?:historico|chamados?)\b.*?\bcliente\s+(\d+)\b", texto
    )
    if historico and any(palavra in texto for palavra in ("historico", "chamados")):
        return "buscar_historico_cliente", {"cliente_id": int(historico.group(1))}

    verbo_lista = re.search(
        r"\b(liste|listar|lista|mostre|mostrar|exiba|quais|ver)\b", texto
    )
    tem_alvo_de_lista = bool(
        re.search(r"\bchamados?\b", texto)
        or extrair_status(texto)
        or re.search(r"\btodos?\b", texto)
    )
    tem_intencao_de_lista = bool(verbo_lista and tem_alvo_de_lista)
    if tem_intencao_de_lista:
        status = extrair_status(texto)
        if status:
            return "listar_chamados", {"status": status}

        status_explicitado = re.search(r"\bstatus\s+(?:de\s+)?(.+)$", texto)
        if status_explicitado:
            valor = status_explicitado.group(1).strip(" .!?;:")
            return "listar_chamados", {"status": valor.replace(" ", "_")}

        return "listar_chamados", {}

    return None


async def chamar_tool(nome: str, argumentos: dict[str, Any]):
    ambiente = os.environ.copy()
    transporte = StdioTransport(
        command=sys.executable,
        args=["-m", "server"],
        env=ambiente,
        cwd=str(PROJECT_ROOT),
    )
    async with Client(transporte, timeout=30) as cliente:
        return await cliente.call_tool(nome, argumentos, raise_on_error=False)


def renderizar_chamados(chamados: list[dict[str, Any]]) -> str:
    if not chamados:
        return "Nenhum chamado encontrado."

    blocos = [f"Encontrei **{len(chamados)} chamado(s)**:"]
    for chamado in chamados:
        blocos.append(
            "\n".join(
                [
                    f"**Chamado #{chamado['id']}** · {chamado['status']}",
                    f"Cliente: {chamado['cliente_id']}",
                    f"Descrição: {chamado['descricao']}",
                    "Criado (Brasília): "
                    f"{formatar_horario_brasilia(chamado['created_at'])} · "
                    "Atualizado (Brasília): "
                    f"{formatar_horario_brasilia(chamado['updated_at'])}",
                ]
            )
        )
    return "\n\n".join(blocos)


def formatar_resultado(resultado: Any) -> str:
    if resultado.is_error:
        mensagens = [
            item.text for item in resultado.content if getattr(item, "text", None)
        ]
        return "Não foi possível concluir a solicitação: " + (
            " ".join(mensagens) if mensagens else "o servidor MCP retornou um erro."
        )

    dados = resultado.data
    if isinstance(dados, list):
        return renderizar_chamados(dados)
    if isinstance(dados, dict):
        return "Status atualizado com sucesso.\n\n" + renderizar_chamados([dados])
    return str(dados)


def responder(mensagem: str) -> str:
    chamada = interpretar_comando(mensagem)
    if chamada is None:
        return (
            "Não reconheci esse comando. Exemplos: `listar abertos`, "
            "`histórico do cliente 2` ou `alterar chamado 1001 para fechado`. "
            "Nos dados demonstrativos, os chamados vão de 1001 a 1006, os clientes "
            "de 1 a 3, e os status aceitos são aberto, em_atendimento, "
            "aguardando_cliente, resolvido e fechado."
        )

    nome, argumentos = chamada
    try:
        resultado = asyncio.run(chamar_tool(nome, argumentos))
        return formatar_resultado(resultado)
    except Exception as erro:  # falha de conexão ou inicialização do servidor MCP
        return f"Não consegui conectar ao servidor MCP: {erro}"


st.set_page_config(page_title="Atendimento Helpdesk", page_icon="🎫")
st.title("Atendimento Helpdesk")
st.write(
    "Olá! Use comandos simples para consultar chamados, ver o histórico de um "
    "cliente ou atualizar um status. As solicitações são encaminhadas ao servidor "
    "Helpdesk pelo protocolo MCP; esta versão não usa IA."
)
st.caption(
    "Exemplos: “listar abertos”, “histórico do cliente 2” e "
    "“alterar chamado 1001 para fechado”. IDs demonstrativos: chamados 1001–1006; "
    "clientes 1–3. Status: aberto, em_atendimento, aguardando_cliente, resolvido e fechado."
)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Como posso ajudar com os chamados?",
        }
    ]

for mensagem in st.session_state.messages:
    with st.chat_message(mensagem["role"]):
        st.markdown(mensagem["content"])

entrada = st.chat_input("Digite um comando para o helpdesk")
if entrada:
    st.session_state.messages.append({"role": "user", "content": entrada})
    with st.chat_message("user"):
        st.markdown(entrada)

    resposta = responder(entrada)
    st.session_state.messages.append({"role": "assistant", "content": resposta})
    with st.chat_message("assistant"):
        st.markdown(resposta)
