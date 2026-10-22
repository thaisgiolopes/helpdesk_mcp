# Roadmap — Helpdesk MCP

## Fase 1 — Listar chamados

**Status:** Concluída — implementação entregue em 2026-10-22.

**Tool:** `listar_chamados`

**Objetivo:** Implementar a consulta dos chamados registrados no banco SQLite, permitindo listar todos os chamados ou filtrar os resultados por status.

**Critério geral de conclusão:** A ferramenta está implementada e testada por meio do servidor MCP, retornando os chamados corretamente, aplicando o filtro opcional por status e tratando entradas inválidas conforme a especificação.

**Registro da conclusão:** Persistência SQLite, inicialização idempotente, contrato de consulta, testes e documentação foram implementados. Na execução disponível, 7 testes passaram; a verificação de cliente MCP via `stdio` não concluiu a inicialização usando Python 3.14.4. Como a versão-alvo é Python 3.12 e ela não estava instalada neste ambiente, a validação V14 permanece pendente nesse runtime. A ferramenta foi descoberta e invocada com sucesso pelo cliente MCP em processo; isso não substitui o teste `stdio` previsto.

## Fase 2 — Buscar histórico de cliente

**Tool:** `buscar_historico_cliente`

**Objetivo:** Implementar a consulta dos chamados associados a um cliente específico, permitindo visualizar seu histórico de atendimento.

**Critérios de conclusão:**
- Recebe um `cliente_id` válido e retorna somente os chamados vinculados a ele.
- Retorna `[]` para cliente existente sem chamados e um erro claro para cliente inexistente, distinguindo os dois casos.
- Ordena por `created_at` decrescente e, em caso de empate, por `id` crescente.
- É descoberta e invocada por cliente MCP via `stdio`; os casos de sucesso, cliente inexistente e cliente sem chamados são testados.

**Decisão de escopo:** “Histórico” nesta fase significa a lista de chamados do cliente. Não representa o registro das transições de status ao longo do tempo.

## Fase 3 — Atualizar status

**Tool:** `atualizar_status`

**Objetivo:** Implementar a atualização do status de um chamado existente, validando o identificador do chamado e o novo status informado.

**Critérios de conclusão:**
- Recebe um identificador de chamado e um dos status permitidos na especificação vigente.
- Persiste o novo status e atualiza `updated_at` na mesma transação.
- Retorna resultado claro para chamado inexistente e status inválido; falhas não alteram o registro.
- É descoberta e invocada por cliente MCP via `stdio`; sucesso, status inválido, chamado inexistente e persistência após nova conexão são testados.
- Não cria uma tabela de transições de status nesta fase; o banco mantém o estado atual do chamado.

## Critério geral do roadmap

As fases deverão ser concluídas na ordem apresentada. Antes de implementar cada fase, deverá existir uma especificação funcional com parâmetros, retornos, validações, erros e cenários de teste; a implementação e os testes devem atender a essa especificação.

Ao final das três fases, o servidor deverá disponibilizar as três ferramentas MCP e permitir demonstrar suas operações com dados fictícios no banco SQLite. A integração com a aplicação Streamlit será desenvolvida posteriormente, em uma etapa separada, fora destas três fases.
