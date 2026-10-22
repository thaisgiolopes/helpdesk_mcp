# Planejamento — Listar chamados

## Objetivo
Implementar `listar_chamados` em tarefas pequenas, rastreáveis aos requisitos e verificáveis por testes.

## 1. Confirmar o contrato
- [x] Confirmar os campos retornados.
- [x] Registrar os status aceitos: `aberto`, `em_atendimento`, `aguardando_cliente`, `resolvido` e `fechado`.
- [x] Confirmar que status omitido/nulo significa sem filtro e status vazio/desconhecido é inválido.
- [x] Confirmar o retorno `[]` quando não houver correspondências.

**Conclusão:** contrato documentado e coerente com missão, pilha tecnológica e roadmap.

## 2. Preparar a consulta SQLite
- [x] Reutilizar a conexão definida na arquitetura.
- [x] Usar o caminho do banco definido na pilha tecnológica, independentemente do diretório de execução.
- [x] Usar consultas parametrizadas.
- [x] Definir ordenação determinística.

**Conclusão:** a camada de persistência consulta todos os chamados ou filtra por status sem alterar os dados.

## 3. Preparar a inicialização fictícia
- [x] Criar automaticamente diretório, banco e tabelas quando ausentes.
- [x] Inserir registros fictícios suficientes para demonstrar a ferramenta.
- [x] Tornar a inicialização idempotente.
- [x] Verificar que execuções repetidas não duplicam os registros iniciais nem apagam alterações existentes.

**Conclusão:** um ambiente novo fica pronto para demonstração e inicializações posteriores preservam os dados.

## 4. Implementar a tool MCP
- [x] Registrar `listar_chamados` no FastMCP.
- [x] Implementar o parâmetro opcional `status`.
- [x] Validar o status antes da consulta.
- [x] Retornar os campos definidos em `requisitos.md`.
- [x] Retornar `[]` quando não houver correspondências.
- [x] Manter mensagens de diagnóstico fora de `stdout` para não interferir no transporte `stdio`.

**Conclusão:** a ferramenta está registrada e respeita o contrato funcional.

## 5. Testar
- [x] Testar consulta sem filtro.
- [x] Testar cada status aceito.
- [x] Testar status inválido e string vazia.
- [x] Testar banco sem chamados e filtro sem correspondências.
- [x] Verificar que a consulta não altera registros.
- [x] Testar inicialização repetida.
- [x] Testar a ferramenta por cliente MCP em processo, além dos testes da persistência.
- [ ] Repetir V14 com cliente MCP via `stdio` usando Python 3.12; registrar o resultado em `validacao.md`.

**Conclusão:** implementação e testes funcionais concluídos. A execução e a pendência do cenário V14 estão registradas em `validacao.md`.

## 6. Documentar
- [x] Atualizar o README com instruções para iniciar o servidor e testar a ferramenta.
- [x] Incluir exemplos sem filtro e com filtro.
- [x] Documentar decisões ou desvios antes de incorporá-los ao código.

**Conclusão:** outra pessoa consegue reproduzir e demonstrar a funcionalidade.

## Ordem
Executar as tarefas na ordem apresentada. Não avançar para a fase 2 antes de concluir e verificar esta funcionalidade.
