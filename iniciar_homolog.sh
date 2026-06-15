#!/usr/bin/env bash
# Sobe o ambiente de HOMOLOGACAO em background (build + up -d).
set -e
cd "$(dirname "$0")"

if [ ! -f .env ]; then
  echo "[info] Arquivo .env nao encontrado. Criando a partir de .env.example..."
  cp .env.example .env
fi

echo ">> Subindo HOMOLOGACAO (o primeiro build pode demorar um pouco)..."
docker compose -f docker-compose.homolog.yml up -d --build

echo ""
echo "HOMOLOGACAO no ar:"
echo "  App:   http://localhost:5001"
echo "  Banco: localhost:5433 (gcs_homolog)"
echo "  Login: admin123 / senhaSegura"
