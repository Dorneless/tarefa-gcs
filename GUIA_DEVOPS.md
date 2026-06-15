# Guia DevOps — Projeto GCS (Flask + PostgreSQL + Docker + Flyway + CI/CD)

Passo a passo **exato** para rodar tudo na sua máquina e para os dois cenários
da apresentação. Os comandos funcionam no **PowerShell** do Windows.

---

## 0. Pré-requisitos (IMPORTANTE)

Toda a infraestrutura roda em contêineres. Você **precisa instalar o Docker
Desktop** (ele ainda não está instalado nesta máquina):

1. Baixe e instale o **Docker Desktop** (com WSL2): https://www.docker.com/products/docker-desktop/
2. Abra o Docker Desktop e espere o status ficar **"Engine running"**.
3. Confirme no terminal:
   ```powershell
   docker --version
   docker compose version
   ```

> Para rodar os testes localmente também é útil ter **Python 3.12** (3.11 já
> funciona). O GitHub Actions usa 3.12.

---

## 1. Variáveis de ambiente (.env)

O segredo NUNCA fica no código — fica no `.env` (que está no `.gitignore`).
Você já tem o `.env` preenchido. Confira se ele contém:

```env
SECRET_KEY=...                 # chave do Flask (sessão/login)
MAIL_SERVER=smtp.gmail.com
MAIL_USERNAME=...              # usuário do e-mail
MAIL_PASSWORD=...              # senha de app do e-mail
POSTGRES_USER=gcs_user         # usuário do Postgres dos contêineres
POSTGRES_PASSWORD=gcs_pass     # senha do Postgres dos contêineres
DATABASE_URL=postgresql://gcs_user:gcs_pass@localhost:5433/gcs_homolog
TEST_DATABASE_URL=postgresql://gcs_user:gcs_pass@localhost:5435/gcs_test
```

O `docker compose` lê o `.env` automaticamente para preencher `${...}`.
O `.env.example` (sem segredos) é o que vai para o GitHub.

---

## 2. Subir o ambiente de HOMOLOGAÇÃO

```powershell
docker compose -f docker-compose.homolog.yml up -d --build
```

Ordem do que acontece: sobe o **Postgres** → o **Flyway** aplica a migration
**V1** (cria tabelas + dados base) e encerra → a **App** sobe.

- App de homologação: **http://localhost:5001**
- Banco de homologação: **localhost:5433** (DB `gcs_homolog`)
- Login: usuário `admin123` / senha `senhaSegura`

---

## 3. Subir o ambiente de PRODUÇÃO (portas diferentes)

```powershell
docker compose -f docker-compose.prod.yml up -d --build
```

- App de produção: **http://localhost:5002**
- Banco de produção: **localhost:5434** (DB `gcs_prod`)

> Os dois ambientes são **projetos isolados** (`name: gcs-homolog` e
> `name: gcs-prod`), com volumes e portas próprios. Por isso podem rodar ao
> mesmo tempo sem conflito — essencial para o Cenário B.

---

## 4. Rodar os testes LOCALMENTE (pytest + flake8)

Os testes agora usam PostgreSQL. Suba um Postgres **descartável** só para teste
(porta 5435, igual ao `TEST_DATABASE_URL`):

```powershell
# 1) Sobe o Postgres de teste
docker run --rm -d --name gcs-test-db `
  -e POSTGRES_USER=gcs_user -e POSTGRES_PASSWORD=gcs_pass -e POSTGRES_DB=gcs_test `
  -p 5435:5432 postgres:16-alpine

# 2) Instala as dependências (de preferência num venv)
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 3) Roda lint + testes com cobertura
flake8 .
pytest --cov=app --cov-report=term-missing

# 4) Ao terminar, derruba o Postgres de teste
docker stop gcs-test-db
```

Esperado: **flake8 sem erros** e **20 passed**.

---

## 5. Como o Pipeline (GitHub Actions) funciona

Arquivo: `.github/workflows/pipeline.yml`. Dispara em `push`/`pull_request` na
branch `main`. Tem 2 etapas:

1. **`testes`**: sobe um Postgres de serviço, instala deps, roda **`flake8 .`** e
   **`pytest --cov`** (e salva o relatório de cobertura como artefato).
2. **`build-docker`**: só executa **se a etapa 1 passar** (`needs: testes`) — faz
   o `docker build` da imagem da aplicação.

Ou seja: **teste vermelho ⇒ build não acontece ⇒ pipeline falha.** É exatamente
o que o Cenário A demonstra.

---

## 6. 🎬 CENÁRIO A — O Código Quebrado (falhar nos testes)

Objetivo: mostrar o pipeline **falhando na etapa de testes**.

**Quebre a lógica do teste 07** — arquivo `test_app.py`, **linha 116**:

```python
# ANTES (correto):
    assert b"Luz" in response.data

# DEPOIS (quebrado de propósito):
    assert b"TextoQueNaoExiste" in response.data
```

Depois faça commit e push:

```powershell
git checkout -b demo/pipeline-quebrado
git add test_app.py
git commit -m "demo: quebra o teste 07 para mostrar o pipeline falhando"
git push -u origin demo/pipeline-quebrado
```

No GitHub → aba **Actions**: a etapa **"Lint + Testes"** fica **vermelha** e o
**build Docker nem roda**.

**Para reverter** (deixar verde de novo): desfaça a mudança da linha 116
(voltar para `b"Luz"`), commit e push.

> Alternativa (erro de sintaxe): apague os dois-pontos `:` do final de qualquer
> `def test_...(client):` — o pytest nem coleta os testes e a etapa falha.

---

## 7. 🎬 CENÁRIO B — Tabela exclusiva em Homologação (V2)

Objetivo: aplicar a migration **V2 (tabela `categoria`) só em homologação** e
provar que **produção NÃO foi afetada automaticamente**.

> Por que funciona: nos dois `docker-compose`, o Flyway sobe **travado em
> `FLYWAY_TARGET=1`**. Logo, mesmo o arquivo `V2__criar_tabela_categoria.sql`
> existindo na pasta, **nenhum ambiente aplica a V2 sozinho**. Só aplicamos a
> V2 onde rodarmos o comando manual — e só vamos rodar em homologação.

### Passo 1 — Garanta os dois ambientes no ar (ambos na V1)

```powershell
docker compose -f docker-compose.homolog.yml up -d --build
docker compose -f docker-compose.prod.yml up -d --build
```

### Passo 2 — Estado ANTES (nenhum tem `categoria`)

```powershell
docker compose -f docker-compose.homolog.yml exec db psql -U gcs_user -d gcs_homolog -c "\dt"
docker compose -f docker-compose.prod.yml   exec db psql -U gcs_user -d gcs_prod   -c "\dt"
```
Os dois mostram só `usuario` e `lancamento`.

### Passo 3 — ⭐ COMANDO EXATO: aplicar a V2 SÓ em homologação

```powershell
docker compose -f docker-compose.homolog.yml run --rm -e FLYWAY_TARGET=2 flyway migrate
```

(O `-e FLYWAY_TARGET=2` libera a subida até a V2 **apenas nesta execução**, e
o `run --rm` roda só no projeto de homologação.)

### Passo 4 — Estado DEPOIS (a prova)

```powershell
# HOMOLOGAÇÃO — agora TEM a tabela categoria:
docker compose -f docker-compose.homolog.yml exec db psql -U gcs_user -d gcs_homolog -c "\dt"

# PRODUÇÃO — continua SEM a tabela categoria:
docker compose -f docker-compose.prod.yml exec db psql -U gcs_user -d gcs_prod -c "\dt"
```

Resultado: **homologação tem `categoria`, produção não.** Prova de que a
migration foi controlada por ambiente e produção não foi tocada.

> Opcional (mostrar o histórico de versões de cada ambiente):
> ```powershell
> docker compose -f docker-compose.homolog.yml run --rm flyway info
> docker compose -f docker-compose.prod.yml   run --rm flyway info
> ```

---

## 8. Comandos úteis

```powershell
# Ver logs da app
docker compose -f docker-compose.homolog.yml logs -f app

# Derrubar um ambiente (mantém os dados no volume)
docker compose -f docker-compose.homolog.yml down

# Derrubar e APAGAR os dados (zera o banco / reaplica V1 do zero)
docker compose -f docker-compose.homolog.yml down -v
```

---

## 9. Notas de segurança aplicadas

- **Sem segredos no código**: `SECRET_KEY`, credenciais de e-mail e a
  `DATABASE_URL` vêm 100% de variáveis de ambiente (`os.getenv` + `python-dotenv`).
- **`.env` no `.gitignore`**: segredos reais nunca vão para o GitHub; o
  `.env.example` documenta as chaves sem expor valores.
- **SQL parametrizado** (`%s`): protege contra SQL Injection.
- **Contêiner sem root**: o `Dockerfile` cria e usa o usuário `appuser`.
- **Servidor de produção**: a imagem roda com **gunicorn**, não com o servidor
  de desenvolvimento do Flask.

### Melhoria recomendada (fica como sugestão, não implementada)

As senhas dos usuários ainda são comparadas em texto puro no `login`. Em um
próximo passo, troque para **hash** (ex.: `werkzeug.security` com
`generate_password_hash` / `check_password_hash`) e ajuste a V1 para gravar o
hash em vez de `senhaSegura`.
