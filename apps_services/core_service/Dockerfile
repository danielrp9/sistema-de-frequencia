# Usar uma imagem Python estável
FROM python:3.11-slim

# Evitar que o Python gere arquivos .pyc e garanta log em tempo real
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Diretório de trabalho no container
WORKDIR /app

# Instalar dependências do sistema necessárias para PostgreSQL e outras ferramentas
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependências do Python
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o restante do código
COPY . /app/

# Script de entrada para garantir que o banco esteja pronto
COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
