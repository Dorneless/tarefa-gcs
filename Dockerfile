# Imagem base enxuta com Python
FROM python:3.12-slim

# Boas praticas: sem .pyc e logs sem buffer
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Instala dependencias primeiro (aproveita cache de camadas)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do codigo
COPY . .

# Seguranca: roda como usuario sem privilegios (nao-root)
RUN useradd --create-home appuser
USER appuser

EXPOSE 5000

# Servidor WSGI de producao (nao usar o servidor de dev do Flask)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]
