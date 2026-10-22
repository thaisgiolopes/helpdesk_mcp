# Validação — Listar chamados

## Objetivo
Definir como verificar que `listar_chamados` atende aos requisitos antes de considerar a Fase 1 concluída.

## Estratégia
Usar `pytest`, banco SQLite temporário e testes de integração por meio de um cliente MCP. Os testes não devem depender do banco de desenvolvimento nem de dados reais.

## Cenários

| ID | Cenário | Entrada/preparação | Resultado esperado |
|---|---|---|---|
| V01 | Listar sem filtro | Banco com chamados de diferentes status; omitir `status` | Todos os chamados, com os campos obrigatórios e ordenação definida |
| V02 | Filtrar por status válido | Executar para cada status aceito | Todos os itens retornados têm o status solicitado |
| V03 | Status válido sem correspondências | Status válido ausente nos dados de teste | Retorna `[]`, sem erro |
| V04 | Banco sem chamados | Tabelas existem, sem registros | Retorna `[]` |
| V05 | Status desconhecido | Valor fora da lista | Erro de validação claro |
| V06 | Status vazio | String vazia ou apenas espaços | Erro de validação claro |
| V07 | Status omitido ou nulo | Omitir o parâmetro ou fornecer nulo | Consulta sem filtro |
| V08 | Campos de saída | Consulta com resultados | Cada item contém `id`, `cliente_id`, `descricao`, `status`, `created_at` e `updated_at` |
| V09 | Ordenação | Datas distintas e empatadas | Mais recentes primeiro; empates por `id` crescente |
| V10 | Sem alteração de dados | Comparar banco antes e depois | A consulta não cria, altera nem remove chamados |
| V11 | Inicialização inicial | Banco inexistente | Banco, tabelas e dados fictícios são criados |
| V12 | Inicialização repetida | Executar inicialização várias vezes | Não duplica registros iniciais nem apaga alterações existentes |
| V13 | Isolamento | Executar suíte de testes | Usa banco temporário e não modifica `data/helpdesk.db` |
| V14 | Integração MCP | Invocar a ferramenta por cliente MCP via `stdio` | Ferramenta descoberta e invocada com resultado esperado |
| V15 | Falha real de banco | Simular erro de acesso ao SQLite | Erro apropriado; não é mascarado como `[]` |

## Critério de aprovação
A fase está concluída quando todos os cenários aplicáveis passam, a ferramenta foi invocada por um cliente MCP, a inicialização idempotente foi verificada e a documentação de execução está atualizada.

Divergências entre a implementação e os requisitos devem ser corrigidas ou discutidas e registradas nas especificações antes da conclusão da fase.

## Registro de execução

Na execução registrada em 2026-10-21, `pytest` apresentou 7 testes aprovados e 1 falha. Os cenários de contrato, persistência, isolamento e inicialização passaram. O teste V14 (cliente MCP via `stdio`) falhou durante a inicialização do cliente no Python 3.14.4 disponível. A versão-alvo Python 3.12 não estava instalada, portanto V14 continua pendente de repetição no runtime previsto. A chamada pelo cliente MCP em processo passou, mas não substitui V14.
