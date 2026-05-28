FROM python:3.11-alpine

# Instala dependências de sistema necessárias para compilar algumas libs do Postgres se necessário
RUN apk add --no-cache gcc musl-dev postgresql-dev

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000