# Dockerfile - Docker konteynerida bot ishga tushirish

FROM python:3.11-slim

WORKDIR /app

# Sistemali paketlarni o'rnatish
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# Python dependenciyalari
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Fayl nusxalash
COPY . .

# Environment
ENV PYTHONUNBUFFERED=1

# Ishga tushirish
CMD ["python", "-m", "app.main"]

