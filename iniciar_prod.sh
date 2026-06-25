#!/usr/bin/env bash
# Sobe o ambiente de PRODUCAO (build + up -d) e aplica as migrations.
# Aplica ate a V2 (tabela categoria) quando ela existir na pasta migrations,
# entao rodar este script ja "promove" a V2 para producao.
set -e
cd "$(dirname "$0")"

if [ ! -f .env ]; then
  echo "[info] Arquivo .env nao encontrado. Criando a partir de .env.example..."
  cp .env.example .env
fi

echo ">> Subindo PRODUCAO (o primeiro build pode demorar um pouco)..."
docker compose -f docker-compose.prod.yml up -d --build

echo ""
echo ">> Aplicando migrations em PRODUCAO (sobe ate a V2/categoria quando existir)..."
docker compose -f docker-compose.prod.yml run --rm -e FLYWAY_TARGET=2 flyway migrate

echo ""
echo "PRODUCAO no ar:"
echo "  App:   http://localhost:5002"
echo "  Banco: localhost:5434 (gcs_prod)"
echo "  Login: admin123 / senhaSegura"
