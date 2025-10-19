#!/usr/bin/env bash
# Lance l'API FastAPI (port 5000)

echo "🚀 Lancement de l'API FastAPI sur http://localhost:5000 ..."
cd "$(dirname "$0")/../api" || exit 1

# Activer l'environnement virtuel si besoin
if [ -d "../.venv" ]; then
  source ../.venv/bin/activate
fi

# Lancer Uvicorn
uvicorn main:app --host 0.0.0.0 --port 5000 --reload
