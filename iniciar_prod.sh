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
docker compose -f docker-compose.prod.yml run --rm -e FLYWAY_TARGET=latest flyway migrate

