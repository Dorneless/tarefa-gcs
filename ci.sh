#!/usr/bin/env bash
# CI completo LOCAL: flake8 + os 20 testes (pytest), via Docker.
# Sobe um Postgres de teste descartavel. (Equivale ao "npm run ci".)
set -e
cd "$(dirname "$0")"

NET=gcs_ci_net
DB=gcs_ci_db

cleanup() {
  docker rm -f "$DB" >/dev/null 2>&1 || true
  docker network rm "$NET" >/dev/null 2>&1 || true
}
trap cleanup EXIT

echo ">> Subindo Postgres de teste descartavel..."
docker network create "$NET" >/dev/null 2>&1 || true
docker run -d --rm --name "$DB" --network "$NET" \
  -e POSTGRES_USER=gcs_user -e POSTGRES_PASSWORD=gcs_pass -e POSTGRES_DB=gcs_test \
  postgres:16-alpine >/dev/null

echo ">> Aguardando o banco ficar pronto..."
until docker exec "$DB" pg_isready -U gcs_user -d gcs_test >/dev/null 2>&1; do
  sleep 1
done

echo ">> Rodando flake8 + pytest (20 testes)..."
docker run --rm --network "$NET" -v "$PWD":/app -w /app \
  -e TEST_DATABASE_URL="postgresql://gcs_user:gcs_pass@${DB}:5432/gcs_test" \
  -e SECRET_KEY=ci-local \
  -e MAIL_USERNAME=ci@example.com -e MAIL_PASSWORD=dummy \
  python:3.12-slim \
  sh -c "pip install -q -r requirements.txt && flake8 . && pytest --cov=app"

echo "OK! Qualidade (flake8) + os 20 testes passaram."
