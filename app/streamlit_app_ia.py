"""Chat de perguntas livres com seleção local de tools via Ollama e MCP."""

from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any

import streamlit as st
from fastmcp import Client as MCPClient
from fastmcp.client.transports import StdioTransport
from ollama import Client as OllamaClient

try:
    from app.time_format import formatar_horario_brasilia
except ModuleNotFoundError:  # Streamlit também pode executar o arquivo como script
    from time_format import formatar_horario_brasilia


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OLLAMA_MODEL = os.environ.get("HELPDESK_LLM_MODEL", "qwen3:4b")
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
VALID_STATUSES = (
    "aberto",
    "em_atendimento",
    "aguardando_cliente",
    "resolvido",
    "fechado",
)
SYSTEM_PROMPT = """Você é um assistente para atendentes de helpdesk. Responda em português.
Use as ferramentas MCP disponíveis para consultar chamados ou histórico e para
alterar status. Escolha uma ferramenta adequada quando a pergunta exigir dados
do helpdesk. Não invente IDs, status ou resultados; use somente o que vier das
ferramentas. Os status aceitos são: aberto, em_atendimento,
aguardando_cliente, resolvido e fechado. Se faltarem dados para uma operação,
peça esclarecimento. A aplicação pedirá confirmação explícita antes de executar
atualizar_status; nunca diga que uma alteração foi concluída antes do resultado
da ferramenta. Para assuntos fora do helpdesk, explique brevemente o escopo."""


def criar_transporte() -> StdioTransport:
    return StdioTransport(
        command=sys.executable,
        args=["-m", "server"],
        env=os.environ.copy(),
        cwd=str(PROJECT_ROOT),
    )


async def descobrir_tools() -> list[Any]:
    async with MCPClient(criar_transporte(), timeout=30) as cliente:
        return await cliente.list_tools()


async def chamar_tool(nome: str, argumentos: dict[str, Any]):
    async with MCPClient(criar_transporte(), timeout=30) as cliente:
        return await cliente.call_tool(nome, argumentos, raise_on_error=False)


def schema_para_ollama(tool: Any) -> dict[str, Any]:
    """Adapta o JSON Schema MCP ao formato de function tools do Ollama."""
    schema = tool.model_dump().get("input_schema", {})
    propriedades = {}
    for nome, definicao in schema.get("properties", {}).items():
        campo = dict(definicao)
        tipos = campo.pop("anyOf", None)
        if tipos:
            campo["type"] = next(
                (opcao["type"] for opcao in tipos if opcao.get("type") != "null"),
                "string",
            )
        campo.pop("default", None)
        campo.pop("exclusiveMinimum", None)
        propriedades[nome] = campo

    if tool.name == "atualizar_status" and "novo_status" in propriedades:
        propriedades["novo_status"]["enum"] = list(VALID_STATUSES)

    parametros = {
        "type": "object",
        "properties": propriedades,
        "required": schema.get("required", []),
    }
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description or tool.name,
            "parameters": parametros,
        },
    }


def erro_da_tool(resultado: Any) -> str | None:
    if not resultado.is_error:
        return None
    mensagens = [
        item.text for item in resultado.content if getattr(item, "text", None)
    ]
    return "Não foi possível concluir: " + (
        " ".join(mensagens) if mensagens else "o servidor MCP retornou um erro."
    )


def formatar_chamados(chamados: list[dict[str, Any]]) -> str:
    if not chamados:
        return "Nenhum chamado encontrado."

    saida = [f"Encontrei **{len(chamados)} chamado(s)**:"]
    for chamado in chamados:
        saida.append(
            "\n".join(
                (
                    f"**Chamado #{chamado['id']}** · {chamado['status']}",
                    f"Cliente: {chamado['cliente_id']}",
                    f"Descrição: {chamado['descricao']}",
                    "Criado (Brasília): "
                    f"{formatar_horario_brasilia(chamado['created_at'])}",
                    "Atualizado (Brasília): "
                    f"{formatar_horario_brasilia(chamado['updated_at'])}",
                )
            )
        )
    return "\n\n".join(saida)


def formatar_resultado(resultado: Any) -> str:
    erro = erro_da_tool(resultado)
    if erro:
        return erro

    dados = resultado.data
    if isinstance(dados, list):
        return formatar_chamados(dados)
    if isinstance(dados, dict):
        return "Atualização concluída.\n\n" + formatar_chamados([dados])
    return str(dados)


def validar_atualizacao(argumentos: dict[str, Any]) -> str | None:
    chamado_id = argumentos.get("chamado_id")
    status = argumentos.get("novo_status")
    if type(chamado_id) is not int or chamado_id < 1:
        return "Não consegui identificar um ID de chamado inteiro e positivo."
    if type(status) is not str or status not in VALID_STATUSES:
        return "O status informado não é válido. Valores aceitos: " + ", ".join(
            VALID_STATUSES
        )
    return None


def selecionar_tool(pergunta: str) -> tuple[str | None, dict[str, Any], str]:
    """Pede ao modelo local que selecione uma das tools MCP disponíveis."""
    try:
        tools_mcp = asyncio.run(descobrir_tools())
        ferramentas = {tool.name: tool for tool in tools_mcp}
        ferramentas_ollama = [schema_para_ollama(tool) for tool in tools_mcp]
    except Exception as erro:
        return None, {}, f"Não consegui conectar ao servidor MCP: {erro}"

    try:
        modelo = OllamaClient(host=OLLAMA_HOST)
        resposta = modelo.chat(
            model=OLLAMA_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": pergunta},
            ],
            tools=ferramentas_ollama,
            options={"temperature": 0},
        )
    except Exception as erro:
        return (
            None,
            {},
            "Não consegui acessar o modelo local. Inicie o Ollama e baixe o modelo "
            f"`{OLLAMA_MODEL}`. Detalhe: {erro}",
        )

    chamadas = resposta.message.tool_calls or []
    if not chamadas:
        return None, {}, resposta.message.content or (
            "Não identifiquei uma operação do helpdesk para essa pergunta."
        )
    if len(chamadas) != 1:
        return None, {}, "Faça uma solicitação por vez para eu executar a operação com segurança."

    chamada = chamadas[0].function
    nome = chamada.name
    argumentos = dict(chamada.arguments)
    if nome not in ferramentas:
        return None, {}, "O modelo selecionou uma ferramenta que não está no servidor MCP."
    return nome, argumentos, ""


def preparar_resposta(pergunta: str) -> tuple[str, dict[str, Any] | None]:
    nome, argumentos, texto = selecionar_tool(pergunta)
    if nome is None:
        return texto, None

    if nome == "atualizar_status":
        erro = validar_atualizacao(argumentos)
        if erro:
            return erro, None
        return (
            "O modelo propôs atualizar o chamado "
            f"**#{argumentos['chamado_id']}** para **{argumentos['novo_status']}**. "
            "Confirme a operação abaixo para enviá-la ao servidor MCP.",
            {"name": nome, "arguments": argumentos},
        )

    try:
        resultado = asyncio.run(chamar_tool(nome, argumentos))
        return formatar_resultado(resultado), None
    except Exception as erro:
        return f"Não consegui chamar o servidor MCP: {erro}", None


def confirmar_atualizacao(pendente: dict[str, Any]) -> str:
    try:
        resultado = asyncio.run(
            chamar_tool(pendente["name"], pendente["arguments"])
        )
        return formatar_resultado(resultado)
    except Exception as erro:
        return f"Não consegui chamar o servidor MCP: {erro}"


st.set_page_config(page_title="Atendimento Helpdesk com IA local", page_icon="🎫")
st.title("Atendimento Helpdesk")
st.write(
    "Faça perguntas em linguagem natural. Um modelo local escolhe a ferramenta MCP "
    "adequada; os dados e as alterações continuam sendo tratados pelo servidor "
    "Helpdesk. Nenhuma API paga é necessária."
)
st.caption(
    f"Modelo local: `{OLLAMA_MODEL}`. Datas exibidas no horário de Brasília. "
    "Alterações de status exigem confirmação antes de chamar a ferramenta."
)

if "messages_ia" not in st.session_state:
    st.session_state.messages_ia = [
        {"role": "assistant", "content": "Olá! O que você precisa saber sobre os chamados?"}
    ]
if "pending_update" not in st.session_state:
    st.session_state.pending_update = None

for mensagem in st.session_state.messages_ia:
    with st.chat_message(mensagem["role"]):
        st.markdown(mensagem["content"])

pendente = st.session_state.pending_update
if pendente:
    col_confirmar, col_cancelar = st.columns(2)
    if col_confirmar.button("Confirmar atualização", type="primary"):
        with st.spinner("Atualizando pelo servidor MCP..."):
            resposta = confirmar_atualizacao(pendente)
        st.session_state.messages_ia.append(
            {"role": "assistant", "content": resposta}
        )
        st.session_state.pending_update = None
        st.rerun()
    if col_cancelar.button("Cancelar atualização"):
        st.session_state.messages_ia.append(
            {"role": "assistant", "content": "Atualização cancelada; nenhuma alteração foi enviada."}
        )
        st.session_state.pending_update = None
        st.rerun()

pergunta = st.chat_input(
    "Escreva sua pergunta sobre o helpdesk",
    disabled=bool(st.session_state.pending_update),
)
if pergunta:
    st.session_state.messages_ia.append({"role": "user", "content": pergunta})
    with st.chat_message("user"):
        st.markdown(pergunta)

    with st.chat_message("assistant"):
        with st.spinner("Interpretando a pergunta e consultando as ferramentas..."):
            resposta, pendente = preparar_resposta(pergunta)
        st.markdown(resposta)

    st.session_state.messages_ia.append({"role": "assistant", "content": resposta})
    st.session_state.pending_update = pendente
