#!/usr/bin/env bash
# "Quality gate" local: roda APENAS o flake8, dentro de um container Python.
# Nao precisa de Python instalado na VM, so Docker. (Equivale ao "npm run quality".)
set -e
cd "$(dirname "$0")"

echo ">> Rodando flake8 (analise de qualidade)..."
docker run --rm -v "$PWD":/app -w /app python:3.12-slim \
  sh -c "pip install -q flake8==7.1.1 && flake8 ."

echo "OK! Nenhum problema de qualidade encontrado."
