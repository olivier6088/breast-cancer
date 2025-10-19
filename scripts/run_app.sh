
#!/usr/bin/env bash
# Lance l'app Streamlit (port 8501)

echo "🎨 Lancement de l'app Streamlit sur http://localhost:8501 ..."
cd "$(dirname "$0")/../app" || exit 1

# Activer l'environnement virtuel si besoin
if [ -d "../.venv" ]; then
  source ../.venv/bin/activate
fi

# Définir la variable d'environnement pour l’API
export API_BASE_URL="http://localhost:5000"

# Lancer Streamlit
streamlit run app.py --server.port 8501
