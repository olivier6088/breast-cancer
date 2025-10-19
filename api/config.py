from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"
MODEL_PATH = MODELS_DIR / "model.joblib"
FEATURES_PATH = MODELS_DIR / "features_metadata.json"
CLASSES_PATH = MODELS_DIR / "class_names.json"
