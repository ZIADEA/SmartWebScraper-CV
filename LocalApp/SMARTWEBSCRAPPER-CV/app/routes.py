# routes.py - VERSION RÉORGANISÉE ET NETTOYÉE
# SmartWebScraper-CV - Structure modulaire et claire

# ═══════════════════════════════════════════════════════════════════
# IMPORTS
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
import json, subprocess, torch
from detectron2.config import get_cfg
from detectron2 import model_zoo
from detectron2.data import DatasetCatalog, MetadataCatalog
from detectron2.engine import DefaultTrainer
load_dotenv()


ocr_cache = {}

def get_image_hash(image_path):
    """Génère un hash unique pour une image"""
    import hashlib
    
    try:
        # Hash basé sur le chemin et la taille du fichier
        stat = os.stat(image_path)
        content = f"{image_path}_{stat.st_size}_{stat.st_mtime}"
        return hashlib.md5(content.encode()).hexdigest()
    except:
        return None

MIN_HEIGHT = 800
MAX_HEIGHT = 10000


def is_ocr_processed(capture_id, image_path):
    """Vérifie si l'OCR a déjà été fait pour cette image"""
    image_hash = get_image_hash(image_path)
    if not image_hash:
        return False
    
    # Vérifier si l'image est en cache ET si le nlp_system a des données
    return (capture_id in ocr_cache and 
            ocr_cache[capture_id].get('hash') == image_hash and
            hasattr(nlp_system.qa_system, 'sentences') and 
            len(nlp_system.qa_system.sentences) > 0)


def process_ocr_with_cache(capture_id, image_path):
    """Version avec préservation du contenu complet"""
    
    if is_ocr_processed(capture_id, image_path):
        print(f"[CACHE] OCR déjà traité pour {capture_id}")
        cached_data = ocr_cache[capture_id]
        
        # Restaurer TOUT le contenu
        if not hasattr(nlp_system.qa_system, 'sentences') or not nlp_system.qa_system.sentences:
            print("[CACHE] Restauration du contenu COMPLET depuis le cache")
            nlp_system.qa_system.sentences = cached_data['sentences']  # TOUT le contenu
            nlp_system.qa_system.sentences_for_vectorization = cached_data['sentences_for_vectorization']
            nlp_system.qa_system.topics = cached_data['topics']
            nlp_system.qa_system.sentence_vectors = cached_data['sentence_vectors']
        
        return f"OCR utilisé depuis le cache ({len(nlp_system.qa_system.sentences)} phrases complètes)"
    
    print(f"[OCR] Nouveau traitement avec préservation complète pour {capture_id}")
    start_time = time.time()
    
    result = nlp_system.process_image_optimized(image_path, use_layout=True, parallel=True)
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    # Mise en cache du contenu COMPLET
    image_hash = get_image_hash(image_path)
    if image_hash and hasattr(nlp_system.qa_system, 'sentences'):
        ocr_cache[capture_id] = {
            'hash': image_hash,
            'sentences': nlp_system.qa_system.sentences.copy(),  # TOUT le contenu
            'sentences_for_vectorization': nlp_system.qa_system.sentences_for_vectorization.copy(),
            'topics': nlp_system.qa_system.topics.copy(),
            'sentence_vectors': nlp_system.qa_system.sentence_vectors,
            'timestamp': time.time(),
            'processing_time': processing_time
        }
        print(f"[CACHE] Contenu COMPLET mis en cache pour {capture_id}")
    
    return result

def clear_old_cache_entries(max_age_hours=2, max_entries=10):
    """Nettoie les anciennes entrées du cache"""
    current_time = time.time()
    max_age_seconds = max_age_hours * 3600
    
    # Supprimer les entrées trop anciennes
    old_keys = [
        key for key, data in ocr_cache.items() 
        if current_time - data.get('timestamp', 0) > max_age_seconds
    ]
    
    for key in old_keys:
        del ocr_cache[key]
        print(f"[CACHE] Suppression entrée expirée : {key}")
    
    # Limiter le nombre d'entrées (garder les plus récentes)
    if len(ocr_cache) > max_entries:
        sorted_items = sorted(
            ocr_cache.items(), 
            key=lambda x: x[1].get('timestamp', 0), 
            reverse=True
        )
        
        # Garder seulement les max_entries plus récentes
        keys_to_keep = [item[0] for item in sorted_items[:max_entries]]
        keys_to_remove = [key for key in ocr_cache.keys() if key not in keys_to_keep]
        
        for key in keys_to_remove:
            del ocr_cache[key]
            print(f"[CACHE] Suppression entrée excédentaire : {key}")

# ═══════════════════════════════════════════════════════════════════
# FILTRES JINJA2 ET CONTEXT PROCESSORS
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
# CONFIGURATION ET INITIALISATION
# ═══════════════════════════════════════════════════════════════════

# NLP System
nlp_system = CompleteOCRQASystem(
    language='french', 
    ocr_lang='fr',
    max_image_height=2000,
    use_gpu=False,
    cpu_optimized=True
)
# Vérification des configurations requises
required_configs = [
    'ORIGINALS_FOLDER', 'RESIZED_FOLDER', 'ANNOTATED_FOLDER',
     'PREDICTIONS_SCALED_FOLDER',
    'HUMAN_DATA_FOLDER', 'FINE_TUNE_DATA_FOLDER'
]

for config_key in required_configs:
    if config_key not in app.config:
        raise RuntimeError(f"Configuration manquante: {config_key}")

# Créer les dossiers de données
for folder_key in required_configs:
    os.makedirs(app.config[folder_key], exist_ok=True)

# Créer le fichier des liens visités
if not os.path.exists(app.config["VISITED_LINKS_FILE"]):
    with open(app.config["VISITED_LINKS_FILE"], 'w') as f:
        json.dump([], f)

# Dossier pour les images filtrées manuellement
SUPPRESSION_HUMAN_FOLDER = os.path.join(app.root_path, "data", "suppression_human")
os.makedirs(SUPPRESSION_HUMAN_FOLDER, exist_ok=True)

# ═══════════════════════════════════════════════════════════════════
# FONCTIONS UTILITAIRES
# ═══════════════════════════════════════════════════════════════════

def is_admin_logged_in():
    """Vérifie si l'admin est connecté"""
    return session.get("admin_logged_in", False)

def ensure_human_data_structure():
    """Assure que la structure des dossiers human_data est correcte"""
    human_data_path = app.config["HUMAN_DATA_FOLDER"]
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
        
        # Compter les prédictions validées dans human_data/model
        human_data_path = app.config["HUMAN_DATA_FOLDER"]
        model_folder = os.path.join(human_data_path, "model")
        predictions_count = 0
        if os.path.exists(model_folder):
            predictions_count = len([d for d in os.listdir(model_folder) 
                                   if os.path.isdir(os.path.join(model_folder, d))])
        
        # Compter les annotations manuelles dans human_data/manual
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
        
        # DEBUG: Afficher les comptes
        print(f"[DEBUG] Comptages: sites={sites_count}, predictions={predictions_count}, manual={manual_count}, fine_tune={fine_tune_count}")
        
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

def save_validated_prediction_to_human_data(capture_id, kept_box_ids=None):
    """
    Sauvegarde directe de l'image et du JSON de prédiction du modèle
    dans human_data/model/<capture_id>/. Écrase le fichier JSON existant.
    """
    try:
        human_data_path = app.config["HUMAN_DATA_FOLDER"]
        model_folder = os.path.join(human_data_path, "model", capture_id)
        os.makedirs(model_folder, exist_ok=True)

        # Chemins source et destination
        original_image_path = os.path.join(app.config["ORIGINALS_FOLDER"], f"{capture_id}.png")
        prediction_json_path = os.path.join(app.config["PREDICTIONS_SCALED_FOLDER"], f"{capture_id}.json")
        target_image_path = os.path.join(model_folder, f"{capture_id}.png")
        target_json_path = os.path.join(model_folder, f"{capture_id}_coco.json")

        # Copie de l'image
        if not os.path.exists(original_image_path):
            print(f"[WARNING] Image originale non trouvée : {original_image_path}")
            return False
        shutil.copy2(original_image_path, target_image_path)

        # Copie du JSON (prédiction modèle)
        if not os.path.exists(prediction_json_path):
            print(f"[WARNING] JSON de prédiction non trouvé : {prediction_json_path}")
            return False
        shutil.copy2(prediction_json_path, target_json_path)

        print(f"[INFO] Image et prédiction copiées dans : {model_folder}")
        return True

    except Exception as e:
        print(f"[ERROR] save_validated_prediction_to_human_data : {e}")
        return False


def find_capture_by_id(capture_id_or_filename):
    """Trouve une capture par ID ou nom de fichier"""
    links = load_visited_links()
    for link in links:
        if link.get("capture_id") == capture_id_or_filename:
            return link
        if link.get("filename") == capture_id_or_filename:
            return link
    return None

def load_visited_links():
    """Charge la liste des liens visités"""
    try:
        with open(app.config["VISITED_LINKS_FILE"], 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_visited_links(links):
    """Sauvegarde la liste des liens visités"""
    try:
        with open(app.config["VISITED_LINKS_FILE"], 'w') as f:
            json.dump(links, f, indent=4)
    except IOError as e:
        flash(f"Error saving visited links: {e}", "danger")

def save_annotations_as_coco(image_id, annotations, image_path, output_json_path):
    """Convertit les annotations en format COCO"""
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
        image_np = cv2.imread(image_path)
        if image_np is None:
            print(f"[ERROR] Impossible de charger l'image: {image_path}")
            return False
            
        height, width = image_np.shape[:2]

        for i, ann in enumerate(annotations):
            value = ann.get("value", {})
            if not value:
                continue
                
            label = value.get("rectanglelabels", ["unknown"])[0]
            
            x = int((value.get("x", 0) / 100.0) * width)
            y = int((value.get("y", 0) / 100.0) * height)
            w = int((value.get("width", 0) / 100.0) * width)
            h = int((value.get("height", 0) / 100.0) * height)
            
            color = (0, 255, 0)
            thickness = 2
            
            cv2.rectangle(image_np, (x, y), (x + w, y + h), color, thickness)
            
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.6
            text_thickness = 2
            text_size = cv2.getTextSize(label, font, font_scale, text_thickness)[0]
            
            cv2.rectangle(image_np, (x, y - text_size[1] - 5), (x + text_size[0], y), color, -1)
            cv2.putText(image_np, label, (x, y - 5), font, font_scale, (0, 0, 0), text_thickness)

        success = cv2.imwrite(output_path, image_np)
        return success
            
    except Exception as e:
        print(f"[EXCEPTION] Erreur dans draw_boxes_cv2: {e}")
        return False

def remove_zones_from_image(image_path, annotations, output_path):
    """Supprime les zones annotées de l'image"""
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
        image[y:y+h, x:x+w] = 255

    image = remove_uniform_bands(image)
    cv2.imwrite(output_path, image)

def remove_uniform_bands(image_np):
    """Supprime les bandes blanches uniformes autour de l'image"""
    gray = np.mean(image_np, axis=2)
    mask = gray < 250
    coords = np.argwhere(mask)
    if coords.size == 0:
        return image_np
    y0, x0 = coords.min(axis=0)
    y1, x1 = coords.max(axis=0) + 1
    return image_np[y0:y1, x0:x1]

# Initialisation
ensure_human_data_structure()

# ═══════════════════════════════════════════════════════════════════
# ROUTES PRINCIPALES
# ═══════════════════════════════════════════════════════════════════

@app.route("/")
def index():
    """Page d'accueil avec sélection de rôle"""
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Page de connexion administrateur"""
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
            return render_template("login.html")
    
    return render_template("login.html")

@app.route("/logout")
def logout():
    """Déconnexion"""
    session.pop("admin_logged_in", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))

# ═══════════════════════════════════════════════════════════════════
# ROUTES ADMINISTRATION
# ═══════════════════════════════════════════════════════════════════

@app.route("/admin/dashboard")
def admin_dashboard():
    """Dashboard administrateur principal"""
    if not is_admin_logged_in():
        flash("Veuillez vous connecter pour accéder à cette page.", "warning")
        return redirect(url_for("login"))
    
    ensure_human_data_structure()
    stats = count_admin_data()
    
    return render_template("admin_dashboard.html", stats=stats)

@app.route("/admin/visited_links")
def admin_visited_links():
    """Affichage des liens visités"""
    if not is_admin_logged_in():
        flash("Please log in to access this page.", "warning")
        return redirect(url_for("login"))
    
    links = load_visited_links()
    return render_template("admin_visited_links.html", links=links)

# ───────────────────────────────────────────────────────────────────
# GESTION DES PRÉDICTIONS VALIDÉES
# ───────────────────────────────────────────────────────────────────

@app.route("/admin/predictions_validees")
def admin_predictions_validees():
    """Affichage des prédictions validées par feedback utilisateur"""
    if not is_admin_logged_in():
        flash("Veuillez vous connecter pour accéder à cette page.", "warning")
        return redirect(url_for("login"))
    
    human_data_path = app.config["HUMAN_DATA_FOLDER"]
    items_predictions = []
    
    try:
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
        
        items_predictions.sort(key=lambda x: x["timestamp"], reverse=True)
        
    except Exception as e:
        flash(f"Erreur lors du chargement des prédictions validées: {e}", "danger")
    
    return render_template("admin_predictions_validees.html", items=items_predictions)

@app.route("/admin/prediction_detail/<item_id>")
def admin_prediction_detail(item_id):
    """Détail d'une prédiction validée"""
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
    
    # CORRECTION: Charger les vraies informations JSON
    json_info = {}
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
            annotations = json_data.get("annotations", [])
            unique_cats = {ann.get("category_id") for ann in annotations if ann.get("category_id") is not None}
            json_info = {
                "nb_annotations": len(annotations),
                "categories": len(unique_cats),
                "image_info": json_data.get("images", [{}])[0] if json_data.get("images") else {}
            }
            print(f"[DEBUG] JSON chargé pour {item_id}: {json_info}")
    except Exception as e:
        json_info = {"error": f"Erreur lecture JSON: {e}"}
        print(f"[ERROR] Erreur JSON pour {item_id}: {e}")

    # Vérifier si une image annotée par OpenCV existe
    annotated_filename = f"annotated_{image_filename}"
    annotated_path = os.path.join(app.config['ANNOTATED_FOLDER'], annotated_filename)
    if os.path.exists(annotated_path):
        annotated_image_url = url_for('serve_annotated_image', filename=annotated_filename)
    else:
        annotated_image_url = None

    # URL pour servir l'image depuis le bon dossier
    image_url = url_for("serve_human_data_prediction", item_id=item_id, filename=image_filename)


    return render_template(
        "admin_prediction_detail.html",
        item_id=item_id,
        image_url=image_url,
        json_info=json_info,
        annotated_image_url=annotated_image_url,
    )

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
        os.makedirs(fine_tune_data_path, exist_ok=True)
        
        for filename in os.listdir(src_folder):
            src_file = os.path.join(src_folder, filename)
            dst_file = os.path.join(fine_tune_data_path, filename)
            shutil.move(src_file, dst_file)
        
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

# ───────────────────────────────────────────────────────────────────
# GESTION DES ANNOTATIONS MANUELLES
# ───────────────────────────────────────────────────────────────────

@app.route("/admin/annotations_manuelles")
def admin_annotations_manuelles():
    """Affichage des annotations créées manuellement"""
    if not is_admin_logged_in():
        flash("Veuillez vous connecter pour accéder à cette page.", "warning")
        return redirect(url_for("login"))
    
    human_data_path = app.config["HUMAN_DATA_FOLDER"]
    items_manuelles = []
    
    try:
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
        
        items_manuelles.sort(key=lambda x: x["timestamp"], reverse=True)
        
    except Exception as e:
        flash(f"Erreur lors du chargement des annotations manuelles: {e}", "danger")
    
    return render_template("admin_annotations_manuelles.html", items=items_manuelles)
# ═══════════════════════════════════════════════════════════════════
# ROUTES ADMINISTRATION CORRIGÉES
# ═══════════════════════════════════════════════════════════════════

# ───────────────────────────────────────────────────────────────────
# PAGE AA : ANNOTATION MANUELLE PAR L'ADMINISTRATEUR
# ───────────────────────────────────────────────────────────────────

@app.route("/admin/annotation_manuelle/<capture_id>")
def admin_annotation_manuelle(capture_id):
    """Page AA - Interface d'annotation manuelle pour l'administrateur"""
    if not is_admin_logged_in():
        flash("Veuillez vous connecter pour accéder à cette page.", "warning")
        return redirect(url_for("login"))
    
    # Chercher l'image dans les différents dossiers possibles
    image_path = None
    image_url = None
    
    # 1. D'abord dans human_data/model
    human_data_path = app.config["HUMAN_DATA_FOLDER"]
    model_folder = os.path.join(human_data_path, "model", capture_id)
    if os.path.exists(os.path.join(model_folder, f"{capture_id}.png")):
        image_url = url_for("serve_human_data_prediction", item_id=capture_id, filename=f"{capture_id}.png")
        image_path = os.path.join(model_folder, f"{capture_id}.png")
    
    # 2. Sinon dans human_data/manual
    elif os.path.exists(os.path.join(human_data_path, "manual", capture_id, f"{capture_id}.png")):
        image_url = url_for("serve_human_data_manual", item_id=capture_id, filename=f"{capture_id}.png")
        image_path = os.path.join(human_data_path, "manual", capture_id, f"{capture_id}.png")
    
    # 3. Sinon dans originals
    else:
        original_path = os.path.join(app.config["ORIGINALS_FOLDER"], f"{capture_id}.png")
        if os.path.exists(original_path):
            image_url = url_for("serve_original_image", filename=f"{capture_id}.png")
            image_path = original_path
    
    if not image_path:
        flash(f"Image {capture_id} non trouvée.", "danger")
        return redirect(url_for("admin_dashboard"))
    
    return render_template("admin_annotation_manuelle.html",
                         capture_id=capture_id,
                         image_url=image_url)

@app.route("/admin/save_annotation_manuelle", methods=["POST"])
def admin_save_annotation_manuelle():
    """Sauvegarde des annotations de l'administrateur - VA DIRECTEMENT DANS FINE_TUNE_DATA"""
    if not is_admin_logged_in():
        return jsonify({"error": "Non autorisé"}), 401
    
    data = request.get_json()
    capture_id = data.get("capture_id")
    annotations = data.get("annotations")
    
    if not capture_id or not annotations:
        return jsonify({"error": "Données manquantes"}), 400
    
    try:
        fine_tune_data_path = app.config["FINE_TUNE_DATA_FOLDER"]
        os.makedirs(fine_tune_data_path, exist_ok=True)
        
        # Trouver l'image source
        source_image_path = None
        
        # Chercher dans human_data/model
        model_path = os.path.join(app.config["HUMAN_DATA_FOLDER"], "model", capture_id, f"{capture_id}.png")
        if os.path.exists(model_path):
            source_image_path = model_path
        
        # Chercher dans human_data/manual
        manual_path = os.path.join(app.config["HUMAN_DATA_FOLDER"], "manual", capture_id, f"{capture_id}.png")
        if os.path.exists(manual_path):
            source_image_path = manual_path
        
        # Chercher dans originals
        original_path = os.path.join(app.config["ORIGINALS_FOLDER"], f"{capture_id}.png")
        if os.path.exists(original_path):
            source_image_path = original_path
        
        if not source_image_path:
            return jsonify({"error": "Image source non trouvée"}), 404
        
        # Copier l'image dans fine_tune_data
        target_image_path = os.path.join(fine_tune_data_path, f"{capture_id}.png")
        shutil.copy2(source_image_path, target_image_path)
        
        # Sauvegarder au format COCO directement dans fine_tune_data
        coco_path = os.path.join(fine_tune_data_path, f"{capture_id}_coco.json")
        save_annotations_as_coco(capture_id, annotations, target_image_path, coco_path)
        
        # IMPORTANT: Supprimer l'image des dossiers human_data après sauvegarde
        # Supprimer de human_data/model si elle y était
        model_folder = os.path.join(app.config["HUMAN_DATA_FOLDER"], "model", capture_id)
        if os.path.exists(model_folder):
            shutil.rmtree(model_folder)
        
        # Supprimer de human_data/manual si elle y était
        manual_folder = os.path.join(app.config["HUMAN_DATA_FOLDER"], "manual", capture_id)
        if os.path.exists(manual_folder):
            shutil.rmtree(manual_folder)
        
        return jsonify({
            "status": "success", 
            "message": "Annotation sauvegardée dans fine_tune_data",
            "redirect": url_for("admin_fine_tune_management")
        })
        
    except Exception as e:
        return jsonify({"error": f"Erreur de sauvegarde: {e}"}), 500

# ───────────────────────────────────────────────────────────────────
# CORRECTION DES ACTIONS DE VALIDATION/SUPPRESSION/MODIFICATION
# ───────────────────────────────────────────────────────────────────

@app.route("/admin/action_prediction/<item_id>/<action>", methods=["POST"])
def admin_action_prediction(item_id, action):
    """Actions sur les prédictions: valider, supprimer, modifier"""
    if not is_admin_logged_in():
        flash("Veuillez vous connecter pour effectuer cette action.", "warning")
        return redirect(url_for("login"))
    
    human_data_path = app.config["HUMAN_DATA_FOLDER"]
    src_folder = os.path.join(human_data_path, "model", item_id)
    
    if not os.path.exists(src_folder):
        flash(f"Prédiction {item_id} non trouvée.", "danger")
        return redirect(url_for("admin_predictions_validees"))
    
    try:
        if action == "validate":
            # ✅ VALIDER: Déplacer vers fine_tune_data et tout supprimer
            fine_tune_data_path = app.config["FINE_TUNE_DATA_FOLDER"]
            os.makedirs(fine_tune_data_path, exist_ok=True)
            
            # Déplacer tous les fichiers vers fine_tune_data
            for filename in os.listdir(src_folder):
                src_file = os.path.join(src_folder, filename)
                dst_file = os.path.join(fine_tune_data_path, filename)
                shutil.move(src_file, dst_file)
            
            # Supprimer le dossier vide
            os.rmdir(src_folder)
            
            # Supprimer l'image annotée OpenCV correspondante
            annotated_folder = app.config.get("ANNOTATED_FOLDER")
            if annotated_folder:
                annotated_file = os.path.join(annotated_folder, f"annotated_{item_id}.png")
                if os.path.exists(annotated_file):
                    os.remove(annotated_file)
            
            flash(f"✅ Prédiction {item_id} validée et déplacée vers fine_tune_data.", "success")
            
        elif action == "delete":
            # 🗑️ SUPPRIMER: Supprimer complètement
            shutil.rmtree(src_folder)
            
            # Supprimer aussi tous les fichiers associés dans tous les dossiers
            folders_to_clean = [
                app.config["ORIGINALS_FOLDER"],
                app.config["ANNOTATED_FOLDER"],
                # app.config["PREDICTIONS_RAW_FOLDER"],
                app.config["PREDICTIONS_SCALED_FOLDER"],
                os.path.join(app.root_path, "data", "suppression"),
                os.path.join(app.root_path, "data", "annoted_by_human")
            ]
            
            for folder in folders_to_clean:
                if folder and os.path.exists(folder):
                    # Chercher tous les fichiers qui contiennent l'item_id
                    for filename in os.listdir(folder):
                        if item_id in filename:
                            file_path = os.path.join(folder, filename)
                            try:
                                os.remove(file_path)
                            except:
                                pass
            
            flash(f"🗑️ Prédiction {item_id} et tous ses fichiers supprimés.", "success")
            
        elif action == "modify":
            # ✏️ MODIFIER: Rediriger vers la page d'annotation admin
            return redirect(url_for("admin_annotation_manuelle", capture_id=item_id))
            
    except Exception as e:
        flash(f"Erreur lors de l'action {action}: {e}", "danger")
    
    return redirect(url_for("admin_predictions_validees"))

@app.route("/admin/action_annotation_manuelle/<item_id>/<action>", methods=["POST"])
def admin_action_annotation_manuelle(item_id, action):
    """Actions sur les annotations manuelles: valider, supprimer, modifier"""
    if not is_admin_logged_in():
        flash("Veuillez vous connecter pour effectuer cette action.", "warning")
        return redirect(url_for("login"))
    
    human_data_path = app.config["HUMAN_DATA_FOLDER"]
    src_folder = os.path.join(human_data_path, "manual", item_id)
    
    if not os.path.exists(src_folder):
        flash(f"Annotation manuelle {item_id} non trouvée.", "danger")
        return redirect(url_for("admin_annotations_manuelles"))
    
    try:
        if action == "validate":
            # ✅ VALIDER: Déplacer vers fine_tune_data et tout supprimer
            fine_tune_data_path = app.config["FINE_TUNE_DATA_FOLDER"]
            os.makedirs(fine_tune_data_path, exist_ok=True)
            
            # Déplacer tous les fichiers vers fine_tune_data
            for filename in os.listdir(src_folder):
                src_file = os.path.join(src_folder, filename)
                dst_file = os.path.join(fine_tune_data_path, filename)
                shutil.move(src_file, dst_file)
            
            # Supprimer le dossier vide
            os.rmdir(src_folder)
            
            # Supprimer l'image annotée OpenCV correspondante
            base_dir = os.path.dirname(current_app.root_path)
            annotated_by_human_dir = os.path.join(base_dir, "app", "data", "annoted_by_human")
            annotated_file = os.path.join(annotated_by_human_dir, f"annotated_{item_id}.jpg")
            if os.path.exists(annotated_file):
                os.remove(annotated_file)
            
            flash(f"✅ Annotation manuelle {item_id} validée et déplacée vers fine_tune_data.", "success")
            
        elif action == "delete":
            # 🗑️ SUPPRIMER: Supprimer complètement
            shutil.rmtree(src_folder)
            
            # Supprimer aussi l'image annotée OpenCV
            base_dir = os.path.dirname(current_app.root_path)
            annotated_by_human_dir = os.path.join(base_dir, "app", "data", "annoted_by_human")
            annotated_file = os.path.join(annotated_by_human_dir, f"annotated_{item_id}.jpg")
            if os.path.exists(annotated_file):
                os.remove(annotated_file)
            
            # Supprimer dans le dossier suppression_human aussi
            suppression_file = os.path.join(SUPPRESSION_HUMAN_FOLDER, f"{item_id}_filtered.jpg")
            if os.path.exists(suppression_file):
                os.remove(suppression_file)
            
            flash(f"🗑️ Annotation manuelle {item_id} et tous ses fichiers supprimés.", "success")
            
        elif action == "modify":
            # ✏️ MODIFIER: Rediriger vers la page d'annotation admin
            return redirect(url_for("admin_annotation_manuelle", capture_id=item_id))
            
    except Exception as e:
        flash(f"Erreur lors de l'action {action}: {e}", "danger")
    
    return redirect(url_for("admin_annotations_manuelles"))

# ───────────────────────────────────────────────────────────────────
# CORRECTION DU FINE-TUNING AVEC SUPPRESSION AUTOMATIQUE
# ───────────────────────────────────────────────────────────────────

@app.route("/admin/launch_fine_tuning_final", methods=["POST"])
def admin_launch_fine_tuning_final():
    """Lancer le fine-tuning avec suppression automatique des données après"""
    if not is_admin_logged_in():
        flash("Veuillez vous connecter pour effectuer cette action.", "warning")
        return redirect(url_for("login"))
    
    fine_tune_data_path = app.config["FINE_TUNE_DATA_FOLDER"]
    
    try:
        if not os.path.exists(fine_tune_data_path):
            flash("Aucun dossier fine_tune_data trouvé.", "danger")
            return redirect(url_for("admin_fine_tune_management"))
        
        files = os.listdir(fine_tune_data_path)
        if not files:
            flash("Aucun fichier dans fine_tune_data.", "warning")
            return redirect(url_for("admin_fine_tune_management"))
        
        # 1. Créer un dossier de backup avec timestamp
        backup_folder = os.path.join(app.root_path, "data", "fine_tune_backup")
        os.makedirs(backup_folder, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_folder, f"backup_{timestamp}")
        os.makedirs(backup_path, exist_ok=True)
        
        # 2. Copier les fichiers vers le backup (pas déplacer, copier)
        files_count = 0
        for filename in files:
            src = os.path.join(fine_tune_data_path, filename)
            dst = os.path.join(backup_path, filename)
            shutil.copy2(src, dst)
            files_count += 1
        
        # 3. TODO: Ici, ajouter le code de fine-tuning réel
        # Par exemple: appel à un script Python externe, ou intégration Detectron2
        print(f"[FINE-TUNING] Démarrage avec {files_count} fichiers...")
        
        # Simuler le processus (remplacer par le vrai code)
        time.sleep(2)  # Simulation
        
        # 4. APRÈS LE FINE-TUNING: Supprimer automatiquement fine_tune_data/
        for filename in files:
            file_path = os.path.join(fine_tune_data_path, filename)
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Erreur suppression {filename}: {e}")
        
        flash(f"🚀 Fine-tuning terminé ! {files_count} fichiers traités. Backup sauvé: backup_{timestamp}. Dossier fine_tune_data vidé automatiquement.", "success")
        
    except Exception as e:
        flash(f"Erreur lors du fine-tuning: {e}", "danger")
    
    return redirect(url_for("admin_fine_tune_management"))

# ───────────────────────────────────────────────────────────────────
# ROUTE POUR AFFICHER LES BACKUPS DE FINE-TUNING
# ───────────────────────────────────────────────────────────────────

@app.route("/admin/fine_tune_backups")
def admin_fine_tune_backups():
    """Affichage des backups de fine-tuning"""
    if not is_admin_logged_in():
        flash("Veuillez vous connecter pour accéder à cette page.", "warning")
        return redirect(url_for("login"))
    
    backup_folder = os.path.join(app.root_path, "data", "fine_tune_backup")
    backups = []
    
    if os.path.exists(backup_folder):
        for backup_name in os.listdir(backup_folder):
            backup_path = os.path.join(backup_folder, backup_name)
            if os.path.isdir(backup_path):
                files_count = len(os.listdir(backup_path))
                backups.append({
                    "name": backup_name,
                    "path": backup_path,
                    "files_count": files_count,
                    "timestamp": os.path.getctime(backup_path)
                })
    
    backups.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return render_template("admin_fine_tune_backups.html", backups=backups)

@app.route("/admin/annotation_manuelle_detail/<item_id>")
def admin_annotation_manuelle_detail(item_id):
    """Détail d'une annotation manuelle"""
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
    
    json_info = {}
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
            annotations = json_data.get("annotations", [])
            unique_cats = {ann.get("category_id") for ann in annotations if ann.get("category_id") is not None}
            json_info = {
                "nb_annotations": len(annotations),
                "categories": len(unique_cats),
                "image_info": json_data.get("images", [{}])[0]
            }
    except Exception as e:
        json_info = {"error": f"Erreur lecture JSON: {e}"}
    
    image_url = url_for("serve_human_data_manual", item_id=item_id, filename=image_filename)

    annotated_filename = f"annotated_{item_id}.jpg"
    base_dir = os.path.dirname(current_app.root_path)
    annotated_dir = os.path.join(base_dir, "app", "data", "annoted_by_human")
    os.makedirs(annotated_dir, exist_ok=True)
    annotated_path = os.path.join(annotated_dir, annotated_filename)

    if not os.path.exists(annotated_path):
        manual_json_path = os.path.join(manual_folder, f"{item_id}.json")
        if os.path.exists(manual_json_path):
            try:
                with open(manual_json_path, "r", encoding="utf-8") as f:
                    anns = json.load(f)
                draw_boxes_cv2(image_path, anns, annotated_path)
            except Exception as e:
                print(f"[ERROR] Unable to recreate annotated image: {e}")

    annotated_image_url = None
    if os.path.exists(annotated_path):
        annotated_image_url = url_for("serve_manual_annotated_image", filename=annotated_filename)

    return render_template("admin_annotation_manuelle_detail.html",
                         item_id=item_id,
                         image_url=image_url,
                         json_info=json_info,
                         annotated_image_url=annotated_image_url)

@app.route("/admin/validate_annotation_manuelle/<item_id>", methods=["POST"])
def admin_validate_annotation_manuelle(item_id):
    """Valider annotation manuelle et déplacer vers fine_tune_data"""
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
        os.makedirs(fine_tune_data_path, exist_ok=True)
        
        for filename in os.listdir(src_folder):
            src_file = os.path.join(src_folder, filename)
            dst_file = os.path.join(fine_tune_data_path, filename)
            shutil.move(src_file, dst_file)
        
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

# ───────────────────────────────────────────────────────────────────
# GESTION DU FINE-TUNING
# ───────────────────────────────────────────────────────────────────

# --- IMPORTS ADDITIONNELS ---

# ----------------------------


# ──────────────────────────────────────────────────────────────
# 1) PAGE DE GESTION : inchangée
# ──────────────────────────────────────────────────────────────
@app.route("/admin/fine_tune_management")
def admin_fine_tune_management():
    """Gestion du fine-tuning"""
    if not is_admin_logged_in():
        flash("Veuillez vous connecter pour accéder à cette page.", "warning")
        return redirect(url_for("login"))

    fine_tune_data_path = app.config["FINE_TUNE_DATA_FOLDER"]

    image_count = 0
    json_count  = 0
    files_info  = []

    try:
        if os.path.exists(fine_tune_data_path):
            for filename in os.listdir(fine_tune_data_path):
                file_path = os.path.join(fine_tune_data_path, filename)
                if not os.path.isfile(file_path):
                    continue
                if filename.lower().endswith((".png", ".jpg", ".jpeg")):
                    image_count += 1
                    file_type = "image"
                elif filename.lower().endswith(".json"):
                    json_count += 1
                    file_type = "json"
                else:
                    continue

                files_info.append(
                    dict(
                        name=filename,
                        type=file_type,
                        size=os.path.getsize(file_path),
                        timestamp=os.path.getctime(file_path),
                    )
                )

        files_info.sort(key=lambda x: x["timestamp"], reverse=True)

    except Exception as e:
        flash(f"Erreur lors du scan du dossier fine_tune_data : {e}", "danger")

    return render_template(
        "admin_fine_tune_management.html",
        image_count=image_count,
        json_count=json_count,
        files_info=files_info,
    )


# ──────────────────────────────────────────────────────────────
# 2) LANCEMENT RÉEL DU FINE-TUNING
# ──────────────────────────────────────────────────────────────
@app.route("/admin/launch_fine_tuning", methods=["POST"])
def admin_launch_fine_tuning():
    """Sauvegarder les données puis lancer le fine-tuning Detectron2"""
    if not is_admin_logged_in():
        flash("Veuillez vous connecter pour effectuer cette action.", "warning")
        return redirect(url_for("login"))

    data_dir = app.config["FINE_TUNE_DATA_FOLDER"]
    if not os.path.exists(data_dir):
        flash("Aucun dossier fine_tune_data trouvé.", "danger")
        return redirect(url_for("admin_fine_tune_management"))

    files = os.listdir(data_dir)
    if not files:
        flash("Aucun fichier dans fine_tune_data.", "warning")
        return redirect(url_for("admin_fine_tune_management"))

    # 2-A. Backup
    timestamp   = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(app.root_path, "data", "fine_tune_backup", f"backup_{timestamp}")
    os.makedirs(backup_path, exist_ok=True)
    for f in files:
        shutil.move(os.path.join(data_dir, f), os.path.join(backup_path, f))

    flash(f"{len(files)} fichiers déplacés dans backup_{timestamp}.", "success")

    # 2-B. Préparation du dataset COCO
    json_ann   = os.path.join(backup_path, "annotations.json")  # ← s'assure qu'il existe
    images_dir = os.path.join(backup_path, "images")
    if not os.path.isfile(json_ann):
        flash("Le fichier annotations.json est introuvable dans le backup.", "danger")
        return redirect(url_for("admin_fine_tune_management"))

    def get_dicts():
        with open(json_ann, encoding="utf-8") as f:
            return json.load(f)

    ds_name = f"fine_tune_{timestamp}"
    if ds_name in DatasetCatalog.list():
        DatasetCatalog.remove(ds_name)
        MetadataCatalog.remove(ds_name)
    DatasetCatalog.register(ds_name, get_dicts)

    classes = [
        "advertisement", "chaine", "commentaire", "description",
        "header", "footer", "left sidebar", "logo", "likes", "media",
        "pop up", "recommendations", "right sidebar", "suggestions",
        "title", "vues", "none access", "other",
    ]
    MetadataCatalog.get(ds_name).set(thing_classes=classes, json_file=json_ann, image_root=images_dir)

    # 2-C. Configuration Detectron2
    cfg = get_cfg()
    cfg.merge_from_file(model_zoo.get_config_file("COCO-Detection/faster_rcnn_R_101_FPN_3x.yaml"))
    cfg.DATASETS.TRAIN = (ds_name,)
    cfg.DATASETS.TEST  = ()
    cfg.DATALOADER.NUM_WORKERS = 2
    cfg.MODEL.WEIGHTS  = os.path.join(app.root_path, "app", "models", "best_model.pth")  # point de départ
    cfg.SOLVER.IMS_PER_BATCH = 2
    cfg.SOLVER.BASE_LR       = 1e-4
    cfg.SOLVER.MAX_ITER      = 1000              # à ajuster
    cfg.SOLVER.STEPS         = []
    cfg.MODEL.ROI_HEADS.BATCH_SIZE_PER_IMAGE = 128
    cfg.MODEL.ROI_HEADS.NUM_CLASSES         = len(classes)
    cfg.MODEL.DEVICE = "cpu"                 # passe à "cuda" si dispo

    # 2-D. Dossier de sortie
    cfg.OUTPUT_DIR = os.path.join(app.root_path, "app", "models", f"fine_tune_{timestamp}")
    os.makedirs(cfg.OUTPUT_DIR, exist_ok=True)

    # 2-E. Entraînement
    try:
        trainer = DefaultTrainer(cfg)
        trainer.resume_or_load(resume=False)
        trainer.train()
        flash("Fine-tuning Detectron2 terminé avec succès.", "success")

        # 2-F. Remplacer automatiquement le modèle courant
        new_model = os.path.join(cfg.OUTPUT_DIR, "model_final.pth")
        dest_best = os.path.join(app.root_path, "app", "models", "best_model.pth")
        shutil.copyfile(new_model, dest_best)
        flash("`best_model.pth` mis à jour avec le modèle fine-tuné.", "info")

    except Exception as e:
        flash(f"Erreur pendant le fine-tuning : {e}", "danger")

    return redirect(url_for("admin_fine_tune_management"))


# ──────────────────────────────────────────────────────────────
# 3) ROUTE ALIAS : inchangée
# ──────────────────────────────────────────────────────────────
@app.route("/admin/launch_fine_tuning_validated", methods=["POST"])
def admin_launch_fine_tuning_validated():
    """Alias -> lance la même fonction"""
    return admin_launch_fine_tuning()

# ═══════════════════════════════════════════════════════════════════
# ROUTES UTILISATEUR
# ═══════════════════════════════════════════════════════════════════

@app.route("/user/capture", methods=["GET", "POST"])
def user_capture():
    """Capture d'une nouvelle page web"""
    if request.method == "POST":
        url = request.form.get("url")
        if not url or not validators.url(url):
            flash("Veuillez entrer une URL valide.", "warning")
            return redirect(url_for("user_capture"))

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    viewport={"width": 1280, "height": 1024},
                    java_script_enabled=True
                )
                page = context.new_page()
                
                page.goto(url, wait_until="load", timeout=30000)
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(2000)

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{timestamp}_{uuid.uuid4().hex}.png"
                capture_id = filename.split(".")[0]
                filepath = os.path.join(app.config["ORIGINALS_FOLDER"], filename)

                # Obtenir la hauteur réelle de la page
                scroll_height = page.evaluate("() => document.body.scrollHeight")

                # Appliquer la contrainte de hauteur
                clamped_height = max(MIN_HEIGHT, min(scroll_height, MAX_HEIGHT))

                # Ajuster la taille de la capture
                screenshot_bytes = page.screenshot(full_page=True)
                from PIL import Image
                import io

                img = Image.open(io.BytesIO(screenshot_bytes))
                width, height = img.size

                # Rogner si nécessaire
                if height > clamped_height:
                    img = img.crop((0, 0, width, clamped_height))

                # Sauvegarder l'image rognée
                img.save(filepath)

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

@app.route("/user/display/<filename>")
def user_display_capture(filename):
    """Affichage d'une capture"""
    capture_info = find_capture_by_id(filename)
    if not capture_info:
        flash("Capture non trouvée.", "danger")
        return redirect(url_for("user_capture"))

    if "capture_id" not in capture_info:
        capture_info["capture_id"] = capture_info["filename"].split(".")[0]

    image_filename = f"{capture_info['capture_id']}.png"
    image_path = url_for("serve_original_image", filename=image_filename)

    return render_template("user_display_capture.html",
                           capture_info=capture_info,
                           image_path=image_path)

@app.route("/user/save_options/<capture_id>")
def user_save_options(capture_id):
    """Options de sauvegarde pour une capture"""
    capture_info = find_capture_by_id(capture_id)
    if not capture_info:
        flash("Capture non trouvée.", "danger")
        return redirect(url_for("user_capture"))

    if "capture_id" not in capture_info:
        capture_info["capture_id"] = capture_info["filename"].split(".")[0]

    image_filename = capture_info["filename"]
    image_path = url_for("serve_original_image", filename=image_filename)

    return render_template("user_save_options.html", 
                         capture_info=capture_info, 
                         image_path=image_path)

@app.route("/user/download_original/<capture_id>")
def user_download_original(capture_id):
    """Téléchargement de l'image originale"""
    capture_info = find_capture_by_id(capture_id)
    if not capture_info:
        flash("Capture non trouvée.", "danger")
        return redirect(url_for("user_capture"))

    image_filename = capture_info.get("filename")
    image_path = url_for("serve_original_image", filename=image_filename)

    return render_template("user_download_original.html", 
                         capture_info=capture_info, 
                         image_path=image_path)

# ───────────────────────────────────────────────────────────────────
# ANNOTATION AUTOMATIQUE (MODÈLE)
# ───────────────────────────────────────────────────────────────────

@app.route("/user/annotate_model/<capture_id>")
def user_annotate_model(capture_id):
    """Annotation automatique par le modèle IA"""
    capture_info = find_capture_by_id(capture_id)
    if not capture_info:
        flash("Capture non trouvée.", "danger")
        return redirect(url_for("user_capture"))

    try:
        from detectron2.config import get_cfg
        from detectron2.engine import DefaultPredictor
        from detectron2 import model_zoo
        from detectron2.data import MetadataCatalog

        original_image_path = os.path.join(app.config["ORIGINALS_FOLDER"], capture_info["filename"])
        annotated_image_filename = f"annotated_{capture_info['filename']}"
        annotated_image_path_local = os.path.join(app.config["ANNOTATED_FOLDER"], annotated_image_filename)
        coco_json_path = os.path.join(app.config["PREDICTIONS_SCALED_FOLDER"], f"{capture_id}.json")

        # Configuration Detectron2
        cfg = get_cfg()
        cfg.merge_from_file(model_zoo.get_config_file("COCO-Detection/faster_rcnn_R_101_FPN_3x.yaml"))
        cfg.OUTPUT_DIR = os.path.join("app", "models")
        cfg.MODEL.WEIGHTS = os.path.join(cfg.OUTPUT_DIR, "best_model.pth")
        cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.3
        cfg.MODEL.ROI_HEADS.NUM_CLASSES = 18
        cfg.MODEL.DEVICE = "cpu"
        
        thing_classes = [
            "advertisement", "chaine", "commentaire", "description", "header", "footer", "left sidebar",
            "logo", "likes", "media", "pop up", "recommendations", "right sidebar", "suggestions",
            "title", "vues", "none access", "other"
        ]
        MetadataCatalog.get("web_custom").thing_classes = thing_classes
        cfg.DATASETS.TEST = ("web_custom",)
        predictor = DefaultPredictor(cfg)

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

        # Traitement de l'image
        img = cv2.imread(original_image_path)
        slices = slice_image_array(img)
        annotated = img.copy()
        detected_boxes = []
        annotations = []
        kept = {}
        annotation_id = 1

        CLASS_COLORS = {
            "advertisement": (255, 0, 0), "chaine": (0, 255, 0), "commentaire": (0, 0, 255),
            "description": (255, 255, 0), "header": (255, 0, 255), "footer": (0, 255, 255),
            "left sidebar": (128, 0, 0), "logo": (0, 128, 0), "likes": (0, 0, 128),
            "media": (128, 128, 0), "pop up": (128, 0, 128), "recommendations": (0, 128, 128),
            "right sidebar": (64, 0, 0), "suggestions": (0, 64, 0), "title": (0, 0, 64),
            "vues": (64, 64, 0), "none access": (64, 0, 64), "other": (0, 64, 64)
        }

        unique_class_limit = {
            "footer", "header", "chaine", "commentaire", "description",
            "left sidebar", "likes", "recommendations", "vues", "title", "right sidebar"
        }
        to_ignore_classes = {"other", "none access", "suggestions","vues","likes"}

        for crop, y_offset in slices:
            outputs = predictor(crop)["instances"].to("cpu")
            boxes = outputs.pred_boxes.tensor.numpy()
            labels = outputs.pred_classes.numpy()
            scores = outputs.scores.numpy()

            for i in range(len(boxes)):
                class_id = int(labels[i])
                class_name = thing_classes[class_id]
                score = float(scores[i])

                if class_name in to_ignore_classes:
                    continue

                x1, y1, x2, y2 = map(int, boxes[i])
                y1 += y_offset
                y2 += y_offset

                # Correction métier: reclasser "pop up" en "media"
                if class_name == "pop up":
                    class_name = "media"
                    class_id = thing_classes.index("media")

                # === Étape 1 : stocker les boîtes footer et header (dans une variable temporaire)
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

        cv2.imwrite(annotated_image_path_local, annotated)
        annotated_image_path = url_for("serve_annotated_image", filename=annotated_image_filename)

        with open(coco_json_path, "w") as f:
            json.dump({"annotations": annotations}, f, indent=2)


        return render_template("user_annotate_model.html", 
                             capture_info=capture_info, 
                             annotated_image_path=annotated_image_path, 
                             detected_boxes=detected_boxes)

    except Exception as e:
        flash(f"Erreur lors de l'annotation automatique: {str(e)}", "danger")
        return redirect(url_for("user_capture"))

@app.route("/user/process_annotation/<capture_id>", methods=["POST"])
def user_process_annotation(capture_id):
    """Traitement des choix d'annotation"""
    capture_info = find_capture_by_id(capture_id)
    if not capture_info:
        flash("Capture non trouvée.", "danger")
        return redirect(url_for("user_capture"))

    kept_box_ids = request.form.getlist("keep_box")
    session[f"kept_boxes_{capture_id}"] = kept_box_ids
    flash(f"Choix des boîtes enregistrés ({len(kept_box_ids)} à supprimer). Veuillez donner votre feedback.", "info")

    return redirect(url_for("user_feedback", capture_id=capture_id))

@app.route("/user/feedback/<capture_id>", methods=["GET", "POST"])
def user_feedback(capture_id):
    """Page de feedback utilisateur"""
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

# ───────────────────────────────────────────────────────────────────
# ANNOTATION MANUELLE
# ───────────────────────────────────────────────────────────────────

@app.route("/user/manual/annotate/<capture_id>")
def manual_annotation(capture_id):
    """Interface d'annotation manuelle"""
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

@app.route("/user/manual/save", methods=["POST"])
def manual_annotation_save():
    """Sauvegarde des annotations manuelles"""
    data = request.get_json()
    image_id = data.get("image_id")
    annotations = data.get("annotations")
    
    base_dir = os.path.dirname(current_app.root_path)
    src_image = os.path.join(base_dir, "app", "data", "originals", f"{image_id}.png")
    save_dir = os.path.join(base_dir, "app", "data", "human_data", "manual", image_id)
    os.makedirs(save_dir, exist_ok=True)

    annotated_by_human_dir = os.path.join(base_dir, "app", "data", "annoted_by_human")
    os.makedirs(annotated_by_human_dir, exist_ok=True)

    dst_image = os.path.join(save_dir, f"{image_id}.png")
    shutil.copy(src_image, dst_image)

    json_path = os.path.join(save_dir, f"{image_id}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(annotations, f, indent=2, ensure_ascii=False)

    coco_path = os.path.join(save_dir, f"{image_id}_coco.json")
    save_annotations_as_coco(image_id, annotations, dst_image, coco_path)

    image_out = os.path.join(annotated_by_human_dir, f"annotated_{image_id}.jpg")
    success = draw_boxes_cv2(src_image, annotations, image_out)
    
    if success:
        print(f"[SUCCESS] Image annotée créée: {image_out}")
    else:
        print(f"[ERROR] Échec création image annotée: {image_out}")

    redirect_url = url_for("manual_boxes_review", capture_id=image_id)
    return jsonify({"status": "success", "redirect": redirect_url})

@app.route("/user/manual/review/<capture_id>", methods=["GET", "POST"])
def manual_boxes_review(capture_id):
    """Révision des boîtes d'annotation manuelle"""
    base_dir = os.path.dirname(current_app.root_path)
    ann_dir = os.path.join(base_dir, "app", "data", "human_data", "manual", capture_id)
    json_path = os.path.join(ann_dir, f"{capture_id}.json")
    img_path = os.path.join(ann_dir, f"{capture_id}.png")
    
    annotated_visual_path = os.path.join(base_dir, "app", "data", "annoted_by_human", f"annotated_{capture_id}.jpg")

    if not os.path.exists(json_path) or not os.path.exists(img_path):
        flash("Fichiers manquants pour l'annotation manuelle.", "danger")
        return redirect(url_for("user_capture"))

    if not os.path.exists(annotated_visual_path):
        try:
            with open(json_path, "r") as f:
                annotations = json.load(f)
            
            success = draw_boxes_cv2(img_path, annotations, annotated_visual_path)
            if success:
                print(f"[SUCCESS] Image annotée recréée: {annotated_visual_path}")
        except Exception as e:
            print(f"[ERROR] Erreur recréation image: {e}")

    if request.method == "POST":
        kept_ids = request.form.getlist("keep_manual_box")
        with open(json_path, "r") as f:
            annotations = json.load(f)

        filtered = [ann for ann in annotations if str(ann.get("id")) in kept_ids]
        with open(json_path, "w") as f:
            json.dump(filtered, f, indent=2)

        output_path = os.path.join(SUPPRESSION_HUMAN_FOLDER, f"{capture_id}_filtered.jpg")
        remove_zones_from_image(img_path, filtered, output_path)

        return redirect(url_for("manual_display_final_annotation", capture_id=capture_id))

    with open(json_path, "r") as f:
        annotations = json.load(f)

    return render_template("user_manual_remove_boxes.html",
                           capture_info=find_capture_by_id(capture_id),
                           annotated_image_path=url_for("serve_manual_annotated_image", filename=f"annotated_{capture_id}.jpg"),
                           manual_boxes=[{
                               "id": str(ann.get("id")),
                               "class": ann.get("value", {}).get("rectanglelabels", ["?"])[0]
                           } for ann in annotations])

@app.route("/user/manual/final_display/<capture_id>")
def manual_display_final_annotation(capture_id):
    """Affichage final de l'annotation manuelle"""
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
            raise FileNotFoundError(f"Annotations JSON manquantes : {json_path}")

        if not os.path.exists(img_path):
            raise FileNotFoundError(f"Image source manquante : {img_path}")

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
            image[y:y + bh, x:x + bw] = 255

        image = remove_uniform_bands(image)
        saved = cv2.imwrite(output_path, image)

        if not saved:
            raise IOError(f"Échec de sauvegarde de l'image nettoyée : {output_path}")

    except Exception as e:
        flash(f"Erreur lors de la suppression : {str(e)}", "danger")
        output_path = img_path
        output_filename = f"{capture_id}.png"

    return render_template("user_display_final_annotation.html",
                           capture_info=capture_info,
                           annotated_image_path=url_for("serve_filtered_manual_image", filename=output_filename),
                           download_filename=output_filename,
                           source="manual_edited")

@app.route("/user/manual/download/<capture_id>")
def download_manual_filtered_image(capture_id):
    """Téléchargement de l'image filtrée manuelle"""
    path = os.path.join(SUPPRESSION_HUMAN_FOLDER, f"{capture_id}_filtered.jpg")
    if not os.path.exists(path):
        flash("Image non trouvée.", "danger")
        return redirect(url_for("user_capture"))
    return send_file(path, as_attachment=True)

# ───────────────────────────────────────────────────────────────────
# SYSTÈME DE QUESTIONS NLP
# ───────────────────────────────────────────────────────────────────

@app.route("/user/question_choice/<capture_id>")
def user_question_choice(capture_id):
    """Choix du système de questions"""
    return render_template("user_question_choice.html", capture_id=capture_id)

@app.route("/user/question_nlp/<capture_id>", methods=["GET", "POST"])
def user_question_nlp(capture_id):
    """Questions avec système NLP interne - OPTIMISÉ AVEC CACHE"""
    capture_info = find_capture_by_id(capture_id)
    if not capture_info:
        flash("Capture non trouvée.", "danger")
        return redirect(url_for("user_capture"))
        
    image_filename = f"{capture_info['capture_id']}.png"
    absolute_image_path = os.path.join(app.config["ORIGINALS_FOLDER"], image_filename)

    # ✅ OPTIMISATION : OCR avec cache intelligent
    try:
        # Nettoyer le cache périodiquement
        clear_old_cache_entries()
        
        # Traitement OCR avec cache
        result = process_ocr_with_cache(capture_id, absolute_image_path)
        print(f"[NLP] {result}")
        
    except Exception as e:
        print(f"[ERREUR NLP] : {e}")
        flash(f"Erreur lors du traitement OCR : {e}", "danger")
        return redirect(url_for("user_capture"))

    answer = None
    question = None

    if request.method == "POST":
        question = request.form.get("question", "").strip()
        if question:
            # Les données sont déjà en mémoire grâce au cache
            answer = nlp_system.ask_question(question)

    return render_template("user_question.html", 
                         capture_id=capture_id, 
                         question=question, 
                         answer=answer)

@app.route("/user/question_chatgpt/<capture_id>", methods=["GET", "POST"])
def user_question_gemini(capture_id):
    """Questions avec Gemini - OPTIMISÉ AVEC CACHE"""
    image_filename = f"{capture_id}.png"
    absolute_image_path = os.path.join(app.config["ORIGINALS_FOLDER"], image_filename)

    # ✅ OPTIMISATION : OCR avec cache
    try:
        clear_old_cache_entries()
        result = process_ocr_with_cache(capture_id, absolute_image_path)
        
        # Récupérer le contexte (maintenant en cache)
        if hasattr(nlp_system.qa_system, 'sentences') and nlp_system.qa_system.sentences:
            context_text = " ".join(nlp_system.qa_system.sentences)
        else:
            context_text = "Aucun contenu extrait de l'image."
            
    except Exception as e:
        print(f"[ERREUR OCR] : {e}")
        context_text = f"Erreur lors de l'extraction OCR : {e}"

    answer = None
    question = None

    if request.method == "POST":
        question = request.form.get("question", "").strip()
        if question:
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                answer = "Clé API Gemini manquante (variable d'environnement)"
            else:
                try:
                    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
                    headers = {"Content-Type": "application/json"}
                    payload = {
                        "contents": [
                            {
                                "parts": [
                                    {
                                        "text": f"{context_text}\n\nQuestion: {question}\nRéponds en français :"
                                    }
                                ]
                            }
                        ]
                    }
                    params = {"key": api_key}

                    response = requests.post(url, headers=headers, params=params, json=payload)
                    response.raise_for_status()

                    gemini_data = response.json()
                    answer = gemini_data["candidates"][0]["content"]["parts"][0]["text"]
                except Exception as e:
                    answer = f"Erreur Gemini : {e}"

    return render_template("user_question.html", 
                         capture_id=capture_id, 
                         question=question, 
                         answer=answer)


@app.route("/user/question_local_llm/<capture_id>", methods=["GET", "POST"])
def user_question_local_llm(capture_id):
    """Questions avec LLM local (Ollama) - OPTIMISÉ AVEC CACHE"""
    image_filename = f"{capture_id}.png"
    absolute_image_path = os.path.join(app.config["ORIGINALS_FOLDER"], image_filename)

    # ✅ OPTIMISATION : OCR avec cache
    try:
        clear_old_cache_entries()
        result = process_ocr_with_cache(capture_id, absolute_image_path)
        
        # Récupérer le contexte (maintenant en cache)
        if hasattr(nlp_system.qa_system, 'sentences') and nlp_system.qa_system.sentences:
            context_text = " ".join(nlp_system.qa_system.sentences)
        else:
            context_text = "Aucun contenu extrait de l'image."
            
    except Exception as e:
        print(f"[ERREUR OCR] : {e}")
        context_text = f"Erreur lors de l'extraction OCR : {e}"

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
                    "stream": False
                })

                data = response.json()
                answer = data.get('message', {}).get('content') or data.get('response', '').strip()

            except Exception as e:
                answer = f"Erreur LLM local : {e}"

    return render_template("user_question.html", 
                         capture_id=capture_id, 
                         question=question, 
                         answer=answer)

@app.route("/admin/cache_status")
def admin_cache_status():
    """Affichage du statut du cache OCR"""
    if not is_admin_logged_in():
        return jsonify({"error": "Non autorisé"}), 401
    
    cache_info = []
    total_size = 0
    
    for capture_id, data in ocr_cache.items():
        size_estimate = (
            len(data.get('sentences', [])) * 50 +  # Estimation taille phrases
            len(str(data.get('sentence_vectors', ''))) +
            len(data.get('topics', [])) * 100
        )
        total_size += size_estimate
        
        cache_info.append({
            'capture_id': capture_id,
            'sentences_count': len(data.get('sentences', [])),
            'topics_count': len(data.get('topics', [])),
            'processing_time': f"{data.get('processing_time', 0):.2f}s",
            'timestamp': datetime.fromtimestamp(data.get('timestamp', 0)).strftime('%H:%M:%S'),
            'size_estimate': f"{size_estimate / 1024:.1f} KB"
        })
    
    return jsonify({
        'total_entries': len(ocr_cache),
        'total_size_estimate': f"{total_size / 1024:.1f} KB",
        'entries': cache_info
    })

@app.route("/admin/clear_ocr_cache", methods=["POST"])
def admin_clear_ocr_cache():
    """Vider le cache OCR manuellement"""
    if not is_admin_logged_in():
        flash("Veuillez vous connecter pour effectuer cette action.", "warning")
        return redirect(url_for("login"))
    
    global ocr_cache
    entries_count = len(ocr_cache)
    ocr_cache.clear()
    
    flash(f"Cache OCR vidé : {entries_count} entrées supprimées.", "success")
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/preload_ocr/<capture_id>", methods=["POST"])
def admin_preload_ocr(capture_id):
    """Précharger l'OCR pour une image spécifique"""
    if not is_admin_logged_in():
        return jsonify({"error": "Non autorisé"}), 401
    
    image_filename = f"{capture_id}.png"
    absolute_image_path = os.path.join(app.config["ORIGINALS_FOLDER"], image_filename)
    
    if not os.path.exists(absolute_image_path):
        return jsonify({"error": "Image non trouvée"}), 404
    
    try:
        result = process_ocr_with_cache(capture_id, absolute_image_path)
        return jsonify({
            "status": "success",
            "message": f"OCR préchargé pour {capture_id}",
            "result": result
        })
    except Exception as e:
        return jsonify({"error": f"Erreur préchargement : {e}"}), 500

# ═══════════════════════════════════════════════════════════════════
# ROUTE POUR PRÉCHARGER L'OCR DEPUIS LA PAGE DE CAPTURE
# ═══════════════════════════════════════════════════════════════════

@app.route("/user/preload_nlp/<capture_id>", methods=["POST"])
def user_preload_nlp(capture_id):
    """Précharger l'OCR en arrière-plan pour l'utilisateur"""
    try:
        image_filename = f"{capture_id}.png"
        absolute_image_path = os.path.join(app.config["ORIGINALS_FOLDER"], image_filename)
        
        if not os.path.exists(absolute_image_path):
            return jsonify({"error": "Image non trouvée"}), 404
        
        result = process_ocr_with_cache(capture_id, absolute_image_path)
        
        return jsonify({
            "status": "success",
            "message": "OCR préchargé avec succès",
            "sentences_count": len(nlp_system.qa_system.sentences) if hasattr(nlp_system.qa_system, 'sentences') else 0
        })
        
    except Exception as e:
        return jsonify({"error": f"Erreur préchargement : {e}"}), 500 

# ═══════════════════════════════════════════════════════════════════
# ROUTE DE DEBUG POUR TESTER L'OCR
# ═══════════════════════════════════════════════════════════════════

@app.route("/debug/test_ocr/<capture_id>")
def debug_test_ocr(capture_id):
    """Route de debug pour tester l'OCR"""
    if not is_admin_logged_in():
        return jsonify({"error": "Non autorisé"}), 401
    
    image_filename = f"{capture_id}.png"
    absolute_image_path = os.path.join(app.config["ORIGINALS_FOLDER"], image_filename)
    
    if not os.path.exists(absolute_image_path):
        return jsonify({"error": f"Image non trouvée : {absolute_image_path}"}), 404
    
    try:
        # Test du système OCR
        start_time = time.time()
        result = nlp_system.process_image_optimized(
            absolute_image_path, 
            use_layout=True,
            parallel=True
        )
        end_time = time.time()
        
        # Statistiques
        stats = {
            "traitement_temps": f"{end_time - start_time:.2f}s",
            "result": result,
            "nb_phrases": len(nlp_system.qa_system.sentences) if hasattr(nlp_system.qa_system, 'sentences') else 0,
            "nb_phrases_indexees": len(nlp_system.qa_system._sample_sentences) if hasattr(nlp_system.qa_system, '_sample_sentences') else 0,
            "topics": nlp_system.qa_system.topics if hasattr(nlp_system.qa_system, 'topics') else [],
            "image_path": absolute_image_path,
            "image_exists": os.path.exists(absolute_image_path)
        }
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({"error": f"Erreur OCR : {e}"}), 500

# ═══════════════════════════════════════════════════════════════════
# OPTIMISATION MÉMOIRE POUR PRODUCTION
# ═══════════════════════════════════════════════════════════════════

@app.route("/admin/clear_nlp_cache", methods=["POST"])
def admin_clear_nlp_cache():
    """Vider le cache NLP pour libérer la mémoire"""
    if not is_admin_logged_in():
        flash("Veuillez vous connecter pour effectuer cette action.", "warning")
        return redirect(url_for("login"))
    
    try:
        # Réinitialiser le système NLP
        global nlp_system
        del nlp_system
        
        nlp_system = CompleteOCRQASystem(
            language='french', 
            ocr_lang='fr',
            max_image_height=2000,
            use_gpu=False,
            cpu_optimized=True
        )
        
        flash("Cache NLP vidé et système réinitialisé.", "success")
        
    except Exception as e:
        flash(f"Erreur lors du vidage du cache : {e}", "danger")
    
    return redirect(url_for("admin_dashboard"))


# @app.route("/user/question_chatgpt/<capture_id>", methods=["GET", "POST"])
# def user_question_chatgpt(capture_id):
#     """Questions avec ChatGPT"""
#     image_filename = f"{capture_id}.png"
#     absolute_image_path = os.path.join(app.config["ORIGINALS_FOLDER"], image_filename)

#     nlp_system.process_image_optimized(absolute_image_path, use_layout=True)
#     context_text = " ".join(nlp_system.qa_system.sentences)

#     answer = None
#     question = None

#     if request.method == "POST":
#         question = request.form.get("question", "").strip()
#         if question:
#             api_key = os.getenv("OPENAI_API_KEY")
#             if not api_key:
#                 answer = "Clé API OpenAI manquante"
#             else:
#                 try:
#                     client = openai.OpenAI(api_key=api_key)
#                     prompt = f"{context_text}\n\nQuestion: {question}\nRéponds en français :"
#                     response = client.chat.completions.create(
#                         model="gpt-3.5-turbo",
#                         messages=[{"role": "user", "content": prompt}]
#                     )
#                     answer = response.choices[0].message.content.strip()
#                 except Exception as e:
#                     answer = f"Erreur OpenAI : {e}"

#     return render_template("user_question.html", capture_id=capture_id, question=question, answer=answer)

#════════════════════════════════════════════════════════════
# ROUTES DE SERVICE (FICHIERS STATIQUES)
# ═══════════════════════════════════════════════════════════════════

@app.route("/data/originals/<filename>")
def serve_original_image(filename):
    """Servir les images originales"""
    return send_from_directory(os.path.join(app.root_path, "data", "originals"), filename)

@app.route("/data/annotated/<filename>")
def serve_annotated_image(filename):
    """Servir les images annotées"""
    return send_from_directory(app.config["ANNOTATED_FOLDER"], filename)

@app.route("/data/suppression/<filename>")
def serve_suppressed_image(filename):
    """Servir les images avec suppressions"""
    suppression_dir = os.path.join(app.root_path, "data", "suppression")
    return send_from_directory(suppression_dir, filename)

@app.route("/data/human_data/<filename>")
def serve_human_data_image(filename):
    """Servir les images du dossier human_data"""
    return send_from_directory(app.config["HUMAN_DATA_FOLDER"], filename)

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

@app.route("/user/manual/serve_annotated/<filename>")
def serve_manual_annotated_image(filename):
    """Servir les images annotées par l'utilisateur"""
    base_dir = os.path.dirname(current_app.root_path)
    folder = os.path.join(base_dir, "app", "data", "annoted_by_human")
    file_path = os.path.join(folder, filename)

    if not os.path.exists(file_path):
        print("[404 ERROR] File does not exist:", file_path)
        abort(404)

    return send_file(file_path, mimetype="image/jpeg")

@app.route("/user/manual/serve_filtered/<filename>")
def serve_filtered_manual_image(filename):
    """Servir les images filtrées manuelles"""
    image_path = os.path.join(SUPPRESSION_HUMAN_FOLDER, filename)

    if not os.path.exists(image_path):
        print("[404] Image filtrée manuelle introuvable :", image_path)
        abort(404)

    return send_file(image_path, mimetype="image/jpeg")

@app.route("/download/final_image/<filename>")
def download_final_image(filename):
    """Téléchargement des images finales"""
    suppression_dir = os.path.join(app.root_path, "data", "suppression")
    file_path = os.path.join(suppression_dir, filename)
    if not os.path.exists(file_path):
        flash("Fichier introuvable.", "danger")
        return redirect(url_for("index"))
    return send_file(file_path, as_attachment=True)

# ═══════════════════════════════════════════════════════════════════
# ROUTES DE DEBUG ET MAINTENANCE
# ═══════════════════════════════════════════════════════════════════

@app.route("/debug/check_annotated/<capture_id>")
def debug_check_annotated(capture_id):
    """Route de debug pour vérifier les fichiers d'annotation"""
    if not is_admin_logged_in():
        return jsonify({"error": "Non autorisé"}), 401
    
    base_dir = os.path.dirname(current_app.root_path)
    
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

# ═══════════════════════════════════════════════════════════════════
# ROUTES D'ERREUR
# ═══════════════════════════════════════════════════════════════════

@app.errorhandler(404)
def not_found_error(error):
    """Gestionnaire d'erreur 404"""
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Gestionnaire d'erreur 500"""
    return render_template('errors/500.html'), 500

 
