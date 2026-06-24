#!/usr/bin/env bash
# Sobe o ambiente de PRODUCAO em background (build + up -d).
set -e
cd "$(dirname "$0")"

if [ ! -f .env ]; then
  echo "[info] Arquivo .env nao encontrado. Criando a partir de .env.example..."
  cp .env.example .env
fi

echo ">> Subindo PRODUCAO (o primeiro build pode demorar um pouco)..."
docker compose -f docker-compose.prod.yml up -d --build

echo ""
echo "PRODUCAO no ar:"
echo "  App:   http://localhost:5002"
echo "  Banco: localhost:5434 (gcs_prod)"
echo "  Login: admin123 / senhaSegura"
