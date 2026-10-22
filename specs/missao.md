# Missão - Helpdesk MCP

## 1. Propósito

O Helpdesk MCP tem como propósito disponibilizar operações sobre chamados de clientes por meio de um servidor compatível com o Model Context Protocol (MCP).

O projeto busca demonstrar como agentes de inteligência artificial e aplicações clientes podem acessar dados estruturados e executar operações controladas por meio de ferramentas MCP.

O problema abordado é a necessidade de consultar informações de chamados, recuperar o histórico de atendimento de clientes e atualizar o status dos registros de forma organizada e verificável.

## 2. Público-alvo

As ferramentas do servidor serão utilizadas por agentes de inteligência artificial e aplicações clientes compatíveis com MCP.

Esses clientes poderão solicitar operações sobre os chamados sem precisar implementar diretamente a lógica de acesso ao banco de dados.

O servidor será responsável por receber os argumentos das ferramentas, executar as operações correspondentes e retornar os resultados ao cliente.

O atendente interage com o protótipo Streamlit em `app/`, que funciona como cliente MCP separado. O código do servidor e a interface não compartilham acesso direto ao SQLite.

## 3. Escopo inicial

A versão inicial deverá disponibilizar três ferramentas MCP:

### 3.1. Listar chamados

Permitir a consulta dos chamados registrados no banco de dados, com suporte à filtragem por status.

### 3.2. Consultar histórico de um cliente

Permitir a recuperação dos chamados associados a um cliente identificado por seu identificador no sistema.

### 3.3. Atualizar status de um chamado

Permitir a atualização do status de um chamado existente, mediante identificação do registro e fornecimento do novo status.

As regras detalhadas, os parâmetros, os retornos e os comportamentos em caso de erro serão definidos nas especificações individuais das funcionalidades.

## 4. Dados e armazenamento

Os dados serão armazenados em um banco SQLite local.

O projeto incluirá um mecanismo de inicialização do banco com dados fictícios, permitindo que outra pessoa reproduza a execução e teste as ferramentas sem precisar cadastrar manualmente todos os registros.

Não serão utilizados dados reais de clientes.

## 5. Limites do projeto

O projeto possui finalidade didática e apresenta as seguintes limitações:

- A execução será local, sem necessidade de uma infraestrutura de produção.
- Os registros serão fictícios e destinados exclusivamente a testes e demonstrações.
- Não haverá autenticação real, gerenciamento de usuários ou controle de acesso de produção.
- Não haverá integração com sistemas externos de atendimento ou plataformas comerciais de helpdesk.
- O servidor disponibilizará operações sobre os dados, mas não será responsável pela interface gráfica destinada ao atendente.
- A aplicação Streamlit é um cliente separado e deverá demonstrar uma chamada real ao servidor MCP; a validação ponta a ponta via `stdio` continua pendente no runtime-alvo.

## 6. Princípios de desenvolvimento

O desenvolvimento seguirá os seguintes princípios:

- **Especificação antes da implementação:** os comportamentos esperados serão documentados antes da escrita do código correspondente.
- **Separação de responsabilidades:** o servidor MCP, o armazenamento de dados e a interface Streamlit terão responsabilidades distintas.
- **Reprodutibilidade:** o repositório conterá as instruções e os recursos necessários para instalar, executar e testar o projeto.
- **Verificabilidade:** cada funcionalidade deverá possuir critérios que permitam conferir se a implementação atende à sua especificação.
- **Simplicidade didática:** as decisões técnicas deverão favorecer a compreensão do funcionamento do MCP e do processo SDD.
- **Protótipo de interface:** a aplicação Streamlit é uma demonstração adicional fora das três fases funcionais MCP e foi desenvolvida sem SDD, conforme o escopo solicitado para essa atividade.

## 7. Resultado esperado

Ao final do projeto, deverá ser possível executar localmente o servidor MCP, inicializar o banco SQLite com dados fictícios, demonstrar o funcionamento das três ferramentas e utilizar pelo menos uma delas por meio de uma chamada real realizada pela aplicação Streamlit.

O repositório também deverá documentar as especificações, as decisões de desenvolvimento e os testes realizados.
