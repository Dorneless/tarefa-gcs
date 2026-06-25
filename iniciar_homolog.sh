#!/usr/bin/env bash
# Sobe o ambiente de HOMOLOGACAO (build + up -d) e aplica as migrations.
# Aplica ate a V2 (tabela categoria) quando ela existir na pasta migrations,
# entao rodar este script ja sobe a V2 para homologacao.
set -e
cd "$(dirname "$0")"

if [ ! -f .env ]; then
  echo "[info] Arquivo .env nao encontrado. Criando a partir de .env.example..."
  cp .env.example .env
fi

echo ">> Subindo HOMOLOGACAO (o primeiro build pode demorar um pouco)..."
docker compose -f docker-compose.homolog.yml up -d --build

echo ""
echo ">> Aplicando migrations em HOMOLOGACAO (sobe ate a V2/categoria quando existir)..."
docker compose -f docker-compose.homolog.yml run --rm -e FLYWAY_TARGET=2 flyway migrate

echo ""
echo "HOMOLOGACAO no ar:"
echo "  App:   http://localhost:5001"
echo "  Banco: localhost:5433 (gcs_homolog)"
echo "  Login: admin123 / senhaSegura"
