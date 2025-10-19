# Breast Cancer — FastAPI (API) + Streamlit (App)

Projet pédagogique (PoC) qui **sert un modèle ML** (régression logistique entraîné sur *Breast Cancer* de scikit-learn) via une **API FastAPI**, et une **application Streamlit** cliente.

Objectifs : apprendre à **exposer un modèle** (API), **consommer l’API** (app), gérer **CORS**, **déploiement local**, **Docker Compose**, puis **Render (API)** et **Azure App Service (App)**.

> ⚠️ **Avertissement éthique** : démonstration **éducative**, **non destinée au soin** ni à un usage clinique réel.

---

## 🧭 Sommaire

* [Architecture](#architecture)
* [Arborescence du repo](#arborescence-du-repo)
* [Prérequis](#prérequis)
* [Démarrage rapide (local)](#démarrage-rapide-local)
* [Scripts utiles](#scripts-utiles)
* [API FastAPI](#api-fastapi)

  * [Endpoints](#endpoints)
  * [Schéma d’entrée](#schéma-dentrée)
  * [Exemples `curl`](#exemples-curl)
* [App Streamlit](#app-streamlit)
* [Configuration / Variables d’environnement](#configuration--variables-denvironnement)
* [Docker Compose (API + App)](#docker-compose-api--app)
* [Déploiement](#déploiement)

  * [API → Render](#api--render)
  * [App → Azure App Service](#app--azure-app-service)
* [Dépannage](#dépannage)
* [Licence](#licence)

---

## Architecture

```
[ Streamlit App ]  ←(HTTP JSON)→  [ FastAPI ]
   http://localhost:8501           http://localhost:5000

En prod :
- API sur Render  → https://<api>.onrender.com
- App sur Azure   → https://<app>.azurewebsites.net
```

---

## Arborescence du repo

```
breast-cancer-fastapi-streamlit/
├─ api/
│  ├─ main.py                 # API FastAPI
│  ├─ config.py               # chemins modèles / metadata
│  ├─ requirements.txt
│  ├─ models/
│  │  ├─ breast_logreg.joblib
│  │  ├─ class_names.json     # ["malignant","benign"]
│  │  └─ features_metadata.json
│  │     # ex: [
│  │     #   {"name":"mean radius","default":14.0,"unit":"NA"},
│  │     #   {"name":"mean texture","default":20.0,"unit":"NA"},
│  │     #   ...
│  │     # ]
│  └─ Dockerfile
├─ app/
│  ├─ streamlit_app.py        # client Streamlit
│  ├─ requirements.txt
│  └─ Dockerfile
├─ scripts/
│  ├─ run_api.sh              # lance FastAPI (local)
│  ├─ run_app.sh              # lance Streamlit (local)
│  └─ run_all.sh              # lance les deux
├─ docker-compose.yml
└─ README.md  (ce fichier)
```

---

## Prérequis

* Python 3.10+ (3.11 recommandé)
* `pip`, `venv`
* (optionnel) Docker & Docker Compose
* Un terminal

---

## Démarrage rapide (local)

1. **Créer l’environnement virtuel** à la racine :

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows
# .venv\Scripts\activate
```

2. **Installer les dépendances** :

```bash
pip install -r api/requirements.txt
pip install -r app/requirements.txt
```

3. **Lancer l’API** :

```bash
./scripts/run_api.sh
# ou:
# cd api
# uvicorn main:app --host 0.0.0.0 --port 5000 --reload
```

* Swagger : [http://localhost:5000/docs](http://localhost:5000/docs)
* Health : [http://localhost:5000/health](http://localhost:5000/health)

4. **Lancer l’app Streamlit** (dans un autre terminal activé) :

```bash
./scripts/run_app.sh
# ou:
# cd app
# streamlit run streamlit_app.py --server.port 8501
```

* App : [http://localhost:8501](http://localhost:8501)

> Astuce : `./scripts/run_all.sh` ouvre (selon OS) deux terminaux et lance les deux services.

---

## Scripts utiles

* **API** : `./scripts/run_api.sh`
* **App** : `./scripts/run_app.sh`
* **Tout** : `./scripts/run_all.sh`

> Les scripts exportent `API_BASE_URL=http://localhost:5000` pour l’app.

---

## API FastAPI

**Fichier** : `api/main.py`
**Modèle** : chargé depuis `api/models/breast_logreg.joblib`
**Features / classes** : chargées depuis JSON (métadonnées & labels)

### Endpoints

* `GET /health` → `{"status":"ok"}`
* `GET /features` → `{"features":[{"name": "...","default": 0.0,"unit":"..."}, ...]}`
* `GET /meta` *(optionnel si ajouté)* → infos modèle (`classes`, `n_features`, etc.)
* `POST /predict` → prédiction + probabilités
  **Response 200** :

  ```json
  {
    "prediction_label": "benign",
    "probabilities": { "malignant": 0.21, "benign": 0.79 },
    "feature_order": ["mean radius", "mean texture", "..."]
  }
  ```

  **Erreurs** :

  * `400` : champs manquants, longueur incorrecte, etc.

### Schéma d’entrée

**Body (JSON)** :

```json
{
  "features": {
    "mean radius": 14.0,
    "mean texture": 20.0,
    "mean perimeter": 90.0,
    "mean area": 600.0,
    "mean smoothness": 0.1,
    "mean compactness": 0.12
  }
}
```

> L’exemple Swagger est **généré dynamiquement** à partir de `features_metadata.json` (les valeurs par défaut y sont définies).

### Exemples `curl`

* **Health**

```bash
curl -s http://localhost:5000/health
```

* **Prédiction**

```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "features": {
      "mean radius": 14.0,
      "mean texture": 20.0,
      "mean perimeter": 90.0,
      "mean area": 600.0,
      "mean smoothness": 0.10,
      "mean compactness": 0.12
    }
  }'
```

---

## App Streamlit

**Fichier** : `app/streamlit_app.py`

* Lit `API_BASE_URL` (par défaut `http://localhost:5000`)
* Récupère/affiche des champs pour les features (avec **valeurs par défaut**)
* Appelle `/predict` et colore la sortie :

  * **malignant** → **rouge** (⚠️)
  * **benign** → **vert** (✅)
* Affiche également les **probabilités**.

---

## Configuration / Variables d’environnement

### API (FastAPI)

* `ALLOWED_ORIGINS` : origines autorisées CORS (séparées par des virgules)
  ex. `http://localhost:8501` en local, puis l’URL Azure en prod.
* (selon ton `config.py`) chemins relatifs aux modèles & metadata.

### App (Streamlit)

* `API_BASE_URL` : URL de l’API
  ex. `http://localhost:5000` en local, puis `https://<api>.onrender.com` en prod.

> Tu peux créer un fichier `.env` (non commité) et l’exposer avec Docker/Render/Azure si besoin.

---

## Docker Compose (API + App)

**Fichier** : `docker-compose.yml`

Démarrer les deux services :

```bash
docker compose up --build
```

* API : [http://localhost:5000](http://localhost:5000)  (Swagger `/docs`)
* App : [http://localhost:8501](http://localhost:8501)

Notes :

* L’app **appelle** l’API via `http://api:5000` **dans le réseau compose** (configuré via `API_BASE_URL`).
* CORS côté API inclut `http://localhost:8501` pour l’usage depuis le navigateur.

---

## Déploiement

### API → Render

1. Repo GitHub avec `api/` (incluant `models/`).
2. Render → **New** → **Web Service** → Root directory: `api`
3. Build command :

   ```
   pip install -r requirements.txt
   ```
4. Start command :

   ```
   uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
5. Variables d’env :

   * `ALLOWED_ORIGINS=https://<ton-app>.azurewebsites.net`
6. Tester :

   * `/health` → OK
   * `/docs` → Swagger
   * `POST /predict` → retourne une prédiction

### App → Azure App Service (Linux)

1. Créer App Service (Python 3.11).
2. Déployer le dossier `app/` (Deployment Center GitHub, ZIP, etc.).
3. **Startup command** :

   ```bash
   bash -c "pip install -r app/requirements.txt && streamlit run app/streamlit_app.py --server.port $PORT --server.address 0.0.0.0"
   ```

   *(adapte les chemins selon ton mode de déploiement)*
4. **App settings** :

   * `API_BASE_URL=https://<ton-api>.onrender.com`
5. Ouvrir `https://<ton-app>.azurewebsites.net`

---

## Dépannage

* **`400 Champs manquants`**
  → Les clés du JSON doivent **exactement** correspondre à `features_metadata.json`.
  Vérifie `/features` ou Swagger `/docs`.

* **CORS (bloqué par le navigateur)**
  → Côté API (FastAPI), `ALLOWED_ORIGINS` doit inclure l’URL **complète** de l’app (Azure).
  Exemple : `https://<ton-app>.azurewebsites.net`

* **Port déjà utilisé**
  → Change de port ou ferme l’appli qui l’utilise (`lsof -i :5000` / `:8501`).

* **Modèle introuvable / chemins**
  → Vérifie `config.py` et que les fichiers existent dans `api/models/`.

* **Cold start Render (lent au premier appel)**
  → Normal en plan gratuit. Relance via `/health` avant une démo.

* **Compose : l’app ne trouve pas l’API**
  → Assure `API_BASE_URL=http://api:5000` côté service `app` dans `docker-compose.yml`.

---

## Licence

* Code : à préciser (MIT recommandé pour un TP).
* Données : dataset *Breast Cancer Wisconsin (Diagnostic)* via scikit-learn (usage éducatif).

---

### 💬 Contact & Remarques

* Projet pensé pour **l’enseignement** : code simple, endpoints clairs, doc Swagger native.
* Extensions possibles : suivi de versions de modèles, logs structurés, monitoring, tests unitaires, CI/CD.

Bonne expérimentation 🔬🚀
