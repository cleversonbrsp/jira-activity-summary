# Jira Activity Summary

Automação Python que busca tarefas no Jira e gera resumos de atividade para liderança.

---

## Índice

1. [Visão geral](#1-visão-geral)
2. [Requisitos](#2-requisitos)
3. [Instalação](#3-instalação)
4. [Configuração](#4-configuração)
5. [Uso da CLI](#5-uso-da-cli)
6. [Opções da linha de comando](#6-opções-da-linha-de-comando)
7. [Uso como módulo Python](#7-uso-como-módulo-python)
8. [Formato do relatório](#8-formato-do-relatório)
9. [Estrutura do projeto](#9-estrutura-do-projeto)
10. [Integração com CI/CD](#10-integração-com-cicd)
11. [Licença](#11-licença)

---

## 1. Visão geral

O **Jira Activity Summary** conecta ao Jira via API REST, busca tarefas conforme critérios configuráveis (projeto, responsável, período ou JQL customizado) e gera um relatório em Markdown para **diretoria e liderança** com:

- Contagem total de itens por status
- Lista de tarefas **concluídas**, **em progresso**, **bloqueadas** e **pendentes**
- **Leitura e resumo do conteúdo** de cada task (descrição) — extrai o essencial em linguagem executiva
- Suporte a descrições em texto plano ou ADF (Atlassian Document Format)

O relatório é voltado para compartilhamento com diretoria em reuniões ou comunicações assíncronas.

---

## 2. Requisitos

- **Python** 3.10 ou superior
- **Conta Jira** (Atlassian Cloud ou Server/Data Center) com permissão de leitura
- **API Token** do Atlassian (substitui senha; mais seguro para automação)

---

## 3. Instalação

```bash
# Entre no diretório do projeto
cd jira-activity-summary

# Crie um ambiente virtual (recomendado)
python -m venv .venv

# Ative o ambiente virtual
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows

# Instale o pacote em modo editável
pip install -e .
```

Após a instalação, o comando `jira-summary` estará disponível. Se não ativar o ambiente virtual, use `.venv/bin/jira-summary`.

---

## 4. Configuração

### 4.1 Gerar o API Token

1. Acesse [Atlassian API Tokens](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Clique em **Create API token**
3. Dê um nome (ex.: `Jira Activity Summary`) e confirme
4. Copie o token e guarde em local seguro (ele não será mostrado novamente)

### 4.2 Arquivo `.env`

Copie o exemplo e edite com suas credenciais:

```bash
cp .env.example .env
```

Edite o `.env`:

```env
# Obrigatórias
JIRA_URL=https://sua-empresa.atlassian.net
JIRA_EMAIL=seu-email@empresa.com
JIRA_API_TOKEN=seu-token-api

# Opcionais (valores padrão)
JIRA_PROJECT=PROJ
JIRA_ASSIGNEE=me
JIRA_DAYS_BACK=7
```

| Variável           | Obrigatória | Descrição                                                                 |
|--------------------|-------------|---------------------------------------------------------------------------|
| `JIRA_URL`         | Sim         | URL base do Jira (ex: `https://minhaempresa.atlassian.net`)               |
| `JIRA_EMAIL`       | Sim         | E-mail da conta Atlassian                                                |
| `JIRA_API_TOKEN`   | Sim         | Token gerado em [API Tokens](https://id.atlassian.com/manage-profile/security/api-tokens) |
| `JIRA_PROJECT`     | Não         | Chave do projeto (ex: `PROJ`) para filtrar por padrão                    |
| `JIRA_ASSIGNEE`    | Não         | Responsável (`me` = tarefas atribuídas a você — padrão, nunca usa reporter) |
| `JIRA_DAYS_BACK`   | Não         | Quantidade de dias para trás (padrão: 7)                                |

> O arquivo `.env` não deve ser commitado (já está no `.gitignore`). Relatórios gerados (relatorio*.txt, report*.md, relatorios/, etc.) também estão ignorados.

---

## 5. Uso da CLI

### Execução básica

```bash
# Com ambiente virtual ativado
jira-summary

# Ou usando o caminho direto do venv
.venv/bin/jira-summary
```

O comando padrão:

- Usa as variáveis do `.env`
- **Foca em tarefas atribuídas a você** (`assignee = currentUser()`), não nas que você criou/abriu
- **Exclui sub-tasks** por padrão (mostra só tarefas principais)
- Considera itens atualizados nos últimos 7 dias
- Exibe o relatório em TXT no terminal (padrão)

### Salvar em arquivo

```bash
# TXT (padrão, ideal para enviar aos líderes)
jira-summary -o relatorio.txt

# Markdown
jira-summary --format markdown -o relatorio.md
```

---

## 6. Opções da linha de comando

| Opção | Forma curta | Descrição |
|-------|-------------|-----------|
| `--project` | `-p` | Chave do projeto (ex: `PROJ`) |
| `--assignee` | `-a` | Responsável (`me` ou e-mail) |
| `--jql` | `-q` | JQL customizado (sobrescreve projeto/assignee/days) |
| `--days` | | Número de dias para trás (padrão: 7) |
| `--format` | | Formato: `txt` (padrão), `markdown`, `english`, `console` |
| `--output` | `-o` | Arquivo de saída (em vez de stdout) |
| `--max-results` | | Máximo de issues (padrão: 100) |
| `--lang` | | Idioma do relatório: `pt` (pt-BR) ou `en` |
| `--include-subtasks` | | Incluir sub-tasks (padrão: excluir tarefas filhas) |
| `--env` | | Caminho para arquivo `.env` customizado |

### Exemplos

```bash
# Filtrar por projeto
jira-summary --project PROJ

# Últimos 14 dias
jira-summary --days 14

# Outro responsável
jira-summary --assignee colega@empresa.com

# JQL customizado (ex: sprint ativa)
jira-summary --jql "project = PROJ AND sprint in openSprints()"

# Salvar em arquivo com data
jira-summary -o relatorio-$(date +%Y-%m-%d).md

# Relatório em inglês
jira-summary --lang en

# Saída compacta no terminal
jira-summary --format console

# Usar outro arquivo .env
jira-summary --env /caminho/.env.producao
```

---

## 7. Uso como módulo Python

Você pode importar e usar o pacote em scripts próprios:

```python
from jira_activity_summary.config import load_config
from jira_activity_summary.jira_client import JiraClient
from jira_activity_summary.summary import build_summary
from jira_activity_summary.report import format_markdown, format_english_markdown

# Carregar config (usa .env ou argumentos)
config = load_config(project="PROJ", days_back=14)

# Buscar issues
client = JiraClient(config)
issues = client.fetch_issues(max_results=50)

# Gerar resumo e relatório
summary = build_summary(issues)
report = format_markdown(summary)  # ou format_english_markdown(summary)

print(report)
# Ou salvar: Path("relatorio.md").write_text(report, encoding="utf-8")
```

---

## 8. Formato do relatório

Formatos: **TXT** (padrão) ou **Markdown**. O relatório contém:

| Seção        | Conteúdo                                                        |
|-------------|-----------------------------------------------------------------|
| **Visão geral** | Tabela com total, concluídos, em progresso, pendentes, bloqueados |
| **Concluídos**  | Lista de tarefas em status Done/Closed/Resolved etc. + resumo do conteúdo |
| **Em progresso**| Tarefas In Progress, In Review, Testing etc. + resumo do conteúdo |
| **Bloqueados**  | Itens em Blocked ou On Hold + resumo do conteúdo               |
| **Pendentes**   | Próximas tarefas (To Do, Backlog) — até 15 itens + resumo      |

### Resumo para diretoria

Para cada tarefa, o app **lê a descrição** (texto ou ADF) e gera um **resumo executivo** em poucas palavras. Usa a primeira frase, bullets ou trechos relevantes; se a descrição for vazia, usa o **último comentário** (o que foi feito / próximos passos). Sem conteúdo útil, a linha Resumo não é exibida. Arquivos de relatório (relatorio*.txt, report*.md, etc.) estão no `.gitignore`.

---

## 9. Estrutura do projeto

```
jira-activity-summary/
├── README.md
├── pyproject.toml
├── .env.example
├── .env                    # Não commitado
├── src/
│   └── jira_activity_summary/
│       ├── __init__.py
│       ├── config.py       # Configuração e JQL
│       ├── jira_client.py   # Cliente Jira
│       ├── content.py      # Extração e resumo do conteúdo (ADF/texto)
│       ├── summary.py      # Geração do resumo
│       ├── report.py       # Formatação Markdown
│       └── cli.py          # Interface de linha de comando
└── tests/
    ├── test_config.py
    ├── test_content.py
    ├── test_report.py
    └── test_summary.py
```

---

## 10. Integração com CI/CD

Para gerar relatórios periodicamente (ex.: cron diário):

```bash
# Todos os dias úteis às 8h
0 8 * * 1-5 cd /caminho/jira-activity-summary && .venv/bin/jira-summary -o /caminho/relatorios/$(date +\%Y-\%m-\%d).md
```

Ajuste `/caminho/` conforme o ambiente. O `.env` deve estar configurado no servidor ou via variáveis de ambiente.

---

## 11. Licença

MIT
