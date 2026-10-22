# Planejamento — Atualizar status

## Objetivo

Implementar `atualizar_status` de acordo com `requisitos.md`, preservando os dados do chamado e mantendo a operação atômica.

## 1. Confirmar o contrato

- [ ] Confirmar os parâmetros obrigatórios `chamado_id` e `novo_status`.
- [ ] Reutilizar o conjunto canônico de status e a regra comum de identificadores positivos sem coerção.
- [ ] Definir erro claro para chamado inexistente e parâmetros inválidos.
- [ ] Confirmar a saída como registro atualizado com os campos do chamado.
- [ ] Confirmar a operação idempotente quando o status já for o atual, sem alterar `updated_at`.
- [ ] Confirmar que transições anteriores não são registradas nesta fase.

**Conclusão:** contrato de entrada, saída, erros e idempotência está alinhado com a Constituição.

## 2. Preparar a persistência SQLite

- [ ] Reutilizar a conexão, o caminho do banco e a tabela definidos nas fases anteriores.
- [ ] Validar o chamado existente e o status antes de persistir a mudança.
- [ ] Atualizar apenas `status` e `updated_at` dentro de uma única transação.
- [ ] Gerar `updated_at` em UTC no formato `YYYY-MM-DDTHH:MM:SSZ`.
- [ ] Manter todos os campos originais quando o status solicitado já for o atual.
- [ ] Propagar erros reais do SQLite e garantir rollback de mudanças parciais.

**Conclusão:** mudanças válidas persistem em conjunto; erros deixam o chamado no estado anterior.

## 3. Implementar a ferramenta MCP

- [ ] Registrar `atualizar_status` no servidor FastMCP sem remover as ferramentas anteriores.
- [ ] Rejeitar IDs ausentes, nulos, booleanos, strings, fracionários, zero e negativos sem conversão implícita.
- [ ] Rejeitar status ausente, nulo, vazio, desconhecido ou com caixa diferente.
- [ ] Retornar erro de domínio claro para chamado inexistente.
- [ ] Retornar o registro atual do chamado em sucesso, inclusive no caso idempotente.
- [ ] Manter mensagens de diagnóstico fora de `stdout` para preservar `stdio`.

**Conclusão:** as três ferramentas ficam disponíveis e a nova respeita o contrato definido.

## 4. Testar

- [ ] Testar mudança válida para cada status permitido.
- [ ] Conferir formato UTC e alteração de `updated_at` após mudança real.
- [ ] Conferir que `id`, `cliente_id`, `descricao` e `created_at` permanecem intactos.
- [ ] Testar atualização repetida para o mesmo status e confirmar que `updated_at` não muda.
- [ ] Testar chamado inexistente e todos os casos de entrada inválida.
- [ ] Simular falha durante o `UPDATE` e confirmar rollback e preservação integral.
- [ ] Confirmar persistência após abrir nova conexão e resultado atualizado em `listar_chamados` e `buscar_historico_cliente`.
- [ ] Confirmar que nenhuma tabela de transições é criada ou preenchida.
- [ ] Testar descoberta e invocação das três ferramentas por cliente MCP via `stdio`.
- [ ] Usar banco temporário isolado em todos os testes.

**Conclusão:** os cenários de `validacao.md` passam no runtime-alvo Python 3.12.

## 5. Documentar

- [ ] Atualizar o README com `atualizar_status`, exemplo de argumentos e comportamento idempotente.
- [ ] Registrar qualquer desvio de contrato antes de incorporá-lo à implementação.

**Conclusão:** instalação, execução e demonstração das três ferramentas estão documentadas.

## Ordem

Não avançar para a integração Streamlit antes de concluir esta fase e registrar os resultados da validação.
