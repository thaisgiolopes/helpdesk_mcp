# Requisitos — Atualizar status

## 1. Objetivo

Definir o comportamento da ferramenta MCP `atualizar_status`, que altera o status atual de um chamado existente no SQLite.

## 2. Escopo

Esta funcionalidade corresponde à Fase 3 do roadmap. Ela atualiza o estado atual do chamado e sua data de atualização, sem alterar sua identidade, seu cliente, sua descrição ou sua data de criação.

O modelo não registra transições de status. Uma mudança substitui o status anterior, que não poderá ser recuperado pela aplicação. Registrar auditoria de transições exigiria especificação e alteração do escopo e do esquema.

## 3. Entrada

A ferramenta recebe os parâmetros obrigatórios:

- `chamado_id`: identificador inteiro positivo do chamado;
- `novo_status`: string que corresponda exatamente a um dos status canônicos: `aberto`, `em_atendimento`, `aguardando_cliente`, `resolvido` ou `fechado`.

Regras:
- Parâmetros ausentes ou nulos são inválidos.
- `chamado_id` deve ser inteiro positivo. Booleanos, strings, números fracionários, zero e valores negativos são inválidos e não devem ser convertidos implicitamente.
- `novo_status` diferencia maiúsculas de minúsculas. String vazia, espaços, variações de caixa e valores desconhecidos são inválidos.
- Um `chamado_id` válido que não exista no banco é um erro de domínio claro; não deve ser tratado como sucesso sem alteração nem criar um chamado.

## 4. Saída

Em caso de sucesso, retornar o chamado atual após a operação, como objeto com os campos:

- `id`;
- `cliente_id`;
- `descricao`;
- `status`;
- `created_at`;
- `updated_at`.

Quando houver mudança de status, `updated_at` representa o instante da mudança em UTC no formato `YYYY-MM-DDTHH:MM:SSZ`. Os demais campos do chamado permanecem iguais.

Quando `novo_status` já for o status atual, a operação é um sucesso idempotente sem alteração. Retorna o chamado atual e mantém `updated_at` inalterado.

Chamado inexistente, parâmetros inválidos e falha real do banco são erros da ferramenta, não resultados de sucesso.

## 5. Comportamentos esperados

1. Chamado existente e novo status válido diferente do atual: atualizar `status` e `updated_at`, então retornar o chamado atualizado.
2. Chamado existente e novo status igual ao atual: retornar sucesso sem modificar qualquer campo.
3. Chamado inexistente: retornar erro claro e não inserir nem alterar registros.
4. Identificador ou status inválido: retornar erro de validação claro e não alterar registros.
5. A operação deve ser atômica: ou a mudança e o novo `updated_at` são persistidos juntos, ou o estado anterior permanece integralmente intacto.
6. Preservar `id`, `cliente_id`, `descricao` e `created_at` em toda atualização.
7. Não criar nem popular uma tabela de histórico de transições nesta fase.
8. Falhas reais do SQLite não devem ser convertidas em sucesso, chamado inexistente ou status inválido.

## 6. Compatibilidade com o modelo de dados

Usar a tabela `chamados` e a restrição `CHECK` existentes. Não é necessária mudança de esquema para esta funcionalidade. O conjunto de status é o definido como canônico em `specs/pilha-tecnologia.md`.

## 7. Fora do escopo

- Consultar ou reconstruir status anteriores.
- Registrar usuário, motivo ou evento da alteração.
- Atualizar descrição, cliente ou outros campos do chamado.
- Criar chamados inexistentes.
- Notificações, autorização de produção ou integração externa.
