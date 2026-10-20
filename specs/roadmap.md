# Roadmap — Helpdesk MCP

## Fase 1 — Listar chamados

**Tool:** `listar_chamados`

**Objetivo:** Implementar a consulta dos chamados registrados no banco SQLite, permitindo listar todos os chamados ou filtrar os resultados por status.

**Critério geral de conclusão:** A ferramenta está implementada e testada por meio do servidor MCP, retornando os chamados corretamente, aplicando o filtro opcional por status e tratando entradas inválidas conforme a especificação.

## Fase 2 — Buscar histórico de cliente

**Tool:** `buscar_historico_cliente`

**Objetivo:** Implementar a consulta dos chamados associados a um cliente específico, permitindo visualizar seu histórico de atendimento.

**Critério geral de conclusão:** A ferramenta está implementada e testada por meio do servidor MCP, retornando os chamados do cliente solicitado e tratando adequadamente clientes inexistentes ou sem chamados registrados.

## Fase 3 — Atualizar status

**Tool:** `atualizar_status`

**Objetivo:** Implementar a atualização do status de um chamado existente, validando o identificador do chamado e o novo status informado.

**Critério geral de conclusão:** A ferramenta está implementada e testada por meio do servidor MCP, persistindo atualizações válidas no SQLite e tratando chamados inexistentes e status inválidos sem modificar indevidamente os dados.

## Critério geral do roadmap

As fases deverão ser concluídas na ordem apresentada. Cada fase deverá possuir uma especificação funcional, implementação correspondente e testes que verifiquem seus critérios de aceitação.

Ao final das três fases, o servidor deverá disponibilizar as três ferramentas MCP e permitir demonstrar suas operações com dados fictícios no banco SQLite. A integração com a aplicação Streamlit será desenvolvida posteriormente, em uma etapa separada.
