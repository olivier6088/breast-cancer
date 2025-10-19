# api/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Déps système utiles
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl build-essential && rm -rf /var/lib/apt/lists/*

# Dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Code + modèles
COPY . .

# Port/API
ENV PORT=5000
EXPOSE 5000

# Démarrage
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]
