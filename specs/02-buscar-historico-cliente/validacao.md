# Validação — Buscar histórico de cliente

## Objetivo

Definir como verificar que `buscar_historico_cliente` atende aos requisitos da Fase 2.

## Estratégia

Usar `pytest`, bancos SQLite temporários e integração por cliente MCP via `stdio`. Os cenários não devem depender do banco de desenvolvimento. Os testes de persistência podem chamar a camada SQLite diretamente; os testes do contrato devem invocar a ferramenta pelo cliente MCP.

## Cenários

| ID | Cenário | Entrada/preparação | Resultado esperado |
|---|---|---|---|
| H01 | Histórico com um chamado | Cliente existente com um chamado | Retorna o chamado daquele cliente |
| H02 | Histórico com vários chamados | Cliente existente com vários chamados e chamados de outros clientes | Retorna todos e somente os chamados do cliente solicitado |
| H03 | Cliente sem chamados | Cliente existente sem registros em `chamados` | Retorna `[]`, sem erro |
| H04 | Cliente inexistente | ID positivo não cadastrado | Erro claro de cliente não encontrado, não `[]` |
| H05 | Identificador ausente | Omitir `cliente_id` | Erro de validação |
| H06 | Identificador nulo | `cliente_id: null` | Erro de validação |
| H07 | Tipo inválido | Booleano, string ou número fracionário | Erro de validação, sem conversão implícita |
| H08 | Identificador fora do intervalo | Zero ou inteiro negativo | Erro de validação |
| H09 | Campos de saída | Consulta com resultados | Cada item contém `id`, `cliente_id`, `descricao`, `status`, `created_at` e `updated_at` |
| H10 | Ordenação determinística | Datas distintas e empatadas | Mais recentes primeiro; empates por `id` crescente |
| H11 | Sem alteração de dados | Comparar clientes e chamados antes e depois | A consulta não cria, altera nem remove registros |
| H12 | Falha real de banco | Simular erro de acesso ao SQLite | Erro apropriado; não é mascarado como `[]` ou cliente inexistente |
| H13 | Isolamento dos testes | Executar a suíte | Usa banco temporário e não altera `data/helpdesk.db` |
| H14 | Integração MCP | Descobrir e invocar a ferramenta via `stdio` | Ferramenta descoberta; sucesso e erros de domínio são representados corretamente |

## Critério de aprovação

A fase está validada quando todos os cenários aplicáveis passam, a ferramenta é descoberta e invocada por cliente MCP via `stdio`, os erros de domínio são distintos dos resultados vazios e a documentação de execução está atualizada.

Se houver divergência entre o comportamento observado e este contrato, corrigir a implementação ou discutir e registrar a mudança nesta especificação antes de concluir a fase.
