# Helpdesk MCP

Servidor MCP local para consultar chamados fictícios armazenados em SQLite. Esta implementação cobre **somente a Fase 1** do roadmap: a ferramenta `listar_chamados`.

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
python server.py
```

O processo fica aguardando mensagens MCP no terminal. Não digite comandos nesse terminal enquanto ele estiver rodando; encerre com `Ctrl+C`. A inicialização cria `data/helpdesk.db` e as tabelas se estiverem ausentes. Os registros fictícios iniciais são inseridos uma única vez e não são recriados ao reiniciar o servidor. Os dados existentes, inclusive alterações e exclusões dos registros iniciais, são preservados.

Para usar outro arquivo SQLite, defina `HELPDESK_DB_PATH` antes de iniciar o servidor:

```bash
HELPDESK_DB_PATH=/caminho/para/teste.db python server.py
```

O caminho padrão do banco é relativo ao diretório do projeto, independentemente do diretório de onde `server.py` é iniciado.

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

## Registrar no VS Code

O workspace já inclui `.vscode/mcp.json`, que registra o servidor usando o Python do ambiente virtual e o transporte `stdio`. Depois de criar `.venv` e instalar as dependências:

1. Abra a raiz deste repositório no VS Code.
2. Abra o arquivo `.vscode/mcp.json` para conferir a configuração `helpdesk`.
3. Na Paleta de Comandos, execute **MCP: List Servers** ou **MCP: Open Workspace Folder MCP Configuration** e inicie/reinicie `helpdesk` se necessário.
4. No chat do Copilot, habilite a ferramenta `listar_chamados` e peça uma listagem, por exemplo: “Liste os chamados em atendimento”.

Para registrar manualmente em outro workspace, execute **MCP: Add Server**, escolha **Command (stdio)** e informe o caminho absoluto para `.venv/bin/python` como comando e o caminho absoluto para `server.py` como argumento. No Windows, use o executável `.venv\\Scripts\\python.exe`. O VS Code mantém as configurações por workspace em `.vscode/mcp.json`; a documentação atual também descreve o formato portátil `.mcp.json`, que usa a chave superior `mcpServers` em vez de `servers`.

## Testes

Com o ambiente virtual ativo, execute:

```bash
pytest
```

Os testes usam bancos temporários isolados. A suíte cobre a persistência e a inicialização idempotente, verifica a descoberta da ferramenta por um cliente FastMCP e exercita o contrato da ferramenta. Há também um teste de invocação via `stdio`, executado com o runtime-alvo Python 3.12.
