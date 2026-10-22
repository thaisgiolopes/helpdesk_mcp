# Requisitos — Buscar histórico de cliente

## 1. Objetivo

Definir o comportamento da ferramenta MCP `buscar_historico_cliente`, que consulta os chamados associados a um cliente existente no SQLite.

## 2. Escopo

Esta funcionalidade corresponde à Fase 2 do roadmap. É uma consulta somente leitura: não cria, altera nem remove clientes ou chamados.

Nesta fase, “histórico do cliente” significa a lista dos chamados vinculados ao cliente. Não significa um log das transições de status. A ferramenta não filtra por status, não busca texto, não pagina resultados e não retorna dados pessoais do cliente além do identificador presente em cada chamado.

## 3. Entrada

A ferramenta recebe o parâmetro obrigatório `cliente_id`, identificador inteiro positivo de um cliente existente.

Regras:
- O parâmetro é obrigatório e não pode ser nulo.
- Valores inteiros menores que 1 são inválidos.
- Valores de outro tipo, incluindo string, número fracionário e booleano, são inválidos; não devem ser convertidos implicitamente.
- Um identificador positivo que não corresponda a um cliente cadastrado é um erro de domínio claro, não uma consulta sem resultados.

## 4. Saída

Para um cliente existente, retornar uma lista dos chamados cujo `cliente_id` corresponde ao argumento. Cada item contém os campos definidos para um chamado em `specs/01-listar-chamados/requisitos.md`:

- `id`;
- `cliente_id`;
- `descricao`;
- `status`;
- `created_at`;
- `updated_at`.

A ordenação é determinística: `created_at` decrescente e, em caso de empate, `id` crescente.

Um cliente existente sem chamados associados retorna `[]`, sem erro. A ferramenta não retorna o nome, o e-mail ou outros atributos da tabela `clientes`.

## 5. Comportamentos esperados

1. Cliente existente com chamados: retornar somente os chamados daquele cliente.
2. Cliente existente sem chamados: retornar `[]` como resultado bem-sucedido.
3. Cliente inexistente: retornar erro claro indicando que o cliente não foi encontrado.
4. `cliente_id` ausente, nulo, não inteiro ou menor que 1: retornar erro de validação claro.
5. Chamados de outros clientes nunca aparecem no resultado.
6. A consulta não altera os dados armazenados.
7. Falhas reais do SQLite não devem ser mascaradas como `[]` nem como cliente inexistente.
8. A ferramenta não reinicializa o banco nem repopula dados fictícios durante a chamada.

## 6. Compatibilidade com o modelo de dados

A implementação utiliza as tabelas `clientes` e `chamados` já criadas na Fase 1. A relação `chamados.cliente_id` para `clientes.id` identifica os registros do histórico. Não é necessária alteração de esquema nesta fase.

## 7. Fora do escopo

- Registrar transições ou eventos de status.
- Filtrar o histórico por status ou período.
- Paginação, ordenação configurável ou busca textual.
- Consultar cliente por nome ou e-mail.
- Alterar dados do cliente ou dos chamados.
