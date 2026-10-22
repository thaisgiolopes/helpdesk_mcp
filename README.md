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

## Registrar no VS Code

O workspace já inclui `.vscode/mcp.json`, que registra o servidor usando o Python do ambiente virtual e o transporte `stdio`. Depois de criar `.venv` e instalar as dependências:

1. Abra a raiz deste repositório no VS Code.
2. Abra o arquivo `.vscode/mcp.json` para conferir a configuração `helpdesk`.
3. Na Paleta de Comandos, execute **MCP: List Servers** ou **MCP: Open Workspace Folder MCP Configuration** e inicie/reinicie `helpdesk` se necessário.
4. No chat do Copilot, habilite as três ferramentas e peça uma consulta ou atualização, por exemplo: “Liste os chamados em atendimento”, “Mostre o histórico do cliente 1” ou “Atualize o chamado 1001 para em atendimento”.

Para registrar manualmente em outro workspace, execute **MCP: Add Server**, escolha **Command (stdio)** e informe o caminho absoluto para `.venv/bin/python` como comando e o caminho absoluto para `server.py` como argumento. No Windows, use o executável `.venv\\Scripts\\python.exe`. O VS Code mantém as configurações por workspace em `.vscode/mcp.json`; a documentação atual também descreve o formato portátil `.mcp.json`, que usa a chave superior `mcpServers` em vez de `servers`.

## Testes

Com o ambiente virtual ativo, execute:

```bash
pytest
```

Os testes usam bancos temporários isolados. A suíte cobre a persistência, inicialização idempotente, consulta por cliente, atualização de status, validações, idempotência e preservação de dados. Também verifica as ferramentas por cliente MCP, incluindo invocação via `stdio` no runtime-alvo Python 3.12.
