#!/usr/bin/env bash
# Derruba o ambiente de PRODUCAO (mantem os dados no volume).
set -e
cd "$(dirname "$0")"

echo ">> Parando PRODUCAO..."
docker compose -f docker-compose.prod.yml down

echo "PRODUCAO parada. (Os dados ficam preservados no volume.)"
