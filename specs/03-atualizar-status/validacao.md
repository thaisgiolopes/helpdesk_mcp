# Validação — Atualizar status

## Objetivo

Definir como verificar que `atualizar_status` atende aos requisitos da Fase 3 sem comprometer as ferramentas e os dados das fases anteriores.

## Estratégia

Usar `pytest`, bancos SQLite temporários e cliente MCP via `stdio`. Testar regras de persistência diretamente na camada SQLite e testar contrato, erros e descoberta por meio do cliente MCP. Os testes não devem depender do banco de desenvolvimento.

## Cenários

| ID | Cenário | Entrada/preparação | Resultado esperado |
|---|---|---|---|
| A01 | Atualização válida | Chamado existente e status permitido diferente do atual | Retorna o chamado com o novo status persistido |
| A02 | Status permitidos | Executar mudança para cada status canônico | Todos são aceitos exatamente como definidos |
| A03 | Data da mudança | Atualização real de status | `updated_at` muda para UTC no formato `YYYY-MM-DDTHH:MM:SSZ` |
| A04 | Preservação dos dados | Comparar campos antes e depois de atualização válida | `id`, `cliente_id`, `descricao` e `created_at` permanecem iguais |
| A05 | Mesmo status solicitado | Chamado já possui o status de destino | Sucesso idempotente; nenhum campo ou `updated_at` muda |
| A06 | Chamado inexistente | ID positivo não cadastrado | Erro claro; nenhum chamado é criado ou alterado |
| A07 | Identificador ausente ou nulo | Omitir `chamado_id` ou enviar nulo | Erro de validação |
| A08 | Tipo de identificador inválido | Booleano, string ou número fracionário | Erro de validação, sem coerção |
| A09 | Identificador fora do intervalo | Zero ou inteiro negativo | Erro de validação |
| A10 | Status ausente ou nulo | Omitir `novo_status` ou enviar nulo | Erro de validação |
| A11 | Status inválido | Vazio, espaços, desconhecido ou caixa diferente | Erro de validação; dados permanecem iguais |
| A12 | Atomicidade | Simular falha SQLite durante a atualização | Rollback; status, `updated_at` e demais campos preservados |
| A13 | Persistência | Atualizar e consultar em nova conexão | O novo status e timestamp continuam persistidos |
| A14 | Reflexo nas consultas existentes | Alterar status e consultar pelas ferramentas de listagem e histórico | Ambas retornam o status atualizado e os mesmos campos não mutáveis |
| A15 | Sem log de transições | Executar várias mudanças válidas | Nenhuma tabela ou registro de transição é criado nesta fase |
| A16 | Erro real de banco | Simular erro de acesso ao SQLite | Erro apropriado; não é mascarado como sucesso ou erro de domínio |
| A17 | Isolamento | Executar toda a suíte | Usa bancos temporários e não altera `data/helpdesk.db` |
| A18 | Integração MCP | Descobrir e invocar as três ferramentas via `stdio` | Ferramentas disponíveis; mudança, idempotência e erros são representados corretamente |

## Critério de aprovação

A fase está validada quando todos os cenários aplicáveis passam, a operação inválida ou inexistente não altera dados, a mudança válida persiste após nova conexão, as ferramentas anteriores continuam disponíveis e a atualização foi exercitada por cliente MCP via `stdio`.

Se o resultado divergir deste contrato, corrigir a implementação ou registrar a decisão aprovada nesta especificação antes de concluir a fase.

## Registro de execução

Na execução de 2026-10-22, `pytest -q` apresentou 47 testes aprovados e 1 falha. Os cenários A01–A17 passaram, incluindo persistência, idempotência, rollback, ferramentas MCP em processo e isolamento. O teste de integração via `stdio` falhou antes da descoberta das ferramentas, durante a inicialização do cliente MCP no Python 3.14.4 disponível. Python 3.12, versão-alvo, não estava instalado; A18 permanece pendente de repetição nesse runtime.
