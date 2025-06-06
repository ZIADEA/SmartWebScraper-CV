import shutil
import os
import json
import uuid  # For generating unique IDs
from datetime import datetime  # For timestamping
import cv2
import numpy as np
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright
import validators  # To validate URL
from detectron2.engine import DefaultPredictor
from detectron2.data import MetadataCatalog
from detectron2.config import get_cfg
from detectron2 import model_zoo
from app import app
from app.utils.nlp_module import CompleteOCRQASystem  # chemin adapté
from flask import (
    current_app,
    jsonify,
    render_template,
    request,
    redirect,
    send_file,
    url_for,
    flash,
    session,
    send_from_directory,
    abort,
)

import openai
from dotenv import load_dotenv
load_dotenv()

# routes.py - Structure complète avec helpers

# ═══════════════════════════════════════════════════════════════════
# IMPORTS (garder tes imports existants + ajouter ceux-ci)
# ═══════════════════════════════════════════════════════════════════

import shutil
import os
import json
import uuid
from datetime import datetime
import cv2
import numpy as np
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright
import validators
from detectron2.engine import DefaultPredictor
from detectron2.data import MetadataCatalog
from detectron2.config import get_cfg
from detectron2 import model_zoo
from app import app
from app.utils.nlp_module import CompleteOCRQASystem
from flask import (
    current_app, jsonify, render_template, request, redirect, send_file,
    url_for, flash, session, send_from_directory, abort
)
import openai
from dotenv import load_dotenv
import requests
from io import BytesIO
import zipfile
import time


# ═══════════════════════════════════════════════════════════════════
# FILTRES JINJA2 (À AJOUTER AU DÉBUT DE TON FICHIER ROUTES)
# ═══════════════════════════════════════════════════════════════════

@app.template_filter('timestamp_to_date')
def timestamp_to_date(timestamp):
    """Convertit un timestamp en date lisible"""
    try:
        return datetime.fromtimestamp(timestamp).strftime('%d/%m/%Y %H:%M')
    except:
        return "Date inconnue"

@app.template_filter('filesize_format')
def filesize_format(size_bytes):
    """Formate la taille de fichier en unités lisibles"""
    try:
        if size_bytes == 0:
            return "0 B"
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024
            i += 1
        return f"{size_bytes:.1f} {size_names[i]}"
    except:
        return "Taille inconnue"

@app.context_processor
def inject_global_vars():
    """Injecte des variables dans tous les templates"""
    return {
        'current_year': datetime.now().year,
        'app_name': 'Scrapper Intelligent',
        'version': '1.0.0'
    }

# ═══════════════════════════════════════════════════════════════════
# FONCTIONS HELPER (À AJOUTER APRÈS LES FILTRES)
# ═══════════════════════════════════════════════════════════════════

def ensure_human_data_structure():
    """Assure que la structure des dossiers human_data est correcte"""
    human_data_path = app.config["HUMAN_DATA_FOLDER"]
    
    # Créer les sous-dossiers nécessaires
    model_folder = os.path.join(human_data_path, "model")
    manual_folder = os.path.join(human_data_path, "manual")
    
    os.makedirs(model_folder, exist_ok=True)
    os.makedirs(manual_folder, exist_ok=True)
    
    return model_folder, manual_folder

def count_admin_data():
    """Compte les données dans chaque section admin"""
    try:
        # Compter les liens visités
        links = load_visited_links()
        sites_count = len(links)
        
        # Compter les prédictions validées
        human_data_path = app.config["HUMAN_DATA_FOLDER"]
        model_folder = os.path.join(human_data_path, "model")
        predictions_count = 0
        if os.path.exists(model_folder):
            predictions_count = len([d for d in os.listdir(model_folder) 
                                   if os.path.isdir(os.path.join(model_folder, d))])
        
        # Compter les annotations manuelles
        manual_folder = os.path.join(human_data_path, "manual")
        manual_count = 0
        if os.path.exists(manual_folder):
            manual_count = len([d for d in os.listdir(manual_folder) 
                               if os.path.isdir(os.path.join(manual_folder, d))])
        
        # Compter les données fine-tune
        fine_tune_data_path = app.config["FINE_TUNE_DATA_FOLDER"]
        fine_tune_count = 0
        if os.path.exists(fine_tune_data_path):
            files = os.listdir(fine_tune_data_path)
            images = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            fine_tune_count = len(images)
        
        return {
            'sites_count': sites_count,
            'predictions_count': predictions_count,
            'manual_count': manual_count,
            'fine_tune_count': fine_tune_count
        }
    except Exception as e:
        print(f"Erreur lors du comptage des données admin: {e}")
        return {
            'sites_count': 0,
            'predictions_count': 0,
            'manual_count': 0,
            'fine_tune_count': 0
        }

def save_validated_prediction_to_human_data(capture_id, kept_box_ids):
    """Sauvegarde une prédiction validée dans human_data/model"""
    try:
        human_data_path = app.config["HUMAN_DATA_FOLDER"]
        model_folder = os.path.join(human_data_path, "model", capture_id)
        os.makedirs(model_folder, exist_ok=True)
        
        # Copier l'image originale
        original_image_path = os.path.join(app.config["ORIGINALS_FOLDER"], f"{capture_id}.png")
        target_image_path = os.path.join(model_folder, f"{capture_id}.png")
        if os.path.exists(original_image_path):
            shutil.copy2(original_image_path, target_image_path)
        
        # Filtrer et sauvegarder les prédictions en format COCO
        json_pred_path = os.path.join(app.config["PREDICTIONS_SCALED_FOLDER"], f"{capture_id}.json")
        if os.path.exists(json_pred_path):
            with open(json_pred_path, "r") as f:
                pred_data = json.load(f)
            
            # Filtrer selon les boîtes gardées
            filtered_annotations = []
            for ann in pred_data.get("annotations", []):
                box_id = f"box{ann['id']}"
                if box_id in kept_box_ids:
                    filtered_annotations.append(ann)
            
            # Créer le JSON COCO complet
            coco_data = {
                "images": [{
                    "id": capture_id,
                    "width": 1280,
                    "height": 1024,
                    "file_name": f"{capture_id}.png"
                }],
                "annotations": filtered_annotations,
                "categories": [
                    {"id": i+1, "name": class_name} 
                    for i, class_name in enumerate(app.config.get("THING_CLASSES", []))
                ]
            }
            
            target_json_path = os.path.join(model_folder, f"{capture_id}_coco.json")
            with open(target_json_path, "w", encoding='utf-8') as f:
                json.dump(coco_data, f, indent=2, ensure_ascii=False)
        
        return True
        
    except Exception as e:
        print(f"Erreur lors de la sauvegarde de la prédiction validée: {e}")
        return False

def validate_training_data():
    """Valide que les données d'entraînement sont correctes"""
    fine_tune_data_path = app.config["FINE_TUNE_DATA_FOLDER"]
    errors = []
    warnings = []
    
    if not os.path.exists(fine_tune_data_path):
        errors.append("Dossier fine_tune_data inexistant")
        return errors, warnings
    
    files = os.listdir(fine_tune_data_path)
    images = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    jsons = [f for f in files if f.lower().endswith('.json')]
    
    if len(images) == 0:
        errors.append("Aucune image trouvée")
    
    if len(jsons) == 0:
        errors.append("Aucun fichier JSON d'annotation trouvé")
    
    if len(images) < 10:
        warnings.append(f"Peu d'images ({len(images)}). Recommandé: au moins 50 pour un bon entraînement")
    
    # Vérifier les paires image/json
    image_stems = {os.path.splitext(f)[0] for f in images}
    json_stems = {os.path.splitext(f)[0].replace('_coco', '') for f in jsons}
    
    missing_jsons = image_stems - json_stems
    missing_images = json_stems - image_stems
    
    if missing_jsons:
        errors.append(f"Images sans annotations: {', '.join(missing_jsons)}")
    
    if missing_images:
        warnings.append(f"Annotations sans images: {', '.join(missing_images)}")
    
    return errors, warnings

def cleanup_old_temp_files():
    """Nettoie les fichiers temporaires anciens"""
    try:
        temp_folders = [
            app.config.get("ANNOTATED_FOLDER"),
            app.config.get("PREDICTIONS_RAW_FOLDER"),
            app.config.get("PREDICTIONS_SCALED_FOLDER"),
            SUPPRESSION_HUMAN_FOLDER
        ]
        
        # Supprimer les fichiers de plus de 7 jours
        current_time = time.time()
        week_ago = current_time - (7 * 24 * 60 * 60)
        
        for folder in temp_folders:
            if folder and os.path.exists(folder):
                for filename in os.listdir(folder):
                    file_path = os.path.join(folder, filename)
                    if os.path.isfile(file_path):
                        if os.path.getctime(file_path) < week_ago:
                            try:
                                os.remove(file_path)
                                print(f"Fichier temporaire supprimé: {file_path}")
                            except Exception as e:
                                print(f"Erreur suppression {file_path}: {e}")
    except Exception as e:
        print(f"Erreur lors du nettoyage: {e}")

def initialize_app_structure():
    """Initialise la structure de l'application au démarrage"""
    try:
        # Assurer la structure des dossiers
        ensure_human_data_structure()
        
        # Nettoyer les anciens fichiers temporaires
        cleanup_old_temp_files()
        
        print("✅ Structure de l'application initialisée avec succès")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation: {e}")

# ═══════════════════════════════════════════════════════════════════
# VARIABLES ET CONFIGURATION (APRÈS TES EXISTING VARIABLES)
# ═══════════════════════════════════════════════════════════════════

# NLP
nlp_system = CompleteOCRQASystem(language='french', ocr_lang='fr')

# Vérification initiale (garde ton code existant)
required_configs = [
    'ORIGINALS_FOLDER', 'RESIZED_FOLDER', 'ANNOTATED_FOLDER',
    'PREDICTIONS_RAW_FOLDER', 'PREDICTIONS_SCALED_FOLDER',
    'HUMAN_DATA_FOLDER', 'FINE_TUNE_DATA_FOLDER'
]

for config_key in required_configs:
    if config_key not in app.config:
        raise RuntimeError(f"Configuration manquante: {config_key}")

# Ensure data directories exist (garde ton code existant)
for folder_key in ["ORIGINALS_FOLDER", "RESIZED_FOLDER", "ANNOTATED_FOLDER", 
                   "PREDICTIONS_RAW_FOLDER", "PREDICTIONS_SCALED_FOLDER", 
                   "HUMAN_DATA_FOLDER", "FINE_TUNE_DATA_FOLDER"]:
    os.makedirs(app.config[folder_key], exist_ok=True)

# Ensure visited links file exists (garde ton code existant)
if not os.path.exists(app.config["VISITED_LINKS_FILE"]):
    with open(app.config["VISITED_LINKS_FILE"], 'w') as f:
        json.dump([], f)

# Folder used to store images filtered manually by users (garde ton code existant)
SUPPRESSION_HUMAN_FOLDER = os.path.join(app.root_path, "data", "suppression_human")
os.makedirs(SUPPRESSION_HUMAN_FOLDER, exist_ok=True)

# Initialiser la structure au démarrage
initialize_app_structure()

# ════════════════════════════════════════════════════════════════


# Placeholder for authentication check
def is_admin_logged_in():
    return session.get("admin_logged_in", False)

# --- Routes --- #

@app.route("/")
def index():
    # Page 1: Welcome page with role selection
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    # Page 1.2: Admin login page
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        admin_email = current_app.config.get("ADMIN_EMAIL")
        admin_password = current_app.config.get("ADMIN_PASSWORD")
        if email == admin_email and password == admin_password:
            session["admin_logged_in"] = True
            flash("Login successful!", "success")
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Invalid credentials.", "danger")
            # Return to login page on failure
            return render_template("login.html")
    # Render login page for GET request
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("admin_logged_in", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))

# REMPLACE ta route admin_dashboard existante par celle-ci :
@app.route("/admin/dashboard")
def admin_dashboard():
    """Page 1.2.1: Admin dashboard avec statistiques"""
    if not is_admin_logged_in():
        flash("Veuillez vous connecter pour accéder à cette page.", "warning")
        return redirect(url_for("login"))
    
    # Assurer la structure des dossiers
    ensure_human_data_structure()
    
    # Obtenir les statistiques
    stats = count_admin_data()
    
    return render_template("admin_dashboard.html", stats=stats)


@app.route("/admin/visited_links")
def admin_visited_links():
    # Page 1.2.1.1: Display visited links
    if not is_admin_logged_in():
        flash("Please log in to access this page.", "warning")
        return redirect(url_for("login"))
    
    links = load_visited_links()
    # Render the template, passing the links data
    return render_template("admin_visited_links.html", links=links)

# Routes administrateur manquantes à ajouter dans ton fichier routes.py

# ===============================
# PAGE 1.2.1.2 - Images prédictions validées
# ===============================
@app.route("/admin/predictions_validees")
def admin_predictions_validees():
    """Page 1.2.1.2: Afficher les images annotées des prédictions validées par human feedback"""
    if not is_admin_logged_in():
        flash("Veuillez vous connecter pour accéder à cette page.", "warning")
        return redirect(url_for("login"))
    
    human_data_path = app.config["HUMAN_DATA_FOLDER"]
    items_predictions = []
    
    try:
        # Chercher les dossiers de prédictions validées
        model_folder = os.path.join(human_data_path, "model")
        if os.path.exists(model_folder):
            for item in os.listdir(model_folder):
                item_path = os.path.join(model_folder, item)
                if os.path.isdir(item_path):
                    image_file = f"{item}.png"
                    json_file = f"{item}_coco.json"
                    image_path = os.path.join(item_path, image_file)
                    json_path = os.path.join(item_path, json_file)
                    
                    if os.path.exists(image_path) and os.path.exists(json_path):
                        items_predictions.append({
                            "id": item,
                            "image_filename": image_file,
                            "json_filename": json_file,
                            "timestamp": os.path.getctime(image_path)
                        })
        
        # Trier par date de création (plus récent en premier)
        items_predictions.sort(key=lambda x: x["timestamp"], reverse=True)
        
    except Exception as e:
        flash(f"Erreur lors du chargement des prédictions validées: {e}", "danger")
    
    return render_template("admin_predictions_validees.html", items=items_predictions)


@app.route("/admin/prediction_detail/<item_id>")
def admin_prediction_detail(item_id):
    """Page 1.2.1.2.1: Détail d'une prédiction validée"""
    if not is_admin_logged_in():
        flash("Veuillez vous connecter pour accéder à cette page.", "warning")
        return redirect(url_for("login"))
    
    human_data_path = app.config["HUMAN_DATA_FOLDER"]
    model_folder = os.path.join(human_data_path, "model", item_id)
    
    if not os.path.exists(model_folder):
        flash(f"Prédiction {item_id} non trouvée.", "danger")
        return redirect(url_for("admin_predictions_validees"))
    
    image_filename = f"{item_id}.png"
    json_filename = f"{item_id}_coco.json"
    image_path = os.path.join(model_folder, image_filename)
    json_path = os.path.join(model_folder, json_filename)
    
    if not os.path.exists(image_path) or not os.path.exists(json_path):
        flash(f"Fichiers manquants pour la prédiction {item_id}.", "danger")
        return redirect(url_for("admin_predictions_validees"))
    
    # Charger les informations JSON pour affichage
    json_info = {}
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
            json_info = {
                "nb_annotations": len(json_data.get("annotations", [])),
                "categories": len(json_data.get("categories", [])),
                "image_info": json_data.get("images", [{}])[0]
            }
    except Exception as e:
        json_info = {"error": f"Erreur lecture JSON: {e}"}
    
    image_url = url_for("serve_human_data_prediction", item_id=item_id, filename=image_filename)
    
    return render_template("admin_prediction_detail.html", 
                         item_id=item_id,
                         image_url=image_url,
                         json_info=json_info)


@app.route("/admin/validate_prediction/<item_id>", methods=["POST"])
def admin_validate_prediction(item_id):
    """Valider et déplacer vers fine_tune_data"""
    if not is_admin_logged_in():
        flash("Veuillez vous connecter pour effectuer cette action.", "warning")
        return redirect(url_for("login"))
    
    human_data_path = app.config["HUMAN_DATA_FOLDER"]
    fine_tune_data_path = app.config["FINE_TUNE_DATA_FOLDER"]
    
    src_folder = os.path.join(human_data_path, "model", item_id)
    
    if not os.path.exists(src_folder):
        flash(f"Prédiction {item_id} non trouvée.", "danger")
        return redirect(url_for("admin_predictions_validees"))
    
    try:
        # Créer le dossier fine_tune_data s'il n'existe pas
        os.makedirs(fine_tune_data_path, exist_ok=True)
        
        # Déplacer tous les fichiers du dossier
        for filename in os.listdir(src_folder):
            src_file = os.path.join(src_folder, filename)
            dst_file = os.path.join(fine_tune_data_path, filename)
            shutil.move(src_file, dst_file)
        
        # Supprimer le dossier vide
        os.rmdir(src_folder)
        
        flash(f"Prédiction {item_id} validée et déplacée vers fine_tune_data.", "success")
        
    except Exception as e:
        flash(f"Erreur lors de la validation: {e}", "danger")
    
    return redirect(url_for("admin_predictions_validees"))


@app.route("/admin/delete_prediction/<item_id>", methods=["POST"])
def admin_delete_prediction(item_id):
    """Supprimer une prédiction"""
    if not is_admin_logged_in():
        flash("Veuillez vous connecter pour effectuer cette action.", "warning")
        return redirect(url_for("login"))
    
    human_data_path = app.config["HUMAN_DATA_FOLDER"]
    src_folder = os.path.join(human_data_path, "model", item_id)
    
    try:
        if os.path.exists(src_folder):
            shutil.rmtree(src_folder)
            flash(f"Prédiction {item_id} supprimée.", "success")
        else:
            flash(f"Prédiction {item_id} non trouvée.", "warning")
    except Exception as e:
        flash(f"Erreur lors de la suppression: {e}", "danger")
    
    return redirect(url_for("admin_predictions_validees"))


# ===============================
# PAGE 1.2.1.3 - Annotations manuelles validées
# ===============================
@app.route("/admin/annotations_manuelles")
def admin_annotations_manuelles():
    """Page 1.2.1.3: Afficher les images annotées manuellement par l'utilisateur"""
    if not is_admin_logged_in():
        flash("Veuillez vous connecter pour accéder à cette page.", "warning")
        return redirect(url_for("login"))
    
    human_data_path = app.config["HUMAN_DATA_FOLDER"]
    items_manuelles = []
    
    try:
        # Chercher les dossiers d'annotations manuelles
        manual_folder = os.path.join(human_data_path, "manual")
        if os.path.exists(manual_folder):
            for item in os.listdir(manual_folder):
                item_path = os.path.join(manual_folder, item)
                if os.path.isdir(item_path):
                    image_file = f"{item}.png"
                    json_file = f"{item}_coco.json"
                    image_path = os.path.join(item_path, image_file)
                    json_path = os.path.join(item_path, json_file)
                    
                    if os.path.exists(image_path) and os.path.exists(json_path):
                        items_manuelles.append({
                            "id": item,
                            "image_filename": image_file,
                            "json_filename": json_file,
                            "timestamp": os.path.getctime(image_path)
                        })
        
        # Trier par date de création (plus récent en premier)
        items_manuelles.sort(key=lambda x: x["timestamp"], reverse=True)
        
    except Exception as e:
        flash(f"Erreur lors du chargement des annotations manuelles: {e}", "danger")
    
    return render_template("admin_annotations_manuelles.html", items=items_manuelles)


@app.route("/admin/annotation_manuelle_detail/<item_id>")
def admin_annotation_manuelle_detail(item_id):
    """Page 1.2.1.3.1: Détail d'une annotation manuelle"""
    if not is_admin_logged_in():
        flash("Veuillez vous connecter pour accéder à cette page.", "warning")
        return redirect(url_for("login"))
    
    human_data_path = app.config["HUMAN_DATA_FOLDER"]
    manual_folder = os.path.join(human_data_path, "manual", item_id)
    
    if not os.path.exists(manual_folder):
        flash(f"Annotation manuelle {item_id} non trouvée.", "danger")
        return redirect(url_for("admin_annotations_manuelles"))
    
    image_filename = f"{item_id}.png"
    json_filename = f"{item_id}_coco.json"
    image_path = os.path.join(manual_folder, image_filename)
    json_path = os.path.join(manual_folder, json_filename)
    
    if not os.path.exists(image_path) or not os.path.exists(json_path):
        flash(f"Fichiers manquants pour l'annotation {item_id}.", "danger")
        return redirect(url_for("admin_annotations_manuelles"))
    
    # Charger les informations JSON pour affichage
    json_info = {}
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
            json_info = {
                "nb_annotations": len(json_data.get("annotations", [])),
                "categories": len(json_data.get("categories", [])),
                "image_info": json_data.get("images", [{}])[0]
            }
    except Exception as e:
        json_info = {"error": f"Erreur lecture JSON: {e}"}
    
    image_url = url_for("serve_human_data_manual", item_id=item_id, filename=image_filename)
    
    return render_template("admin_annotation_manuelle_detail.html", 
                         item_id=item_id,
                         image_url=image_url,
                         json_info=json_info)


@app.route("/admin/validate_annotation_manuelle/<item_id>", methods=["POST"])
def admin_validate_annotation_manuelle(item_id):
    """Valider et déplacer annotation manuelle vers fine_tune_data"""
    if not is_admin_logged_in():
        flash("Veuillez vous connecter pour effectuer cette action.", "warning")
        return redirect(url_for("login"))
    
    human_data_path = app.config["HUMAN_DATA_FOLDER"]
    fine_tune_data_path = app.config["FINE_TUNE_DATA_FOLDER"]
    
    src_folder = os.path.join(human_data_path, "manual", item_id)
    
    if not os.path.exists(src_folder):
        flash(f"Annotation manuelle {item_id} non trouvée.", "danger")
        return redirect(url_for("admin_annotations_manuelles"))
    
    try:
        # Créer le dossier fine_tune_data s'il n'existe pas
        os.makedirs(fine_tune_data_path, exist_ok=True)
        
        # Déplacer tous les fichiers du dossier
        for filename in os.listdir(src_folder):
            src_file = os.path.join(src_folder, filename)
            dst_file = os.path.join(fine_tune_data_path, filename)
            shutil.move(src_file, dst_file)
        
        # Supprimer le dossier vide
        os.rmdir(src_folder)
        
        flash(f"Annotation manuelle {item_id} validée et déplacée vers fine_tune_data.", "success")
        
    except Exception as e:
        flash(f"Erreur lors de la validation: {e}", "danger")
    
    return redirect(url_for("admin_annotations_manuelles"))


@app.route("/admin/delete_annotation_manuelle/<item_id>", methods=["POST"])
def admin_delete_annotation_manuelle(item_id):
    """Supprimer une annotation manuelle"""
    if not is_admin_logged_in():
        flash("Veuillez vous connecter pour effectuer cette action.", "warning")
        return redirect(url_for("login"))
    
    human_data_path = app.config["HUMAN_DATA_FOLDER"]
    src_folder = os.path.join(human_data_path, "manual", item_id)
    
    try:
        if os.path.exists(src_folder):
            shutil.rmtree(src_folder)
            flash(f"Annotation manuelle {item_id} supprimée.", "success")
        else:
            flash(f"Annotation manuelle {item_id} non trouvée.", "warning")
    except Exception as e:
        flash(f"Erreur lors de la suppression: {e}", "danger")
    
    return redirect(url_for("admin_annotations_manuelles"))


# ===============================
# PAGE 1.2.1.4 - Fine tune data et lancement
# ===============================
@app.route("/admin/fine_tune_management")
def admin_fine_tune_management():
    """Page 1.2.1.4: Gestion du fine-tuning"""
    if not is_admin_logged_in():
        flash("Veuillez vous connecter pour accéder à cette page.", "warning")
        return redirect(url_for("login"))
    
    fine_tune_data_path = app.config["FINE_TUNE_DATA_FOLDER"]
    
    # Compter les images et fichiers JSON
    image_count = 0
    json_count = 0
    files_info = []
    
    try:
        if os.path.exists(fine_tune_data_path):
            all_files = os.listdir(fine_tune_data_path)
            
            for filename in all_files:
                file_path = os.path.join(fine_tune_data_path, filename)
                if os.path.isfile(file_path):
                    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                        image_count += 1
                        files_info.append({
                            "name": filename,
                            "type": "image",
                            "size": os.path.getsize(file_path),
                            "timestamp": os.path.getctime(file_path)
                        })
                    elif filename.lower().endswith('.json'):
                        json_count += 1
                        files_info.append({
                            "name": filename,
                            "type": "json",
                            "size": os.path.getsize(file_path),
                            "timestamp": os.path.getctime(file_path)
                        })
        
        # Trier par timestamp (plus récent en premier)
        files_info.sort(key=lambda x: x["timestamp"], reverse=True)
        
    except Exception as e:
        flash(f"Erreur lors du scan du dossier fine_tune_data: {e}", "danger")
    
    return render_template("admin_fine_tune_management.html", 
                         image_count=image_count,
                         json_count=json_count,
                         files_info=files_info)


@app.route("/admin/launch_fine_tuning", methods=["POST"])
def admin_launch_fine_tuning():
    """Lancer le processus de fine-tuning"""
    if not is_admin_logged_in():
        flash("Veuillez vous connecter pour effectuer cette action.", "warning")
        return redirect(url_for("login"))
    
    fine_tune_data_path = app.config["FINE_TUNE_DATA_FOLDER"]
    
    try:
        # Vérifier qu'il y a des données
        if not os.path.exists(fine_tune_data_path):
            flash("Aucun dossier fine_tune_data trouvé.", "danger")
            return redirect(url_for("admin_fine_tune_management"))
        
        files = os.listdir(fine_tune_data_path)
        if not files:
            flash("Aucun fichier dans fine_tune_data.", "warning")
            return redirect(url_for("admin_fine_tune_management"))
        
        # Ici tu peux ajouter ton code de fine-tuning
        # Pour l'instant, on simule le processus
        
        # Créer un dossier de backup avant de supprimer
        backup_folder = os.path.join(app.root_path, "data", "fine_tune_backup")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_folder, f"backup_{timestamp}")
        os.makedirs(backup_path, exist_ok=True)
        
        # Déplacer les fichiers vers le backup
        for filename in files:
            src = os.path.join(fine_tune_data_path, filename)
            dst = os.path.join(backup_path, filename)
            shutil.move(src, dst)
        
        flash(f"Fine-tuning lancé ! {len(files)} fichiers traités et sauvegardés dans backup_{timestamp}.", "success")
        
        # TODO: Ajouter ici ton code de fine-tuning réel
        # import ton_module_fine_tuning
        # ton_module_fine_tuning.lancer_entrainement(backup_path)
        
    except Exception as e:
        flash(f"Erreur lors du lancement du fine-tuning: {e}", "danger")
    
    return redirect(url_for("admin_fine_tune_management"))


# ===============================
# Routes pour servir les images
# ===============================
@app.route("/data/human_data/prediction/<item_id>/<filename>")
def serve_human_data_prediction(item_id, filename):
    """Servir les images des prédictions validées"""
    human_data_path = app.config["HUMAN_DATA_FOLDER"]
    folder_path = os.path.join(human_data_path, "model", item_id)
    return send_from_directory(folder_path, filename)


@app.route("/data/human_data/manual/<item_id>/<filename>")
def serve_human_data_manual(item_id, filename):
    """Servir les images des annotations manuelles"""
    human_data_path = app.config["HUMAN_DATA_FOLDER"]
    folder_path = os.path.join(human_data_path, "manual", item_id)
    return send_from_directory(folder_path, filename)


@app.route("/data/fine_tune_data/<filename>")
def serve_fine_tune_data(filename):
    """Servir les fichiers du dossier fine_tune_data"""
    return send_from_directory(app.config["FINE_TUNE_DATA_FOLDER"], filename)
# --- User Routes --- #

@app.route("/data/human_data/<filename>")
def serve_human_data_image(filename):
    # Serves images stored in the human_data folder
    return send_from_directory(app.config["HUMAN_DATA_FOLDER"], filename)


@app.route("/user/capture", methods=["GET", "POST"])
def user_capture():
    if request.method == "POST":
        url = request.form.get("url")
        if not url or not validators.url(url):
            flash("Veuillez entrer une URL valide.", "warning")
            return redirect(url_for("user_capture"))

        try:
            # Configuration Playwright robuste
            playwright_params = {
                "headless": True,
                "timeout": 30000  # 30 secondes timeout
            }

            with sync_playwright() as p:
                browser = p.chromium.launch(**playwright_params)
                context = browser.new_context(
                    viewport={"width": 1280, "height": 1024},
                    java_script_enabled=True
                )
                page = context.new_page()
                
                page.goto(url, wait_until="load", timeout=30000)
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(2000)

                # Génération nom de fichier + ID
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{timestamp}_{uuid.uuid4().hex}.png"
                capture_id = filename.split(".")[0]
                filepath = os.path.join(app.config["ORIGINALS_FOLDER"], filename)

                page.screenshot(path=filepath, full_page=True)
                context.close()
                browser.close()

            # Sauvegarde dans l'historique
            links = load_visited_links()
            links.append({
                "url": url,
                "filename": filename,
                "capture_id": capture_id,
                "timestamp": datetime.now().isoformat()
            })
            save_visited_links(links)

            flash(f"Capture réussie: {filename}", "success")
            return redirect(url_for("user_display_capture", filename=filename))

        except Exception as e:
            flash(f"Échec de capture: {str(e)}", "danger")
            return redirect(url_for("user_capture"))

    return render_template("user_capture.html")

@app.route("/user/question_nlp/<capture_id>", methods=["GET", "POST"])
def user_question_nlp(capture_id):
    image_path = os.path.join(app.config["ORIGINALS_FOLDER"], f"{capture_id}.png")

    capture_info = find_capture_by_id(capture_id)
    # === 1. Récupérer le nom du fichier image
    image_filename = f"{capture_info['capture_id']}.png"

    # === 2. Déterminer le chemin absolu réel (pour OCR)
    absolute_image_path = os.path.join(app.config["ORIGINALS_FOLDER"], image_filename)

    # === 3. Traiter l'image pour l'OCR/NLP (une seule fois)
    nlp_system.process_image(absolute_image_path, use_layout=True)

    answer = None
    question = None

    if request.method == "POST":
        question = request.form.get("question", "").strip()
        if question:
            answer = nlp_system.ask_question(question)

    return render_template("user_question.html", capture_id=capture_id, question=question, answer=answer)


@app.route("/user/question_chatgpt/<capture_id>", methods=["GET", "POST"])
def user_question_chatgpt(capture_id):
    image_filename = f"{capture_id}.png"
    absolute_image_path = os.path.join(app.config["ORIGINALS_FOLDER"], image_filename)

    nlp_system.process_image(absolute_image_path, use_layout=True)
    context_text = " ".join(nlp_system.qa_system.sentences)

    answer = None
    question = None

    if request.method == "POST":
        question = request.form.get("question", "").strip()
        if question:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                answer = "Clé API OpenAI manquante"
            else:
                try:
                    client = openai.OpenAI(api_key=api_key)
                    prompt = f"{context_text}\n\nQuestion: {question}\nRéponds en français :"
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": prompt}]
                    )
                    answer = response.choices[0].message.content.strip()
                except Exception as e:
                    answer = f"Erreur OpenAI : {e}"

    return render_template("user_question.html", capture_id=capture_id, question=question, answer=answer)

import requests

@app.route("/user/question_local_llm/<capture_id>", methods=["GET", "POST"])
def user_question_local_llm(capture_id):
    image_filename = f"{capture_id}.png"
    absolute_image_path = os.path.join(app.config["ORIGINALS_FOLDER"], image_filename)

    nlp_system.process_image(absolute_image_path, use_layout=True)
    context_text = " ".join(nlp_system.qa_system.sentences)

    answer = None
    question = None

    if request.method == "POST":
        question = request.form.get("question", "").strip()
        if question:
            prompt = f"{context_text}\n\nQuestion : {question}\nRéponds en français :"

            try:
                response = requests.post("http://localhost:11434/api/chat", json={
                    "model": "mistral",
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": False  # ✅ important !
                })

                data = response.json()
                print("Réponse JSON complète :", data)
                answer = data.get('message', {}).get('content') or data.get('response', '').strip()

            except Exception as e:
                answer = f"Erreur LLM local : {e}"


    return render_template("user_question.html", capture_id=capture_id, question=question, answer=answer)

@app.route("/user/question_choice/<capture_id>")
def user_question_choice(capture_id):
    return render_template("user_question_choice.html", capture_id=capture_id)



@app.route("/user/display/<filename>")
def user_display_capture(filename):
    # Page 1.1.2: Affichage de la capture
    capture_info = find_capture_by_id(filename)
    if not capture_info:
        flash("Capture non trouvée.", "danger")
        return redirect(url_for("user_capture"))

    # Ajoute capture_id si absent
    if "capture_id" not in capture_info:
        capture_info["capture_id"] = capture_info["filename"].split(".")[0]

    # === 1. Récupérer le nom du fichier image
    image_filename = f"{capture_info['capture_id']}.png"


    # === 4. Générer le lien URL pour affichage dans la page HTML
    image_path = url_for("serve_original_image", filename=image_filename)

    return render_template("user_display_capture.html",
                           capture_info=capture_info,
                           image_path=image_path)



@app.route("/user/save_options/<capture_id>")
def user_save_options(capture_id):
    # Page 1.1.2.2: Modifications ?
    capture_info = find_capture_by_id(capture_id)
    if not capture_info:
        flash("Capture non trouvée.", "danger")
        return redirect(url_for("user_capture"))

    if "capture_id" not in capture_info:
        capture_info["capture_id"] = capture_info["filename"].split(".")[0]

    image_filename = capture_info["filename"]
    image_path = url_for("serve_original_image", filename=image_filename)

    return render_template("user_save_options.html", capture_info=capture_info, image_path=image_path)


@app.route("/data/originals/<filename>")
def serve_original_image(filename):
    return send_from_directory(os.path.join(app.root_path, "data", "originals"), filename)


@app.route("/data/annotated/<filename>")
def serve_annotated_image(filename):
    return send_from_directory(app.config["ANNOTATED_FOLDER"], filename)


# 🔧 Utilitaire : accepte capture_id ou filename
def find_capture_by_id(capture_id_or_filename):
    links = load_visited_links()
    for link in links:
        if link.get("capture_id") == capture_id_or_filename:
            return link
        if link.get("filename") == capture_id_or_filename:
            return link
    return None


@app.route("/user/download_original/<capture_id>")
def user_download_original(capture_id):
    # Page Tn: Show original capture and allow download
    capture_info = find_capture_by_id(capture_id)
    if not capture_info:
        flash("Capture non trouvée.", "danger")
        return redirect(url_for("user_capture"))

    image_filename = capture_info.get("filename")
    image_path = url_for("serve_original_image", filename=image_filename)

    # Render the template for downloading the original image
    return render_template("user_download_original.html", capture_info=capture_info, image_path=image_path)

# ✅ Nouvelle version de la route : annotation d'une image longue via slicing compatible training
@app.route("/user/annotate_model/<capture_id>")
def user_annotate_model(capture_id):
    capture_info = find_capture_by_id(capture_id)
    if not capture_info:
        flash("Capture non trouvée.", "danger")
        return redirect(url_for("user_capture"))

    import cv2, json, numpy as np
    from detectron2.config import get_cfg
    from detectron2.engine import DefaultPredictor
    from detectron2 import model_zoo
    from detectron2.data import MetadataCatalog

    original_image_path = os.path.join(app.config["ORIGINALS_FOLDER"], capture_info["filename"])
    annotated_image_filename = f"annotated_{capture_info['filename']}"
    annotated_image_path_local = os.path.join(app.config["ANNOTATED_FOLDER"], annotated_image_filename)
    coco_json_path = os.path.join(app.config["PREDICTIONS_SCALED_FOLDER"], f"{capture_id}.json")

    # === 1. Configuration Detectron2 ===
    cfg = get_cfg()
    cfg.merge_from_file(model_zoo.get_config_file("COCO-Detection/faster_rcnn_R_101_FPN_3x.yaml"))
    cfg.OUTPUT_DIR = os.path.join("app", "models")
    cfg.MODEL.WEIGHTS = os.path.join(cfg.OUTPUT_DIR, "best_model.pth")
    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.3
    cfg.MODEL.ROI_HEADS.NUM_CLASSES = 18
    cfg.MODEL.DEVICE = "cpu"
    
    # === 2. Metadata ===
    thing_classes = [
        "advertisement", "chaine", "commentaire", "description", "header", "footer", "left sidebar",
        "logo", "likes", "media", "pop up", "recommendations", "right sidebar", "suggestions",
        "title", "vues", "none access", "other"
    ]
    MetadataCatalog.get("web_custom").thing_classes = thing_classes
    cfg.DATASETS.TEST = ("web_custom",)
    predictor = DefaultPredictor(cfg)

    unique_class_limit = {
        "footer", "header", "chaine", "commentaire", "description",
        "left sidebar", "likes", "recommendations", "vues", "title", "right sidebar"
    }
    to_ignore_classes = { "other", "none access", "suggestions"}

    CLASS_COLORS = {
        "advertisement": (255, 0, 0), "chaine": (0, 255, 0), "commentaire": (0, 0, 255),
        "description": (255, 255, 0), "header": (255, 0, 255), "footer": (0, 255, 255),
        "left sidebar": (128, 0, 0), "logo": (0, 128, 0), "likes": (0, 0, 128),
        "media": (128, 128, 0), "pop up": (128, 0, 128), "recommendations": (0, 128, 128),
        "right sidebar": (64, 0, 0), "suggestions": (0, 64, 0), "title": (0, 0, 64),
        "vues": (64, 64, 0), "none access": (64, 0, 64), "other": (0, 64, 64)
    }

    def slice_image_array(image, max_height=3000, overlap=200):
        h, w = image.shape[:2]
        slices = []
        y = 0
        while y < h:
            end_y = min(y + max_height, h)
            crop = image[y:end_y, :]
            slices.append((crop, y))
            if end_y == h:
                break
            y += max_height - overlap
        return slices

    # === 3. Lecture image & slicing ===
    img = cv2.imread(original_image_path)
    slices = slice_image_array(img)
    annotated = img.copy()
    detected_boxes = []
    annotations = []
    kept = {}
    annotation_id = 1

    for crop, y_offset in slices:
        outputs = predictor(crop)["instances"].to("cpu")
        boxes = outputs.pred_boxes.tensor.numpy()
        labels = outputs.pred_classes.numpy()
        scores = outputs.scores.numpy()

        for i in range(len(boxes)):
            class_id = int(labels[i])
            class_name = thing_classes[class_id]

            x1, y1, x2, y2 = map(int, boxes[i])
            y1 += y_offset
            y2 += y_offset
            if class_name == "pop up":
                class_name = "media"
                class_id = thing_classes.index("media")  # mettre à jour aussi l'ID

            if class_name in ["footer", "header"]:
                if class_name not in kept:
                    kept[class_name] = {"coords": [x1, y1, x2, y2], "score": score, "id": box_id, "class_id": class_id}

            # === Étape 2 : si classe media, vérifier s’il est inclus dans footer/header
            elif class_name == "media":
                def is_inside(inner, outer, margin=10):
                    return (
                        inner[0] >= outer[0] - margin and
                        inner[1] >= outer[1] - margin and
                        inner[2] <= outer[2] + margin and
                        inner[3] <= outer[3] + margin
                    )
                for zone in ["footer", "header"]:
                    if zone in kept:
                        if is_inside([x1, y1, x2, y2], kept[zone]["coords"], margin=10):
                            class_name = "logo"
                            class_id = thing_classes.index("logo")
                            break

                        
            score = float(scores[i])

            if class_name in to_ignore_classes:
                continue

            x1, y1, x2, y2 = map(int, boxes[i])
            y1 += y_offset
            y2 += y_offset

            box_id = f"box{annotation_id}"
            annotation_id += 1

            if class_name in unique_class_limit:
                if class_name in kept and kept[class_name]["score"] >= score:
                    continue
                kept[class_name] = {"coords": [x1, y1, x2, y2], "score": score, "id": box_id, "class_id": class_id}
            else:
                kept[f"{class_name}_{annotation_id}"] = {"coords": [x1, y1, x2, y2], "score": score, "id": box_id, "class_id": class_id}

    for key, val in kept.items():
        x1, y1, x2, y2 = val["coords"]
        color = CLASS_COLORS.get(key.split("_")[0], (0, 255, 0))
        cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
        cv2.putText(annotated, f"{key.split('_')[0]} {val['score']:.2f}", (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

        detected_boxes.append({"id": val["id"], "class": key.split("_")[0], "coords": [x1, y1, x2, y2], "score": val["score"]})
        annotations.append({
            "id": annotation_id,
            "image_id": capture_id,
            "category_id": val["class_id"],
            "bbox": [x1, y1, x2 - x1, y2 - y1],
            "score": val["score"]
        })
        annotation_id += 1

    cv2.imwrite(annotated_image_path_local, annotated)
    annotated_image_path = url_for("serve_annotated_image", filename=annotated_image_filename)

    with open(coco_json_path, "w") as f:
        json.dump({"annotations": annotations}, f, indent=2)

    return render_template("user_annotate_model.html", 
                           capture_info=capture_info, 
                           annotated_image_path=annotated_image_path, 
                           detected_boxes=detected_boxes)



@app.route("/user/process_annotation/<capture_id>", methods=["POST"])
def user_process_annotation(capture_id):
    capture_info = find_capture_by_id(capture_id)
    if not capture_info:
        flash("Capture non trouvée.", "danger")
        return redirect(url_for("user_capture"))

    kept_box_ids = request.form.getlist("keep_box")
    session[f"kept_boxes_{capture_id}"] = kept_box_ids
    flash(f"Choix des boîtes enregistrés ({len(kept_box_ids)} a supprimer). Veuillez donner votre feedback.", "info")

    return redirect(url_for("user_feedback", capture_id=capture_id))

# REMPLACE ta route user_feedback existante par celle-ci :
@app.route("/user/feedback/<capture_id>", methods=["GET", "POST"])
def user_feedback(capture_id):
    capture_info = find_capture_by_id(capture_id)
    if not capture_info:
        flash("Capture non trouvée.", "danger")
        return redirect(url_for("user_capture"))

    image_filename = capture_info.get("filename")
    annotated_image_path = url_for("serve_annotated_image", filename=f"annotated_{image_filename}")

    if request.method == "POST":
        feedback = request.form.get("feedback")
        kept_box_ids = session.get(f"kept_boxes_{capture_id}", [])

        if feedback == "oui":
            # Sauvegarder dans human_data/model
            if save_validated_prediction_to_human_data(capture_id, kept_box_ids):
                flash("Feedback enregistré. Prédiction sauvegardée pour validation admin.", "success")
            else:
                flash("Erreur lors de la sauvegarde de la prédiction.", "warning")
            return redirect(url_for("model_display_final_annotation", capture_id=capture_id, source="model_validated"))

        elif feedback == "non":
            flash("Feedback enregistré. Vous pouvez maintenant annoter manuellement.", "info")
            return redirect(url_for("manual_annotation", capture_id=capture_id))

        flash("Veuillez sélectionner Oui ou Non.", "warning")
        return redirect(url_for("user_feedback", capture_id=capture_id))

    return render_template("user_feedback.html",
                           capture_info=capture_info,
                           annotated_image_path=annotated_image_path)


# ───────────────────────────────
# 📌 Bloc 1 : Annotation manuelle
# ───────────────────────────────
@app.route("/user/manual/annotate/<capture_id>")
def manual_annotation(capture_id):
    capture_info = find_capture_by_id(capture_id)
    if not capture_info:
        flash("Capture non trouvée.", "danger")
        return redirect(url_for("user_capture"))

    image_filename = capture_info["filename"]
    image_id = image_filename.split(".")[0]
    image_url = url_for("serve_original_image", filename=image_filename)

    return render_template("user_manual_annotation.html",
                           capture_id=image_id,
                           image_filename=image_filename,
                           image_url=image_url)

# ───────────────────────────────
# 📌 Bloc 2 : Sauvegarde annotations (COCO + image annotée)
# ───────────────────────────────
@app.route("/user/manual/save", methods=["POST"])
def manual_annotation_save():
    data = request.get_json()
    image_id = data.get("image_id")
    annotations = data.get("annotations")
    
    base_dir = os.path.dirname(current_app.root_path)
    src_image = os.path.join(base_dir, "app", "data", "originals", f"{image_id}.png")
    save_dir = os.path.join(base_dir, "app", "data", "human_data", "manual", image_id)
    os.makedirs(save_dir, exist_ok=True)

    # 🆕 CRÉER AUSSI le dossier pour les images annotées
    annotated_by_human_dir = os.path.join(base_dir, "app", "data", "annoted_by_human")
    os.makedirs(annotated_by_human_dir, exist_ok=True)

    dst_image = os.path.join(save_dir, f"{image_id}.png")
    shutil.copy(src_image, dst_image)

    json_path = os.path.join(save_dir, f"{image_id}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(annotations, f, indent=2, ensure_ascii=False)

    # 📦 COCO format
    coco_path = os.path.join(save_dir, f"{image_id}_coco.json")
    save_annotations_as_coco(image_id, annotations, dst_image, coco_path)

    # 🎯 CORRECTION: Dessiner les boîtes sur l'image avec CV2
    image_out = os.path.join(annotated_by_human_dir, f"annotated_{image_id}.jpg")
    print(f"[DEBUG] Création image annotée: {image_out}")
    
    # ✅ Utiliser l'image source originale, pas la copie
    success = draw_boxes_cv2(src_image, annotations, image_out)
    
    if success:
        print(f"[SUCCESS] Image annotée créée: {image_out}")
    else:
        print(f"[ERROR] Échec création image annotée: {image_out}")

    redirect_url = url_for("manual_boxes_review", capture_id=image_id)
    return jsonify({"status": "success", "redirect": redirect_url})

# ───────────────────────────────
# 📌 Bloc 3 : Sélection des boîtes à conserver (review)
# ───────────────────────────────
@app.route("/user/manual/review/<capture_id>", methods=["GET", "POST"])
def manual_boxes_review(capture_id):
    base_dir = os.path.dirname(current_app.root_path)
    ann_dir = os.path.join(base_dir, "app", "data", "human_data", "manual", capture_id)
    json_path = os.path.join(ann_dir, f"{capture_id}.json")
    img_path = os.path.join(ann_dir, f"{capture_id}.png")
    
    # ✅ Chemin de l'image annotée visuellement
    annotated_visual_path = os.path.join(base_dir, "app", "data", "annoted_by_human", f"annotated_{capture_id}.jpg")

    print(f"[DEBUG] manual_boxes_review - capture_id: {capture_id}")
    print(f"[DEBUG] JSON path: {json_path} (exists: {os.path.exists(json_path)})")
    print(f"[DEBUG] Image path: {img_path} (exists: {os.path.exists(img_path)})")
    print(f"[DEBUG] Annotated visual path: {annotated_visual_path} (exists: {os.path.exists(annotated_visual_path)})")

    if not os.path.exists(json_path) or not os.path.exists(img_path):
        flash("Fichiers manquants pour l'annotation manuelle.", "danger")
        return redirect(url_for("user_capture"))

    # ✅ Vérifier si l'image annotée existe, sinon la recréer
    if not os.path.exists(annotated_visual_path):
        print(f"[WARNING] Image annotée manquante, recréation...")
        try:
            with open(json_path, "r") as f:
                annotations = json.load(f)
            
            # Recréer l'image annotée
            success = draw_boxes_cv2(img_path, annotations, annotated_visual_path)
            if success:
                print(f"[SUCCESS] Image annotée recréée: {annotated_visual_path}")
            else:
                print(f"[ERROR] Échec recréation image annotée")
        except Exception as e:
            print(f"[ERROR] Erreur recréation image: {e}")

    if request.method == "POST":
        kept_ids = request.form.getlist("keep_manual_box")
        with open(json_path, "r") as f:
            annotations = json.load(f)

        filtered = [ann for ann in annotations if str(ann.get("id")) in kept_ids]
        with open(json_path, "w") as f:
            json.dump(filtered, f, indent=2)

        # 🧽 Nettoyage des zones supprimées
        output_path = os.path.join(SUPPRESSION_HUMAN_FOLDER, f"{capture_id}_filtered.jpg")
        remove_zones_from_image(img_path, filtered, output_path)

        return redirect(url_for("manual_display_final_annotation", capture_id=capture_id))

    # → GET: Charger les annotations pour affichage
    with open(json_path, "r") as f:
        annotations = json.load(f)

    return render_template("user_manual_remove_boxes.html",
                           capture_info=find_capture_by_id(capture_id),
                           annotated_image_path=url_for("serve_manual_annotated_image", filename=f"annotated_{capture_id}.jpg"),
                           manual_boxes=[{
                               "id": str(ann.get("id")),
                               "class": ann.get("value", {}).get("rectanglelabels", ["?"])[0]
                           } for ann in annotations])


@app.route("/user/manual/serve_filtered/<filename>")
def serve_filtered_manual_image(filename):

    image_path = os.path.join(SUPPRESSION_HUMAN_FOLDER, filename)

    if not os.path.exists(image_path):
        print("[404] Image filtrée manuelle introuvable :", image_path)
        abort(404)

    return send_file(image_path, mimetype="image/jpeg")


# ───────────────────────────────
# 📌 Bloc 4 : Affichage de l’image finale filtrée
# ───────────────────────────────
# ───────────────────────────────
# 📌 Bloc 4 : Affichage de l’image finale filtrée (après feedback = NON)
# ───────────────────────────────
@app.route("/user/manual/final_display/<capture_id>")
def manual_display_final_annotation(capture_id):

    capture_info = find_capture_by_id(capture_id)
    if not capture_info:
        flash("Capture non trouvée.", "danger")
        return redirect(url_for("user_capture"))

    base_dir = os.path.dirname(current_app.root_path)
    ann_dir = os.path.join(base_dir, "app", "data", "human_data", "manual", capture_id)
    json_path = os.path.join(ann_dir, f"{capture_id}.json")
    img_path = os.path.join(ann_dir, f"{capture_id}.png")

    output_filename = f"{capture_id}_filtered.jpg"
    output_path = os.path.join(SUPPRESSION_HUMAN_FOLDER, output_filename)

    try:
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"[ERREUR] Annotations JSON manquantes : {json_path}")

        if not os.path.exists(img_path):
            raise FileNotFoundError(f"[ERREUR] Image source manquante : {img_path}")

        with open(json_path, "r", encoding='utf-8') as f:
            annotations = json.load(f)

        image = cv2.imread(img_path)
        if image is None:
            raise ValueError(f"Impossible de lire l'image : {img_path}")

        h, w = image.shape[:2]
        for ann in annotations:
            value = ann.get("value") or ann.get("result", [{}])[0].get("value", {})
            x = int(value["x"] / 100 * w)
            y = int(value["y"] / 100 * h)
            bw = int(value["width"] / 100 * w)
            bh = int(value["height"] / 100 * h)
            image[y:y + bh, x:x + bw] = 255  # suppression en blanc

        image = remove_uniform_bands(image)
        saved = cv2.imwrite(output_path, image)
        print("[DEBUG] Image nettoyée sauvegardée :", output_path)

        if not saved:
            raise IOError(f"Échec de sauvegarde de l’image nettoyée : {output_path}")

    except Exception as e:
        flash(f"Erreur lors de la suppression : {str(e)}", "danger")
        output_path = img_path
        output_filename = f"{capture_id}.png"

    return render_template("user_display_final_annotation.html",
                           capture_info=capture_info,
                           annotated_image_path=url_for("serve_filtered_manual_image", filename=output_filename),
                           download_filename=output_filename,
                           source="manual_edited")

# ───────────────────────────────
# 📌 Bloc 5 : Téléchargement de l’image finale
# ───────────────────────────────
@app.route("/user/manual/download/<capture_id>")
def download_manual_filtered_image(capture_id):
    path = os.path.join(SUPPRESSION_HUMAN_FOLDER, f"{capture_id}_filtered.jpg")
    if not os.path.exists(path):
        flash("Image non trouvée.", "danger")
        return redirect(url_for("user_capture"))
    return send_file(path, as_attachment=True)

# ───────────────────────────────
# 📌 Bloc 6 : Serve image annotée par utilisateur
# ───────────────────────────────
@app.route("/user/manual/serve_annotated/<filename>")
def serve_manual_annotated_image(filename):

    base_dir = os.path.dirname(current_app.root_path)
    folder = os.path.join(base_dir, "app", "data", "annoted_by_human")
    file_path = os.path.join(folder, filename)

    print("[DEBUG] Trying to serve file:", file_path)

    if not os.path.exists(file_path):
        print("[404 ERROR] File does not exist:", file_path)
        abort(404)

    return send_file(file_path, mimetype="image/jpeg")



@app.route("/user/display_final_annotation/<capture_id>/<source>")
def model_display_final_annotation(capture_id, source):
    capture_info = find_capture_by_id(capture_id)
    if not capture_info:
        flash("Capture non trouvée.", "danger")
        return redirect(url_for("user_capture"))

    image_filename = capture_info.get("filename")
    capture_id = capture_info.get("capture_id", image_filename.split(".")[0])

    original_path = os.path.join(app.config["ORIGINALS_FOLDER"], image_filename)
    suppression_dir = os.path.join(app.root_path, "data", "suppression")
    os.makedirs(suppression_dir, exist_ok=True)

    output_filename = f"{capture_id}.png"
    output_path = os.path.join(suppression_dir, output_filename)
    json_pred_path = os.path.join(app.config["PREDICTIONS_SCALED_FOLDER"], f"{capture_id}.json")

    kept_box_ids = session.get(f"kept_boxes_{capture_id}", [])

    try:
        import cv2
        import json
        import numpy as np

        print("[DEBUG] Chemin de l'image originale :", original_path)
        if not os.path.exists(original_path):
            raise FileNotFoundError(f"[ERREUR] Image originale introuvable : {original_path}")

        img = cv2.imread(original_path)
        if img is None:
            flash(f"[ERREUR] Impossible de lire l'image : {original_path}", "danger")
            return redirect(url_for("user_capture"))

        print("[DEBUG] Dimensions image :", img.shape)

        if not os.path.exists(json_pred_path):
            raise FileNotFoundError(f"[ERREUR] JSON des prédictions introuvable : {json_pred_path}")

        with open(json_pred_path, "r") as f:
            pred_json = json.load(f)

        h, w = img.shape[:2]
        for ann in pred_json.get("annotations", []):
            box_id = f"box{ann['id']}"
            if box_id not in kept_box_ids:
                x, y, bw, bh = map(int, ann['bbox'])
                class_id = ann['category_id']
                thing_classes = app.config.get("THING_CLASSES", [])
                if 0 <= class_id < len(thing_classes):
                    class_name = thing_classes[class_id]
                else:
                    print(f"[ERREUR] class_id={class_id} hors limites. classes len={len(thing_classes)}")
                    continue

                if class_name == "header":
                    img[0:y + bh, :] = 255
                elif class_name == "footer":
                    img[y:y + bh, :] = 255
                else:
                    img[y:y + bh, x:x + bw] = 255

        img = remove_uniform_bands(img)


        saved = cv2.imwrite(output_path, img)
        print("[DEBUG] Image sauvegardée dans :", output_path)
        print("[DEBUG] Succès sauvegarde ?", saved)

        if not saved:
            raise RuntimeError(f"[ERREUR] La sauvegarde de l'image a échoué : {output_path}")

        flash("Image filtrée enregistrée.", "success")

    except Exception as e:
        flash(f"Erreur de traitement: {str(e)}", "danger")
        print("[EXCEPTION] :", str(e))
        output_filename = image_filename  # fallback si erreur
        output_path = original_path

    return render_template("model_display_final_annotation.html",
                           capture_info=capture_info,
                           annotated_image_path=url_for("serve_suppressed_image", filename=output_filename),
                           download_filename=output_filename,
                           source=source)


@app.route("/data/suppression/<filename>")
def serve_suppressed_image(filename):
    suppression_dir = os.path.join(app.root_path, "data", "suppression")
    return send_from_directory(suppression_dir, filename)

@app.route("/download/final_image/<filename>")
def download_final_image(filename):
    suppression_dir = os.path.join(app.root_path, "data", "suppression")
    file_path = os.path.join(suppression_dir, filename)
    if not os.path.exists(file_path):
        flash("Fichier introuvable.", "danger")
        return redirect(url_for("index"))
    return send_file(file_path, as_attachment=True)


# --- Helper Functions --- #

def find_capture_by_id(capture_id_or_filename):
    links = load_visited_links()
    for link_info in links:
        if link_info.get("capture_id") == capture_id_or_filename:
            return link_info
        if link_info.get("filename") == capture_id_or_filename:
            return link_info
    return None



def load_visited_links():
    try:
        with open(app.config["VISITED_LINKS_FILE"], 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_visited_links(links):
    try:
        with open(app.config["VISITED_LINKS_FILE"], 'w') as f:
            json.dump(links, f, indent=4)
    except IOError as e:
        flash(f"Error saving visited links: {e}", "danger")




def save_annotations_as_coco(image_id, annotations, image_path, output_json_path):

    image = Image.open(image_path)
    width, height = image.size

    coco = {
        "images": [{
            "id": image_id,
            "width": width,
            "height": height,
            "file_name": os.path.basename(image_path)
        }],
        "annotations": [],
        "categories": []
    }

    label_map = {}
    ann_id = 1

    for ann in annotations:
        value = ann.get("value") or ann.get("result", [{}])[0].get("value", {})
        label = value.get("rectanglelabels", ["?"])[0]

        if label not in label_map:
            label_map[label] = len(label_map) + 1
            coco["categories"].append({
                "id": label_map[label],
                "name": label
            })

        x = value["x"] / 100.0 * width
        y = value["y"] / 100.0 * height
        w = value["width"] / 100.0 * width
        h = value["height"] / 100.0 * height

        coco["annotations"].append({
            "id": ann_id,
            "image_id": image_id,
            "category_id": label_map[label],
            "bbox": [x, y, w, h],
            "area": w * h,
            "iscrowd": 0
        })
        ann_id += 1

    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(coco, f, indent=2, ensure_ascii=False)

def draw_boxes_cv2(image_path, annotations, output_path):
    """Dessine les boîtes d'annotation sur l'image avec OpenCV"""
    try:
        print(f"[DEBUG] draw_boxes_cv2 - Input: {image_path}")
        print(f"[DEBUG] draw_boxes_cv2 - Output: {output_path}")
        print(f"[DEBUG] draw_boxes_cv2 - Annotations count: {len(annotations)}")
        
        # ✅ Lire l'image avec CV2 directement
        image_np = cv2.imread(image_path)
        if image_np is None:
            print(f"[ERROR] Impossible de charger l'image: {image_path}")
            return False
            
        height, width = image_np.shape[:2]
        print(f"[DEBUG] Image dimensions: {width}x{height}")

        # ✅ Dessiner chaque annotation
        for i, ann in enumerate(annotations):
            print(f"[DEBUG] Traitement annotation {i+1}: {ann}")
            
            # Récupérer les valeurs de l'annotation
            value = ann.get("value", {})
            if not value:
                print(f"[WARNING] Annotation {i+1} sans valeur")
                continue
                
            label = value.get("rectanglelabels", ["unknown"])[0]
            
            # Convertir les pourcentages en pixels
            x = int((value.get("x", 0) / 100.0) * width)
            y = int((value.get("y", 0) / 100.0) * height)
            w = int((value.get("width", 0) / 100.0) * width)
            h = int((value.get("height", 0) / 100.0) * height)
            
            print(f"[DEBUG] Box {i+1}: label={label}, x={x}, y={y}, w={w}, h={h}")
            
            # ✅ Dessiner le rectangle et le texte
            color = (0, 255, 0)  # Vert
            thickness = 2
            
            # Rectangle
            cv2.rectangle(image_np, (x, y), (x + w, y + h), color, thickness)
            
            # Texte du label
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.6
            text_thickness = 2
            text_size = cv2.getTextSize(label, font, font_scale, text_thickness)[0]
            
            # Background pour le texte
            cv2.rectangle(image_np, (x, y - text_size[1] - 5), (x + text_size[0], y), color, -1)
            cv2.putText(image_np, label, (x, y - 5), font, font_scale, (0, 0, 0), text_thickness)

        # ✅ Sauvegarder l'image annotée
        success = cv2.imwrite(output_path, image_np)
        print(f"[DEBUG] Sauvegarde réussie: {success}")
        
        if success:
            print(f"[SUCCESS] Image annotée sauvegardée: {output_path}")
            return True
        else:
            print(f"[ERROR] Échec sauvegarde image: {output_path}")
            return False
            
    except Exception as e:
        print(f"[EXCEPTION] Erreur dans draw_boxes_cv2: {e}")
        import traceback
        traceback.print_exc()
        return False
# 3. AJOUTER une route de debug pour vérifier que l'image est créée
@app.route("/debug/check_annotated/<capture_id>")
def debug_check_annotated(capture_id):
    """Route de debug pour vérifier les fichiers d'annotation"""
    if not is_admin_logged_in():
        return jsonify({"error": "Non autorisé"}), 401
    
    base_dir = os.path.dirname(current_app.root_path)
    
    # Vérifier les chemins
    paths_to_check = {
        "original": os.path.join(base_dir, "app", "data", "originals", f"{capture_id}.png"),
        "manual_json": os.path.join(base_dir, "app", "data", "human_data", "manual", capture_id, f"{capture_id}.json"),
        "manual_image": os.path.join(base_dir, "app", "data", "human_data", "manual", capture_id, f"{capture_id}.png"),
        "annotated_visual": os.path.join(base_dir, "app", "data", "annoted_by_human", f"annotated_{capture_id}.jpg")
    }
    
    result = {}
    for name, path in paths_to_check.items():
        result[name] = {
            "path": path,
            "exists": os.path.exists(path),
            "size": os.path.getsize(path) if os.path.exists(path) else 0
        }
    
    return jsonify(result)


def remove_zones_from_image(image_path, annotations, output_path):

    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Impossible de charger l'image : {image_path}")

    height, width = image.shape[:2]

    for ann in annotations:
        value = ann.get("value") or ann.get("result", [{}])[0].get("value", {})
        x = int(value["x"] / 100.0 * width)
        y = int(value["y"] / 100.0 * height)
        w = int(value["width"] / 100.0 * width)
        h = int(value["height"] / 100.0 * height)

        image[y:y+h, x:x+w] = 255  # remplissage blanc

    # Facultatif : nettoyage des bandes blanches autour
    image = remove_uniform_bands(image)

    cv2.imwrite(output_path, image)


def remove_uniform_bands(image_np):

    # Supprime les bandes blanches (uniformes) en haut, bas, gauche, droite
    gray = np.mean(image_np, axis=2)
    mask = gray < 250  # tout ce qui est "pas blanc"

    coords = np.argwhere(mask)
    if coords.size == 0:
        return image_np  # rien à garder

    y0, x0 = coords.min(axis=0)
    y1, x1 = coords.max(axis=0) + 1  # slicing

    return image_np[y0:y1, x0:x1]
