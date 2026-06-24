#!/usr/bin/env bash
# Derruba o ambiente de HOMOLOGACAO (mantem os dados no volume).
set -e
cd "$(dirname "$0")"

echo ">> Parando HOMOLOGACAO..."
docker compose -f docker-compose.homolog.yml down

echo "HOMOLOGACAO parada. (Os dados ficam preservados no volume.)"
