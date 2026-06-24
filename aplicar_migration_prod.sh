#!/usr/bin/env bash
# Aplica a migration V2 (tabela categoria) em PRODUCAO.
# Use SOMENTE depois do merge do PR aprovado (promocao controlada de versao).
set -e
cd "$(dirname "$0")"

echo ">> Aplicando migration V2 (categoria) em PRODUCAO..."
docker compose -f docker-compose.prod.yml run --rm -e FLYWAY_TARGET=2 flyway migrate

echo ""
echo "Pronto! V2 aplicada em PRODUCAO (promocao pos-merge)."
echo "Verifique: docker compose -f docker-compose.prod.yml exec db psql -U gcs_user -d gcs_prod -c '\\dt'"
