# Hafif Python imajı
FROM python:3.11-slim

# Sistemde gerekli kütüphaneleri yükle (psycopg2 için libpq-dev lazım)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Python bağımlılıklarını yükle
RUN pip install --no-cache-dir psycopg2-binary confluent-kafka python-dateutil

# Çalışma klasörü
WORKDIR /app

# Scriptler compose içindeki volume'dan mount edilecek (COPY gerek yok)