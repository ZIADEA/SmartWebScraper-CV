from flask import Flask
import os
import json

app = Flask(__name__)
app.config['BASE_DIR'] = os.path.dirname(os.path.abspath(__file__))

app.config['SECRET_KEY'] = 'dev_secret_key'  # À remplacer en production

# Configuration des chemins (version robuste)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app.config.update({
    'DATA_FOLDER': os.path.join(BASE_DIR, 'app/data'),
    'MODELS_FOLDER': os.path.join(BASE_DIR, 'app/models')
})

# Sous-dossiers
data_subfolders = [
    'originals', 'resized', 'annotated',
    'predictions_raw', 'predictions_scaled',
    'human_data', 'fine_tune_data'
]

for folder in data_subfolders:
    key = f"{folder.upper()}_FOLDER"
    path = os.path.join(app.config['DATA_FOLDER'], folder)
    app.config[key] = path
    os.makedirs(path, exist_ok=True)  # Crée le dossier si inexistant

app.config['VISITED_LINKS_FILE'] = os.path.join(app.config['DATA_FOLDER'], 'visited_links.json')

# Load admin credentials from environment or optional config file
admin_email = os.environ.get("ADMIN_EMAIL")
admin_password = os.environ.get("ADMIN_PASSWORD")
config_path = os.path.join(BASE_DIR, "admin_config.json")
if (admin_email is None or admin_password is None) and os.path.exists(config_path):
    try:
        with open(config_path, "r") as f:
            creds = json.load(f)
        admin_email = admin_email or creds.get("ADMIN_EMAIL")
        admin_password = admin_password or creds.get("ADMIN_PASSWORD")
    except Exception:
        pass

app.config["ADMIN_EMAIL"] = admin_email
app.config["ADMIN_PASSWORD"] = admin_password


# Configuration Playwright
PLAYWRIGHT_CONFIG = {
    "HEADLESS": True,
    "TIMEOUT": 30000,
    "VIEWPORT": {"width": 1280, "height": 1024}
}
app.config["THING_CLASSES"] = [
    "advertisement", "chaine", "commentaire", "description", "header", "footer", "left sidebar",
    "logo", "likes", "media", "pop up", "recommendations", "right sidebar", "suggestions",
    "title", "vues", "none access", "other"
]

# Import des routes DOIT être la dernière opération
from app import routes
