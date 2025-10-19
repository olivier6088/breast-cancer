#!/usr/bin/env bash
# Lance l'API et l'app Streamlit en parallèle

echo "🚀 Démarrage API + APP ..."

# Lancer API en arrière-plan
gnome-terminal -- bash -c "./scripts/run_api.sh; exec bash" 2>/dev/null \
  || x-terminal-emulator -e "./scripts/run_api.sh" 2>/dev/null \
  || (echo "👉 Ouvre un autre terminal et lance ./scripts/run_api.sh manuellement")

# Lancer l'app Streamlit
./scripts/run_app.sh
