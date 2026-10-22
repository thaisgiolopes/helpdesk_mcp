# Planejamento — Buscar histórico de cliente

## Objetivo

Implementar `buscar_historico_cliente` de acordo com `requisitos.md`, separando a consulta SQLite do registro da ferramenta MCP.

## 1. Confirmar o contrato

- [ ] Confirmar `cliente_id` obrigatório como inteiro positivo, sem conversão implícita.
- [ ] Distinguir cliente existente sem chamados (`[]`) de cliente inexistente (erro claro).
- [ ] Reutilizar os campos e a ordenação definidos para os chamados.
- [ ] Confirmar que histórico significa lista de chamados, sem log de transições.

**Conclusão:** entrada, saída, erros e limites estão definidos antes da implementação.

## 2. Preparar a consulta SQLite

- [ ] Reutilizar as funções de conexão e o caminho de banco definidos na Fase 1.
- [ ] Consultar chamados por `cliente_id` com parâmetros SQL vinculados.
- [ ] Verificar a existência do cliente para diferenciar cliente inexistente de cliente sem chamados.
- [ ] Ordenar por `created_at` decrescente e `id` crescente em caso de empate.
- [ ] Manter a operação somente leitura e propagar falhas reais do banco.

**Conclusão:** a persistência retorna apenas o histórico do cliente solicitado, sem alterar os dados.

## 3. Implementar a tool MCP

- [ ] Registrar `buscar_historico_cliente` no servidor FastMCP.
- [ ] Validar o parâmetro obrigatório e rejeitar valores inválidos sem coerção.
- [ ] Retornar os chamados no formato definido em `requisitos.md`.
- [ ] Retornar lista vazia para cliente existente sem chamados.
- [ ] Retornar erro claro para cliente inexistente.
- [ ] Manter mensagens de diagnóstico fora de `stdout` para preservar o transporte `stdio`.

**Conclusão:** a ferramenta está descoberta e aplica o contrato funcional.

## 4. Testar

- [ ] Testar clientes com chamados, incluindo cliente com mais de um chamado.
- [ ] Testar cliente existente sem chamados.
- [ ] Testar cliente inexistente.
- [ ] Testar parâmetro ausente, nulo, booleano, string, fracionário, zero e negativo.
- [ ] Verificar os campos, a ordenação e a exclusão de chamados de outros clientes.
- [ ] Comparar os dados antes e depois da consulta.
- [ ] Simular falha real do SQLite e confirmar que não é convertida em lista vazia.
- [ ] Testar descoberta e invocação por cliente MCP via `stdio`.
- [ ] Confirmar que os testes usam banco temporário isolado.

**Conclusão:** os cenários de `validacao.md` passam no runtime-alvo Python 3.12.

## 5. Documentar

- [ ] Atualizar o README para incluir a ferramenta e um exemplo de chamada.
- [ ] Registrar qualquer desvio de contrato antes de incorporá-lo à implementação.

**Conclusão:** a instalação, execução e demonstração da nova ferramenta estão documentadas.

## Ordem

Não avançar para a Fase 3 antes de concluir esta fase e registrar os resultados da validação.
