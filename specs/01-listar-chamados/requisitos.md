# Requisitos — Listar chamados

## 1. Objetivo
Definir o comportamento da ferramenta MCP `listar_chamados`, que consulta os chamados armazenados no SQLite e permite, opcionalmente, filtrar os resultados pelo status.

## 2. Escopo
Esta funcionalidade corresponde à Fase 1 do roadmap. Ela realiza apenas consultas: não cria, altera nem remove chamados. A implementação deverá seguir `specs/missao.md`, `specs/pilha-tecnologia.md` e `specs/roadmap.md`.

## 3. Entrada
A ferramenta aceita um parâmetro opcional `status` (`string` ou ausente/nulo).

Valores aceitos:
- `aberto`
- `em_atendimento`
- `aguardando_cliente`
- `resolvido`
- `fechado`

Essa é a lista canônica de status permitidos definida em `specs/pilha-tecnologia.md`. A validação da ferramenta e a restrição `CHECK` do SQLite devem usar os mesmos valores. Qualquer mudança exige atualizar a Constituição, as especificações e os testes antes de alterar a implementação ou o esquema.

Regras:
- `status` omitido ou nulo: listar chamados de todos os status.
- Status válido: retornar somente chamados com esse status.
- String vazia, apenas espaços ou status desconhecido: retornar erro de validação claro; não interpretar como ausência de filtro.
- Nesta versão, os valores são exatos e diferenciam maiúsculas de minúsculas.

## 4. Saída
Em caso de sucesso, retornar uma lista de chamados. Cada item deve conter:
- `id`: identificador do chamado;
- `cliente_id`: identificador do cliente;
- `descricao`: descrição do problema ou solicitação;
- `status`: status atual;
- `created_at`: data e hora de criação;
- `updated_at`: data e hora da última atualização.

Ordenação determinística: chamados mais recentes primeiro por `created_at`; em caso de empate, `id` crescente.

Se nenhum chamado corresponder à consulta, retornar uma lista vazia (`[]`). Isso é uma consulta bem-sucedida sem correspondências, não um erro. Falhas reais de banco não devem ser mascaradas como lista vazia.

## 5. Comportamentos esperados
1. Sem filtro, retornar todos os chamados existentes.
2. Com status válido, retornar somente chamados daquele status.
3. A consulta não altera os dados armazenados.
4. Banco sem chamados: retornar `[]`.
5. Nenhum chamado com o status solicitado: retornar `[]`.
6. Status inválido: erro de validação claro.
7. A ferramenta não deve reinicializar os dados fictícios a cada chamada. A inicialização pertence à preparação do banco/servidor.

## 6. Inicialização e dados fictícios
O banco e as tabelas devem ser criados automaticamente quando ainda não existirem. Na primeira inicialização, inserir dados fictícios suficientes para demonstrar a listagem geral e o filtro por status, com vários chamados, mais de um cliente e mais de um status.

A inicialização deve ser idempotente:
- execuções posteriores não duplicam os registros iniciais;
- dados alterados durante o uso não são apagados;
- o banco não é recriado a cada chamada da ferramenta;
- testes podem usar banco temporário isolado.

Os registros iniciais devem ter identificadores estáveis ou outro mecanismo explícito de identificação para evitar duplicação.

## 7. Fora do escopo
- Consultar histórico de um cliente específico (fase 2).
- Atualizar status (fase 3).
- Paginação, ordenação configurável e busca textual.
- Autenticação de produção ou integração com sistemas externos.
