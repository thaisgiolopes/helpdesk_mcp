# Helpdesk MCP

Servidor MCP local para consultar e atualizar chamados fictícios armazenados em SQLite. Esta implementação cobre as três fases do roadmap: `listar_chamados`, `buscar_historico_cliente` e `atualizar_status`.

## Requisitos

- Python 3.12.
- `pip`.

## Instalação e execução

Na raiz do repositório, crie e ative um ambiente virtual e instale as dependências fixadas:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Inicie o servidor MCP pelo transporte `stdio`:

```bash
python -m server
```

O processo fica aguardando mensagens MCP no terminal. Não digite comandos nesse terminal enquanto ele estiver rodando; encerre com `Ctrl+C`. A inicialização cria `data/helpdesk.db` e as tabelas se estiverem ausentes. Os registros fictícios iniciais são inseridos uma única vez e não são recriados ao reiniciar o servidor. Os dados existentes, inclusive alterações e exclusões dos registros iniciais, são preservados.

Para usar outro arquivo SQLite, defina `HELPDESK_DB_PATH` antes de iniciar o servidor:

```bash
HELPDESK_DB_PATH=/caminho/para/teste.db python -m server
```

O caminho padrão do banco é `data/helpdesk.db`, relativo à raiz do projeto.

## Ferramenta `listar_chamados`

- Sem argumento ou com `status: null`, retorna todos os chamados.
- Com `status`, filtra por um dos valores exatos: `aberto`, `em_atendimento`, `aguardando_cliente`, `resolvido` ou `fechado`.
- Status vazio, desconhecido ou com diferença de maiúsculas/minúsculas retorna erro de validação.
- Retorna os campos `id`, `cliente_id`, `descricao`, `status`, `created_at` e `updated_at`, ordenados por data de criação decrescente e, em caso de empate, por ID crescente.
- Uma consulta válida sem resultados retorna `[]`.

Exemplos de argumentos MCP:

```json
{}
```

```json
{"status": "aberto"}
```

## Ferramenta `buscar_historico_cliente`

- Recebe o argumento obrigatório `cliente_id`, que deve ser um inteiro positivo.
- Retorna os chamados daquele cliente com os mesmos campos e ordenação de `listar_chamados`.
- Para cliente existente sem chamados, retorna `[]`. Para cliente inexistente ou identificador inválido, retorna erro claro.
- Não retorna nome ou e-mail do cliente e não altera dados.

Exemplo de argumentos MCP:

```json
{"cliente_id": 1}
```

## Ferramenta `atualizar_status`

- Recebe `chamado_id` (inteiro positivo) e `novo_status` (um dos status permitidos, com correspondência exata).
- Em caso de sucesso, retorna o chamado atual com seus seis campos. Atualiza `status` e `updated_at` em uma transação e preserva os demais campos.
- Se o chamado já estiver no status solicitado, retorna sucesso sem alterar os dados nem `updated_at`.
- Para chamado inexistente ou argumentos inválidos, retorna erro claro. O status anterior não é mantido como histórico.

Exemplo de argumentos MCP:

```json
{"chamado_id": 1001, "novo_status": "em_atendimento"}
```

## Aplicação web para atendimento

A interface Streamlit funciona como cliente MCP: inicia o pacote `server` pelo transporte `stdio` e chama suas ferramentas. A aplicação nunca acessa o SQLite diretamente.

### Protótipo com comandos fixos

Esta versão interpreta padrões explícitos, sem modelo de linguagem. Inicie-a na raiz:

```bash
streamlit run app/streamlit_app.py
```

Comandos de exemplo:

- `listar abertos` → `listar_chamados` com `status: aberto`
- `histórico do cliente 2` → `buscar_historico_cliente` com `cliente_id: 2`
- `alterar chamado 1001 para fechado` → `atualizar_status` com `chamado_id: 1001` e `novo_status: fechado`

Os registros demonstrativos usam IDs de chamados de 1001 a 1006 e IDs de clientes de 1 a 3. Os status permitidos são `aberto`, `em_atendimento`, `aguardando_cliente`, `resolvido` e `fechado`. Um ID inexistente é encaminhado ao servidor MCP, que retorna o erro correspondente.

### Versão com perguntas livres e modelo local

Esta versão usa o Ollama e o modelo local `qwen3:4b` para selecionar uma ferramenta MCP a partir da pergunta em linguagem natural. Não é necessário configurar uma chave ou chamar uma API paga. Instale e inicie o Ollama conforme as [instruções oficiais](https://ollama.com/download), baixe o modelo e execute a aplicação:

```bash
ollama pull qwen3:4b
streamlit run app/streamlit_app_ia.py
```

O endereço do Ollama pode ser configurado em `OLLAMA_HOST` e o modelo em `HELPDESK_LLM_MODEL`. Por padrão, a aplicação usa `http://localhost:11434` e `qwen3:4b`. O modelo recebe os schemas MCP descobertos do servidor, mas a execução das operações continua passando pelo cliente MCP via `stdio`.

Antes de executar `atualizar_status`, a interface mostra o chamado e o status propostos e aguarda o botão **Confirmar atualização**. O atendente também pode cancelar; até confirmar, nenhuma alteração é enviada ao servidor.

| Protótipo com comandos fixos | Versão com modelo local |
|---|---|
| Reconhece frases previstas, como `listar abertos` | Interpreta perguntas livres, como “Quais chamados ainda precisam de atendimento?” |
| Resposta previsível e sem dependência de modelo | Mais flexível, mas depende do Ollama e do modelo instalado localmente |
| Não exige serviço de IA | Não exige API paga nem envia a pergunta para um serviço externo |

As duas versões mantêm o histórico na sessão do Streamlit. As datas permanecem armazenadas em UTC no SQLite e são convertidas para o fuso `America/Sao_Paulo` (Brasília) na apresentação.

## Registrar no VS Code

O workspace já inclui `.vscode/mcp.json`, que registra o servidor usando o Python do ambiente virtual e o transporte `stdio`. Depois de criar `.venv` e instalar as dependências:

1. Abra a raiz deste repositório no VS Code.
2. Abra o arquivo `.vscode/mcp.json` para conferir a configuração `helpdesk`.
3. Na Paleta de Comandos, execute **MCP: List Servers** ou **MCP: Open Workspace Folder MCP Configuration** e inicie/reinicie `helpdesk` se necessário.
4. No chat do Copilot, habilite as três ferramentas e peça uma consulta ou atualização, por exemplo: “Liste os chamados em atendimento”, “Mostre o histórico do cliente 1” ou “Atualize o chamado 1001 para em atendimento”.

Para registrar manualmente em outro workspace, execute **MCP: Add Server**, escolha **Command (stdio)** e informe o caminho absoluto para `.venv/bin/python` como comando e `-m server` como argumentos. No Windows, use o executável `.venv\\Scripts\\python.exe`. O VS Code mantém as configurações por workspace em `.vscode/mcp.json`; a documentação atual também descreve o formato portátil `.mcp.json`, que usa a chave superior `mcpServers` em vez de `servers`.

## Testes

Com Python 3.12 e o ambiente virtual ativo, execute a suíte:

```bash
python -m pytest -q
```

Os testes usam bancos temporários isolados. Para executar os grupos separadamente:

```bash
python -m pytest -q tests/test_mcp_tool.py -k "not stdio"  # descoberta e chamada das tools por cliente MCP em processo
python -m pytest -q tests/test_cliente_history.py            # histórico e erros de cliente
python -m pytest -q tests/test_status_update.py              # atualização, persistência e erros
```

`tests/test_database.py` cobre esquema, dados iniciais e listagem. `tests/test_mcp_tool.py` também contém o cenário de subprocesso via `stdio`, incluído na suíte completa.

### Demonstração da chamada da interface

A interface inicia o servidor como processo filho, conecta `fastmcp.Client` por `stdio` e envia a tool selecionada. Para manter a demonstração isolada do banco de desenvolvimento, inicie-a assim:

```bash
HELPDESK_DB_PATH=/tmp/helpdesk-streamlit.db streamlit run app/streamlit_app.py
```

Digite `listar abertos`; a resposta esperada contém os chamados fictícios `1001` e `1006`. Também é possível experimentar `histórico do cliente 2` e `alterar chamado 1001 para fechado` (esta última pede confirmação na versão com IA local).

**Resultado de validação disponível:** a chamada real via `stdio` foi tentada a partir da função `chamar_tool` usada pela aplicação, mas não completou a negociação MCP com Python 3.14.4 (`initialize` expirou). O runtime-alvo documentado é Python 3.12 e não está instalado neste ambiente; por isso, a chamada real da UI ainda precisa ser confirmada em Python 3.12. A suíte executada em Python 3.14.4 teve 47 aprovações e uma falha no mesmo cenário `stdio`. Não considere o critério de integração da UI aprovado até repetir essa validação no runtime-alvo.

## Constituição, especificações e histórico SDD

As decisões gerais ficam em `specs/missao.md` e `specs/pilha-tecnologia.md`. Cada fase MCP tem `requisitos.md`, `planejamento.md` e `validacao.md` em sua pasta. O histórico Git registra as especificações antes da implementação (por exemplo, `2eb1402` antes de `8208641`, `b21c5d5` antes de `a5de24f` e `88113fd` antes de `f1eff7a`). Confira com:

```bash
git log --all --reverse --oneline
```

O protótipo Streamlit é uma demonstração adicional, mantida em `app/` e fora do processo SDD das três fases MCP.

## Link do repositório
https://github.com/thaisgiolopes/helpdesk_mcp.git