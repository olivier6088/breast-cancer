import os
from typing import Dict, List, Union
from pathlib import Path
import json
import joblib
import numpy as np
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Load paths
from config import MODEL_PATH, FEATURES_PATH, CLASSES_PATH

# Lecture du metadata
features_meta = json.loads(FEATURES_PATH.read_text(encoding="utf-8"))
FEATURE_NAMES = [f["name"] for f in features_meta]
DEFAULT_VALUES = {f["name"]: f.get("default", 0.0) for f in features_meta}

# Charger le modèle et classes
MODEL = joblib.load(MODEL_PATH)
CLASS_NAMES = json.loads(CLASSES_PATH.read_text(encoding="utf-8"))

# Exemple Swagger dynamique
example_features = {name: DEFAULT_VALUES[name] for name in FEATURE_NAMES}


class FeaturesPayload(BaseModel):
    features: Union[Dict[str, float], List[float]] = Field(
        ...,
        description="Dictionnaire nom_feature → valeur",
        examples=[example_features],
    )


class PredictionResponse(BaseModel):
    prediction_label: str
    probabilities: Dict[str, float]
    feature_order: List[str]


app = FastAPI(
    title="Breast Cancer API",
    version="1.0",
    description="API FastAPI de démonstration éducative (non clinique)."
)

allowed_origin = os.getenv("ALLOWED_ORIGIN", "http://localhost:8501")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[allowed_origin],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_loaded": MODEL is not None,
        "n_features": len(FEATURE_NAMES),
        "classes": CLASS_NAMES,
    }

@app.get("/features", tags=["meta"])
def get_features():
    """Renvoie la liste des features avec valeurs par défaut"""
    return {"features": features_meta}


@app.post("/predict", response_model=PredictionResponse, tags=["predict"])
def predict(payload: FeaturesPayload):
    
    feats = payload.features
    
    if isinstance(feats, dict):
        missing = [k for k in FEATURE_NAMES if k not in feats]
        if missing:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Champs manquants: {missing}")
        values = [float(feats.get(k)) for k in FEATURE_NAMES]
    else:
        if len(feats) != len(FEATURE_NAMES):
            raise HTTPException(status_code=422, detail=f"Longueur attendue {len(FEATURE_NAMES)}, reçue {len(feats)}")
        values = [float(x) for x in feats]

    X = np.array(values, dtype=float).reshape(1, -1)

    proba = MODEL.predict_proba(X)[0]
    idx = int(np.argmax(proba))

    return PredictionResponse(
        prediction_label=CLASS_NAMES[idx],
        probabilities={CLASS_NAMES[i]: round(float(p), 2) for i, p in enumerate(proba)},
        feature_order=FEATURE_NAMES,
    )
