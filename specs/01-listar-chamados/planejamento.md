# Planejamento — Listar chamados

## Objetivo
Implementar `listar_chamados` em tarefas pequenas, rastreáveis aos requisitos e verificáveis por testes.

## 1. Confirmar o contrato
- [ ] Confirmar os campos retornados.
- [ ] Registrar os status aceitos: `aberto`, `em_atendimento`, `aguardando_cliente`, `resolvido` e `fechado`.
- [ ] Confirmar que status omitido/nulo significa sem filtro e status vazio/desconhecido é inválido.
- [ ] Confirmar o retorno `[]` quando não houver correspondências.

**Conclusão:** contrato documentado e coerente com missão, pilha tecnológica e roadmap.

## 2. Preparar a consulta SQLite
- [ ] Reutilizar a conexão definida na arquitetura.
- [ ] Usar o caminho do banco definido na pilha tecnológica, independentemente do diretório de execução.
- [ ] Usar consultas parametrizadas.
- [ ] Definir ordenação determinística.

**Conclusão:** a camada de persistência consulta todos os chamados ou filtra por status sem alterar os dados.

## 3. Preparar a inicialização fictícia
- [ ] Criar automaticamente diretório, banco e tabelas quando ausentes.
- [ ] Inserir registros fictícios suficientes para demonstrar a ferramenta.
- [ ] Tornar a inicialização idempotente.
- [ ] Verificar que execuções repetidas não duplicam os registros iniciais nem apagam alterações existentes.

**Conclusão:** um ambiente novo fica pronto para demonstração e inicializações posteriores preservam os dados.

## 4. Implementar a tool MCP
- [ ] Registrar `listar_chamados` no FastMCP.
- [ ] Implementar o parâmetro opcional `status`.
- [ ] Validar o status antes da consulta.
- [ ] Retornar os campos definidos em `requisitos.md`.
- [ ] Retornar `[]` quando não houver correspondências.
- [ ] Manter mensagens de diagnóstico fora de `stdout` para não interferir no transporte `stdio`.

**Conclusão:** a ferramenta está registrada e respeita o contrato funcional.

## 5. Testar
- [ ] Testar consulta sem filtro.
- [ ] Testar cada status aceito.
- [ ] Testar status inválido e string vazia.
- [ ] Testar banco sem chamados e filtro sem correspondências.
- [ ] Verificar que a consulta não altera registros.
- [ ] Testar inicialização repetida.
- [ ] Testar a ferramenta por cliente MCP, além dos testes da persistência.

**Conclusão:** os cenários de `validacao.md` passam.

## 6. Documentar
- [ ] Atualizar o README com instruções para iniciar o servidor e testar a ferramenta.
- [ ] Incluir exemplos sem filtro e com filtro.
- [ ] Documentar decisões ou desvios antes de incorporá-los ao código.

**Conclusão:** outra pessoa consegue reproduzir e demonstrar a funcionalidade.

## Ordem
Executar as tarefas na ordem apresentada. Não avançar para a fase 2 antes de concluir e verificar esta funcionalidade.
