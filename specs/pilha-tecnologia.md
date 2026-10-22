# Pilha tecnológica — Helpdesk MCP

## 1. Objetivo

Definir as tecnologias, restrições arquiteturais e decisões técnicas que orientarão o desenvolvimento do Helpdesk MCP, seguindo a abordagem Spec-Driven Development (SDD).

## 2. Decisões obrigatórias

### 2.1. Linguagem e dependências

- Implementar o projeto em Python.
- Utilizar ambiente virtual para isolar as dependências.
- Documentar as dependências em `requirements.txt`, com versões fixadas para permitir a reprodução da instalação.
- Utilizar Python 3.12 como versão-alvo inicial, validando sua compatibilidade com as dependências escolhidas.
- Documentar os comandos de instalação, ativação do ambiente e execução no README.

### 2.2. Servidor MCP

- Utilizar o pacote independente `fastmcp` para implementar o servidor e registrar as ferramentas.
- Expor as ferramentas `listar_chamados`, `buscar_historico_cliente` e `atualizar_status`.
- Utilizar transporte MCP `stdio`.
- Manter as mensagens de diagnóstico fora de `stdout`, utilizando `stderr` quando necessário.
- Definir parâmetros, retornos, validações e erros nas especificações funcionais antes da implementação.

### 2.3. Banco de dados

- Utilizar SQLite com a biblioteca padrão `sqlite3`.
- Armazenar o banco em `data/helpdesk.db`, utilizando um caminho consistente e independente do diretório de onde o comando for executado.
- Criar automaticamente o diretório de dados, o arquivo do banco e as tabelas necessárias.
- Inserir dados fictícios quando o banco ainda não possuir os registros iniciais.
- Evitar duplicações de registros iniciais em execuções posteriores.
- Preservar dados e alterações existentes durante a inicialização normal.
- Utilizar transações nas operações que modificam os dados.

### 2.4. Modelo de dados proposto

A proposta inicial utiliza duas tabelas:

**clientes**
- `id`: chave primária.
- `nome`: nome fictício.
- `email`: endereço fictício, quando necessário.

**chamados**
- `id`: chave primária.
- `cliente_id`: chave estrangeira para `clientes.id`.
- `descricao`: descrição do problema ou solicitação.
- `status`: situação atual do chamado.
- `created_at`: data e hora de criação.
- `updated_at`: data e hora da última atualização.

Os campos de data e hora usam o formato UTC `YYYY-MM-DDTHH:MM:SSZ`, com precisão de segundos e representação consistente para permitir ordenação textual determinística. Uma atualização de status deverá gravar o novo `updated_at` na mesma transação que altera o status.

O relacionamento será de um para muitos entre clientes e chamados. A chave estrangeira deverá ser aplicada com as restrições de integridade apropriadas.

O esquema atual é suficiente para as Fases 2 e 3: a busca de histórico consulta `chamados` pelo `cliente_id` relacionado a `clientes`, e a atualização altera o `status` e `updated_at` do chamado existente. Essas fases não exigem uma nova tabela nem mudança de esquema dentro do escopo definido. Uma tabela adicional só deverá ser proposta se o produto passar a exigir o registro de transições de status.

Os status inicialmente propostos são `aberto`, `em_atendimento`, `aguardando_cliente`, `resolvido` e `fechado`. A lista definitiva deverá ser registrada na especificação funcional antes da implementação.

O histórico de um cliente significa a consulta dos chamados vinculados a ele, ordenados por data de criação decrescente e, em caso de empate, por ID crescente. Isso não representa um log das transições de status. O registro de todas as transições não faz parte das três fases do roadmap; uma necessidade futura deverá ser especificada antes de alterar o modelo de dados.

### 2.5. Arquitetura proposta

A implementação deverá separar:

- `server.py`: registro das ferramentas e inicialização do servidor MCP.
- `database.py`: conexão com SQLite e operações de persistência.
- `seed.py`: inicialização idempotente dos dados fictícios.
- `tests/`: testes automatizados das operações e da integração MCP.

A estrutura poderá ser ajustada mediante justificativa documentada, desde que as responsabilidades permaneçam separadas.

### 2.6. Testes e reprodutibilidade

- Utilizar `pytest` para os testes automatizados.
- Testar as operações de persistência separadamente da comunicação MCP.
- Verificar as três ferramentas por meio de um cliente MCP.
- Testar dados inexistentes, parâmetros inválidos e preservação das alterações.
- Utilizar bancos temporários nos testes, evitando modificar os dados de desenvolvimento.
- Não versionar o banco SQLite gerado nem incluir credenciais ou dados sensíveis no repositório.

## 3. Dependências e compatibilidade

O projeto utilizará o pacote `fastmcp` e, para os testes, `pytest`.

Antes da implementação, deverão ser verificadas as versões compatíveis com Python 3.12. As versões efetivamente selecionadas deverão ser fixadas em `requirements.txt`.

A biblioteca `sqlite3` faz parte da biblioteca padrão do Python e não precisa ser instalada separadamente.

## 4. Inicialização do banco

A inicialização deverá ser idempotente: executar o processo mais de uma vez não deverá duplicar os registros fictícios nem apagar os dados modificados pelo usuário.

Os registros iniciais deverão ter identificadores ou critérios de identificação estáveis que permitam reconhecer quais dados já foram inseridos.

A inicialização deverá criar a estrutura ausente sem recriar indiscriminadamente tabelas que já contenham dados.

## 5. Limites

- Execução local.
- Dados exclusivamente fictícios.
- Ausência de autenticação real.
- Ausência de integração com serviços externos de atendimento.
- Sem exigência de modelo de linguagem ou chave de API para demonstrar as ferramentas MCP.
- Interface Streamlit desenvolvida separadamente, na segunda etapa do projeto.

## 6. Critérios de aceitação

- [ ] O ambiente Python pode ser reproduzido seguindo as instruções do README.
- [ ] O servidor utiliza `fastmcp` e transporte `stdio`.
- [ ] As três ferramentas MCP estão registradas com contratos documentados.
- [ ] O SQLite e as tabelas são criados automaticamente quando necessário.
- [ ] Os dados fictícios são inseridos sem duplicação indiscriminada.
- [ ] Os chamados possuem identificação, cliente, descrição, status e datas.
- [ ] O histórico de um cliente retorna seus chamados relacionados.
- [ ] A atualização de status valida os valores permitidos e preserva a integridade dos dados.
- [ ] Os testes verificam os comportamentos esperados e os casos de erro.
- [ ] O README permite que outra pessoa instale, execute e teste o projeto.
- [ ] A futura aplicação Streamlit realizará pelo menos uma chamada real ao servidor MCP.

## 7. Controle das decisões

As decisões obrigatórias deste documento não deverão ser substituídas silenciosamente.

Mudanças no esquema do banco, nos contratos das ferramentas, nas dependências ou no transporte deverão ser justificadas e refletidas nas especificações antes da implementação correspondente.

As especificações funcionais serão a referência para os comportamentos esperados, enquanto este documento estabelecerá as restrições tecnológicas do projeto.
