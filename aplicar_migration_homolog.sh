#!/usr/bin/env bash
# CENARIO B: aplica a migration V2 (tabela categoria) SOMENTE em homologacao.
# Producao continua travada em FLYWAY_TARGET=1 e NAO e afetada.
set -e
cd "$(dirname "$0")"

echo ">> Aplicando migration V2 (categoria) APENAS em HOMOLOGACAO..."
docker compose -f docker-compose.homolog.yml run --rm -e FLYWAY_TARGET=2 flyway migrate

echo ""
echo "Pronto! V2 aplicada em HOMOLOGACAO. PRODUCAO nao foi tocada."
echo ""
echo "Para provar (compare as tabelas dos dois bancos):"
echo "  Homolog: docker compose -f docker-compose.homolog.yml exec db psql -U gcs_user -d gcs_homolog -c '\\dt'"
echo "  Prod:    docker compose -f docker-compose.prod.yml   exec db psql -U gcs_user -d gcs_prod   -c '\\dt'"
