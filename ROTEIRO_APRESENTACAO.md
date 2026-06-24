# Roteiro da Apresentação — Projeto GCS (Flask + PostgreSQL + Docker + Flyway + CI/CD)

Adaptado do fluxo `homolog → Pull Request → main`. Todos os comandos rodam na
**VM Linux** (Docker e Docker Compose já instalados). Repositório:
`https://github.com/Dorneless/tarefa-gcs`

> Stack: o "quality gate" é o **flake8** e os testes são **20 testes pytest**
> (o equivalente ao ESLint/mocha do Node).

---

## 1. Acessar a VM
```bash
ssh <seu-alias-da-vm>
```

## 2. Mostrar que o Docker está vazio
```bash
docker ps -a
docker images
docker volume ls
```

## 3. Clonar o projeto
```bash
git clone https://github.com/Dorneless/tarefa-gcs
cd tarefa-gcs
```
> Se já tiver clonado antes: `cd tarefa-gcs && git switch main && git pull`

## 4. Criar HOMOLOGAÇÃO
```bash
./iniciar_homolog.sh
docker compose -f docker-compose.homolog.yml ps
```
App em http://localhost:5001 — Banco em localhost:5433.

## 5. Criar PRODUÇÃO
```bash
./iniciar_prod.sh
docker compose -f docker-compose.prod.yml ps
```
App em http://localhost:5002 — Banco em localhost:5434.

## 6. Conferir o banco ANTES da mudança
```bash
docker compose -f docker-compose.homolog.yml exec db psql -U gcs_user -d gcs_homolog -c "\dt"
docker compose -f docker-compose.homolog.yml exec db psql -U gcs_user -d gcs_homolog -c "SELECT COUNT(*) FROM lancamento;"
docker compose -f docker-compose.prod.yml exec db psql -U gcs_user -d gcs_prod -c "\dt"
docker compose -f docker-compose.prod.yml exec db psql -U gcs_user -d gcs_prod -c "SELECT COUNT(*) FROM lancamento;"
```
Esperado nos DOIS: tabelas `usuario` e `lancamento`, COUNT = **10**, e **nenhum**
tem `categoria` ainda.

## 7. Ir para a branch de validação (homolog)
```bash
git switch homolog
git pull origin homolog
```

## 8. 🔴 Demonstrar o ERRO DE QUALIDADE
O código abaixo **roda**, mas a regra do flake8 (import não usado, `F401`)
reprova — igual ao `no-var` do ESLint.

Edite o `app.py` e adicione esta linha logo após os imports (perto da linha 15):
```python
import sys   # ERRO DE QUALIDADE PROPOSITAL: import nao utilizado (flake8 F401)
```
Rode o quality gate:
```bash
./quality.sh
```
Resultado: **falha** com `app.py:15:1: F401 'sys' imported but unused`.
👉 O portão de qualidade barrou o código ANTES de ir para o repositório.

## 9. 🟢 Validar a mudança correta
Remova a linha `import sys` que você adicionou. Depois rode o CI completo
(qualidade + os 20 testes):
```bash
./ci.sh
```
Resultado: **flake8 OK** e **20 passed**.

## 10. Versionar e enviar (dispara o CI + abre o PR)
```bash
git add -A
git commit -m "Altera label e adiciona tabela categoria (V2)"
git push origin homolog
```
O push na `homolog` dispara o **GitHub Actions** (flake8 → 20 testes → build
Docker). Acompanhe em: https://github.com/Dorneless/tarefa-gcs/actions

Com o CI verde, abra o Pull Request para a `main`:
- Pelo site: https://github.com/Dorneless/tarefa-gcs/compare/main...homolog
- Ou pelo terminal (se tiver o `gh`): 
  `gh pr create --base main --head homolog --title "Altera label e adiciona tabela categoria" --body "Promocao para producao"`

> Opcional (regra do colega "só faz merge se passar"): em **Settings → Branches**
> do GitHub, crie uma *branch protection rule* para `main` exigindo o status
> check do pipeline. Aí o botão de merge só libera com o CI verde.

## 11. Atualizar HOMOLOGAÇÃO (aplica a nova migration só em HML)
```bash
# (opcional) rebuildar o app de homolog com o novo código:
./iniciar_homolog.sh

# aplica a V2 (tabela categoria) APENAS em homologação:
./aplicar_migration_homolog.sh

# prova:
docker compose -f docker-compose.homolog.yml exec db psql -U gcs_user -d gcs_homolog -c "\dt"
docker compose -f docker-compose.homolog.yml exec db psql -U gcs_user -d gcs_homolog -c "SELECT COUNT(*) FROM lancamento;"
```
Agora HOMOLOG **tem** `categoria`, e o COUNT de `lancamento` continua **10**
(dados preservados). PRODUÇÃO ainda **não** tem `categoria`.

## 12. Atualizar PRODUÇÃO (somente após o MERGE do PR)
```bash
git switch main
git pull origin main

# (opcional) rebuildar o app de produção com o código aprovado:
./iniciar_prod.sh

# promoção controlada: aplica a V2 em produção:
./aplicar_migration_prod.sh

# prova:
docker compose -f docker-compose.prod.yml exec db psql -U gcs_user -d gcs_prod -c "\dt"
docker compose -f docker-compose.prod.yml exec db psql -U gcs_user -d gcs_prod -c "SELECT COUNT(*) FROM lancamento;"
```
Agora PRODUÇÃO também tem `categoria` — mas só porque **um humano promoveu
após o merge aprovado**. COUNT de `lancamento` segue **10** (nada se perdeu).

---

## Mensagens-chave para a banca
- **Portão de qualidade (flake8)** barra código ruim antes do push (passo 8).
- **CI no GitHub Actions** roda flake8 + 20 testes + build Docker; só passa se
  tudo estiver verde (passo 10).
- **Migrations promovidas por ambiente, sob controle humano**: homolog primeiro
  (passo 11), produção só após o merge do PR (passo 12) — produção nunca é
  alterada automaticamente.
- **Dados preservados** nas migrations (COUNT de `lancamento` = 10 do início ao fim).

## Para limpar tudo ao final
```bash
./parar_homolog.sh
./parar_prod.sh
```
