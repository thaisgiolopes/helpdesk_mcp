# Planejamento — Buscar histórico de cliente

## Objetivo

Implementar `buscar_historico_cliente` de acordo com `requisitos.md`, separando a consulta SQLite do registro da ferramenta MCP.

## 1. Confirmar o contrato

- [x] Confirmar `cliente_id` obrigatório como inteiro positivo, sem conversão implícita.
- [x] Distinguir cliente existente sem chamados (`[]`) de cliente inexistente (erro claro).
- [x] Reutilizar os campos e a ordenação definidos para os chamados.
- [x] Confirmar que histórico significa lista de chamados, sem log de transições.

**Conclusão:** entrada, saída, erros e limites estão definidos antes da implementação.

## 2. Preparar a consulta SQLite

- [x] Reutilizar as funções de conexão e o caminho de banco definidos na Fase 1.
- [x] Consultar chamados por `cliente_id` com parâmetros SQL vinculados.
- [x] Verificar a existência do cliente para diferenciar cliente inexistente de cliente sem chamados.
- [x] Ordenar por `created_at` decrescente e `id` crescente em caso de empate.
- [x] Manter a operação somente leitura e propagar falhas reais do banco.

**Conclusão:** a persistência retorna apenas o histórico do cliente solicitado, sem alterar os dados.

## 3. Implementar a tool MCP

- [x] Registrar `buscar_historico_cliente` no servidor FastMCP.
- [x] Validar o parâmetro obrigatório e rejeitar valores inválidos sem coerção.
- [x] Retornar os chamados no formato definido em `requisitos.md`.
- [x] Retornar lista vazia para cliente existente sem chamados.
- [x] Retornar erro claro para cliente inexistente.
- [x] Manter mensagens de diagnóstico fora de `stdout` para preservar o transporte `stdio`.

**Conclusão:** a ferramenta está descoberta e aplica o contrato funcional.

## 4. Testar

- [x] Testar clientes com chamados, incluindo cliente com mais de um chamado.
- [x] Testar cliente existente sem chamados.
- [x] Testar cliente inexistente.
- [x] Testar parâmetro ausente, nulo, booleano, string, fracionário, zero e negativo.
- [x] Verificar os campos, a ordenação e a exclusão de chamados de outros clientes.
- [x] Comparar os dados antes e depois da consulta.
- [x] Simular falha real do SQLite e confirmar que não é convertida em lista vazia.
- [x] Testar descoberta e invocação por cliente MCP em processo.
- [x] Confirmar que os testes usam banco temporário isolado.
- [ ] Repetir H14 com cliente MCP via `stdio` usando Python 3.12.

**Conclusão:** contrato, persistência e chamada MCP em processo foram implementados e passaram nos testes disponíveis. O H14 via `stdio` permanece pendente de execução no runtime-alvo Python 3.12; o resultado disponível está em `validacao.md`.

## 5. Documentar

- [x] Atualizar o README para incluir a ferramenta e um exemplo de chamada.
- [x] Registrar qualquer desvio de contrato antes de incorporá-lo à implementação.

**Conclusão:** a instalação, execução e demonstração da nova ferramenta estão documentadas.

## Ordem

Não avançar para a Fase 3 antes de concluir esta fase e registrar os resultados da validação.
