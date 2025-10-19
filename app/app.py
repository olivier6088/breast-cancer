import os
import requests
import streamlit as st

# ------------------------------------------------------------
# 🔧 Configuration
# ------------------------------------------------------------
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:5000")

st.set_page_config(page_title="Breast Cancer Demo", page_icon="🩺")
st.title("Breast Cancer Demo")
# st.subheader("FastAPI + Streamlit")

# ------------------------------------------------------------
# 🧠 Récupération dynamique des features depuis l'API
# ------------------------------------------------------------
@st.cache_data
def get_features_from_api():
    """Appelle l'endpoint /features pour récupérer noms et valeurs par défaut"""
    try:
        r = requests.get(f"{API_BASE_URL}/features", timeout=5)
        r.raise_for_status()
        data = r.json()
        features_meta = data.get("features", [])
        # On transforme en dict : {name: default_value}
        features_defaults = {f["name"]: f.get("default", 0.0) for f in features_meta}
        return features_defaults
    except Exception as e:
        st.warning(f"Impossible de récupérer les features : {e}")
        return {}

# Chargement des features
features_defaults = get_features_from_api()

if not features_defaults:
    st.error("⚠️ Aucune feature trouvée. Vérifie que l'API est bien lancée.")
    st.stop()

# ------------------------------------------------------------
# 🧾 Formulaire de saisie
# ------------------------------------------------------------
st.write("")
st.text("Veuillez saisir les caractéristiques")

cols = st.columns(3)
values = {}

for i, (name, default) in enumerate(features_defaults.items()):
    with cols[i % 3]:
        values[name] = st.number_input(
            name,
            value=float(default),
            step=0.01,
            format="%.5f",
        )

# ------------------------------------------------------------
# 🚀 Prédiction
# ------------------------------------------------------------
if st.button("Prédire"):
    payload = {"features": values}
    try:
        r = requests.post(f"{API_BASE_URL}/predict", json=payload, timeout=5)
        if r.ok:
            data = r.json()
            label = data["prediction_label"].strip().lower()
             # Choisir couleur selon le diagnostic
            if label == "malignant":
                color = "red"
                emoji = "⚠️"
            elif label == "benign":
                color = "green"
                emoji = "✅"
            
            st.markdown(
                f"<h3 style='color:{color};'>Prédiction : {emoji} {data['prediction_label'].capitalize()}</h3>",
                unsafe_allow_html=True
            )
            st.json(data["probabilities"])
        else:
            st.error(f"Erreur API ({r.status_code}) : {r.text}")
    except requests.exceptions.RequestException as e:
        st.error(f"API indisponible : {e}")

st.write("")
st.caption(f"🔗 API utilisée : {API_BASE_URL}")

st.markdown(
    """
    <hr>
    <div style="text-align:center; color:gray; font-size:0.9em;">
        🩺 Breast Cancer Demo
        <br>
        <i>Projet éducatif — non destiné à un usage clinique</i><br>
        © 2025 - OSA Formation
    </div>
    """,
    unsafe_allow_html=True
)