# Helpdesk MCP

Servidor MCP para operações sobre chamados de uma equipe de suporte técnico.

## Objetivo

O projeto tem como objetivo desenvolver um servidor baseado no **Model Context Protocol (MCP)** para disponibilizar ferramentas que permitam a agentes de IA e aplicações clientes consultar e atualizar chamados de suporte técnico.

Os dados serão armazenados localmente em um banco SQLite, inicializado com registros fictícios para permitir a execução e os testes do projeto sem depender de serviços externos.

## Funcionalidades previstas

O servidor disponibilizará três ferramentas MCP:

1. **Listar chamados:** consultar os chamados registrados, com a possibilidade de filtrar os resultados por status.
2. **Consultar histórico de um cliente:** recuperar os chamados associados a um cliente específico.
3. **Atualizar status de um chamado:** modificar o status de um chamado existente, respeitando as regras definidas para a operação.

O servidor será responsável pelas operações sobre os dados. A interface destinada à interação com o usuário será desenvolvida separadamente, em uma aplicação Streamlit que utilizará o servidor MCP.

## Desenvolvimento orientado por especificações

O projeto utilizará a abordagem *Spec-Driven Development* (SDD), na qual os requisitos e as regras esperadas são documentados antes da implementação das funcionalidades.

As especificações serão mantidas no diretório `specs/` e servirão como referência para o planejamento, a implementação e a verificação do comportamento do sistema.

## Escopo e limitações

- Utilização de dados exclusivamente fictícios.
- Execução local, com armazenamento em SQLite.
- Ausência de autenticação real e de integração com sistemas externos de atendimento.
- Finalidade didática, sem pretensão de utilização em um ambiente de produção.

## Estado do projeto

O repositório está na etapa inicial de definição da missão e das especificações. As funcionalidades serão implementadas e testadas nas próximas etapas.

## Tecnologias previstas

- Python
- Model Context Protocol (MCP)
- SQLite
- Streamlit, na etapa de desenvolvimento da interface
