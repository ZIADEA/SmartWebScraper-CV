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

#NLP
nlp_system = CompleteOCRQASystem(language='french', ocr_lang='fr')

# Vérification initiale
required_configs = [
    'ORIGINALS_FOLDER', 'RESIZED_FOLDER', 'ANNOTATED_FOLDER',
    'PREDICTIONS_RAW_FOLDER', 'PREDICTIONS_SCALED_FOLDER',
    'HUMAN_DATA_FOLDER', 'FINE_TUNE_DATA_FOLDER'
]

for config_key in required_configs:
    if config_key not in app.config:
        raise RuntimeError(f"Configuration manquante: {config_key}")

# Vos routes continuent ici...
# Ensure data directories exist
for folder_key in ["ORIGINALS_FOLDER", "RESIZED_FOLDER", "ANNOTATED_FOLDER", 
                   "PREDICTIONS_RAW_FOLDER", "PREDICTIONS_SCALED_FOLDER", 
                   "HUMAN_DATA_FOLDER", "FINE_TUNE_DATA_FOLDER"]:
    os.makedirs(app.config[folder_key], exist_ok=True)

# Ensure visited links file exists
if not os.path.exists(app.config["VISITED_LINKS_FILE"]):
    with open(app.config["VISITED_LINKS_FILE"], 'w') as f:
        json.dump([], f)


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
        # Hardcoded credentials as per spec (replace with secure method later)
        if email == "djeryala@gmail.com" and password == "DJERI":
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

@app.route("/admin/dashboard")
def admin_dashboard():
    # Page 1.2.1: Admin dashboard
    if not is_admin_logged_in():
        flash("Please log in to access this page.", "warning")
        return redirect(url_for("login"))
    # Render the admin dashboard template
    return render_template("admin_dashboard.html")

@app.route("/admin/visited_links")
def admin_visited_links():
    # Page 1.2.1.1: Display visited links
    if not is_admin_logged_in():
        flash("Please log in to access this page.", "warning")
        return redirect(url_for("login"))
    
    links = load_visited_links()
    # Render the template, passing the links data
    return render_template("admin_visited_links.html", links=links)

@app.route("/admin/human_data/<data_type>") # data_type can be 'validated_predictions' or 'manual_annotations'
def admin_view_human_data(data_type):
    # Page 1.2.1.2 / 1.2.1.3: Display data from human_data folder
    if not is_admin_logged_in():
        flash("Please log in to access this page.", "warning")
        return redirect(url_for("login"))

    human_data_path = app.config["HUMAN_DATA_FOLDER"]
    items = []
    try:
        # --- Placeholder: Logic to list and categorize items in human_data --- 
        # This should ideally parse JSON files or filenames to distinguish types
        # and pair images with their corresponding JSON annotations.
        all_files = os.listdir(human_data_path)
        # Simple simulation: list all files, assuming pairs exist
        for filename in all_files:
            if filename.lower().endswith(".png"): # Assuming images are PNG
                json_filename = os.path.splitext(filename)[0] + ".json"
                if json_filename in all_files:
                    # Need a way to determine if it's model-validated or manual
                    # For simulation, we'll just list everything for now
                    item_id = os.path.splitext(filename)[0] # Use filename stem as ID
                    items.append({
                        "id": item_id,
                        "image_filename": filename,
                        "json_filename": json_filename,
                        "type": "unknown" # Needs proper categorization
                    })
        # --- End Placeholder ---
    except FileNotFoundError:
        flash("Le dossier human_data n'existe pas.", "danger")
    except Exception as e:
        flash(f"Erreur lors de la lecture de human_data: {e}", "danger")

    title = "Prédictions Validées" if data_type == "validated_predictions" else "Annotations Manuelles"
    # Render the template displaying the grid of items
    return render_template("admin_view_human_data.html", items=items, title=title, data_type=data_type)

@app.route("/admin/item_detail/<item_id>") # item_id might be the filename stem
def admin_view_item_detail(item_id):
    # Page 1.2.1.2.1 / 1.2.1.3.1: Display details of an item from human_data
    if not is_admin_logged_in():
        flash("Please log in to access this page.", "warning")
        return redirect(url_for("login"))

    # --- Placeholder: Logic to find the specific item (image + JSON) in human_data --- 
    human_data_path = app.config["HUMAN_DATA_FOLDER"]
    image_filename = f"{item_id}.png" # Assuming PNG format
    json_filename = f"{item_id}.json"
    image_path_local = os.path.join(human_data_path, image_filename)
    json_path_local = os.path.join(human_data_path, json_filename)

    if not os.path.exists(image_path_local) or not os.path.exists(json_path_local):
        flash(f"Données pour l'élément {item_id} non trouvées dans human_data.", "danger")
        # Redirect back to the list view (need to know which one)
        # For now, redirect to dashboard
        return redirect(url_for("admin_dashboard")) 

    image_path_url = url_for("serve_human_data_image", filename=image_filename)
    # Load JSON content (optional, for display)
    json_content = "Contenu JSON non chargé (simulation)"
    try:
        with open(json_path_local, 'r') as f:
            # Limit reading for display?
            # json_content = json.dumps(json.load(f), indent=2)
            pass # Keep it simple for now
    except Exception as e:
        json_content = f"Erreur lecture JSON: {e}"
    # --- End Placeholder ---

    # Render the detail view template
    return render_template("admin_view_item_detail.html", 
                           item_id=item_id,
                           image_path_url=image_path_url,
                           image_filename=image_filename,
                           json_filename=json_filename,
                           json_content=json_content)

@app.route("/admin/validate_item/<item_id>", methods=["POST"])
def admin_validate_item(item_id):
    # Action from Page 1.2.1.2.1 / 1.2.1.3.1: Move item from human_data to fine_tune_data
    if not is_admin_logged_in():
        flash("Please log in to perform this action.", "warning")
        return redirect(url_for("login"))

    human_data_path = app.config["HUMAN_DATA_FOLDER"]
    fine_tune_data_path = app.config["FINE_TUNE_DATA_FOLDER"]
    image_filename = f"{item_id}.png" # Assuming PNG
    json_filename = f"{item_id}.json"
    src_image_path = os.path.join(human_data_path, image_filename)
    src_json_path = os.path.join(human_data_path, json_filename)
    dest_image_path = os.path.join(fine_tune_data_path, image_filename)
    dest_json_path = os.path.join(fine_tune_data_path, json_filename)

    try:
        if os.path.exists(src_image_path) and os.path.exists(src_json_path):
            # Ensure destination directory exists
            os.makedirs(fine_tune_data_path, exist_ok=True)
            # Move files
            shutil.move(src_image_path, dest_image_path)
            shutil.move(src_json_path, dest_json_path)
            flash(f"Élément {item_id} validé et déplacé vers fine_tune_data.", "success")
        else:
            flash(f"Fichiers pour l'élément {item_id} non trouvés dans human_data.", "danger")
    
    except Exception as e:
        flash(f"Erreur lors de la validation de l'élément {item_id}: {e}", "danger")

    # Redirect back to dashboard (or ideally, the previous list view)
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/delete_item/<item_id>", methods=["POST"])
def admin_delete_item(item_id):
    # Action from Page 1.2.1.2.1 / 1.2.1.3.1: Delete item from human_data
    if not is_admin_logged_in():
        flash("Please log in to perform this action.", "warning")
        return redirect(url_for("login"))

    human_data_path = app.config["HUMAN_DATA_FOLDER"]
    image_filename = f"{item_id}.png" # Assuming PNG
    json_filename = f"{item_id}.json"
    image_path_local = os.path.join(human_data_path, image_filename)
    json_path_local = os.path.join(human_data_path, json_filename)

    deleted = False
    try:
        if os.path.exists(image_path_local):
            os.remove(image_path_local)
            deleted = True
        if os.path.exists(json_path_local):
            os.remove(json_path_local)
            deleted = True
        
        if deleted:
            flash(f"Élément {item_id} supprimé de human_data.", "success")
        else:
            flash(f"Élément {item_id} non trouvé dans human_data.", "warning")

    except Exception as e:
        flash(f"Erreur lors de la suppression de l'élément {item_id}: {e}", "danger")

    # Redirect back to dashboard (or ideally, the previous list view)
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/fine_tune_data")
def admin_fine_tune_data():
    # Page 1.2.1.4: Display count of items in fine_tune_data and option to launch fine-tuning
    if not is_admin_logged_in():
        flash("Please log in to access this page.", "warning")
        return redirect(url_for("login"))

    fine_tune_data_path = app.config["FINE_TUNE_DATA_FOLDER"]
    image_count = 0
    try:
        # Count pairs of image/json files
        all_files = os.listdir(fine_tune_data_path)
        image_files = {os.path.splitext(f)[0] for f in all_files if f.lower().endswith(('.png', '.jpg', '.jpeg'))}
        json_files = {os.path.splitext(f)[0] for f in all_files if f.lower().endswith('.json')}
        image_count = len(image_files.intersection(json_files))
    except FileNotFoundError:
        flash("Le dossier fine_tune_data n'existe pas.", "warning") # Warning, not danger, as it might just be empty
    except Exception as e:
        flash(f"Erreur lors de la lecture de fine_tune_data: {e}", "danger")

    # Render the template displaying the count and the button
    return render_template("admin_fine_tune_data.html", image_count=image_count)


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

@app.route("/user/question/<capture_id>", methods=["GET", "POST"])
def user_question(capture_id):
    image_path = os.path.join(app.config["ORIGINALS_FOLDER"], f"{capture_id}.png")

    capture_info = find_capture_by_id(capture_id)
    # === 1. Récupérer le nom du fichier image
    image_filename = f"{capture_info['capture_id']}.png"

    # === 2. Déterminer le chemin absolu réel (pour OCR)
    absolute_image_path = os.path.join(app.config["ORIGINALS_FOLDER"], image_filename)

    # === 3. Traiter l'image pour l'OCR/NLP
    nlp_system.process_image(absolute_image_path, use_layout=True)


    # Re-traiter si jamais pas déjà fait (optionnel selon logique)
    nlp_system.process_image(image_path, use_layout=True)

    answer = None
    question = None

    if request.method == "POST":
        question = request.form.get("question", "").strip()
        if question:
            answer = nlp_system.ask_question(question)

    return render_template("user_question.html", capture_id=capture_id, question=question, answer=answer)



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

@app.route("/user/annotate_model/<capture_id>")
def user_annotate_model(capture_id):
    capture_info = find_capture_by_id(capture_id)
    if not capture_info:
        flash("Capture non trouvée.", "danger")
        return redirect(url_for("user_capture"))


    original_image_path = os.path.join(app.config["ORIGINALS_FOLDER"], capture_info["filename"])
    annotated_image_filename = f"annotated_{capture_info['filename']}"
    annotated_image_path_local = os.path.join(app.config["ANNOTATED_FOLDER"], annotated_image_filename)
    coco_json_path = os.path.join(app.config["PREDICTIONS_SCALED_FOLDER"], f"{capture_id}.json")

    cfg = get_cfg()
    cfg.merge_from_file(model_zoo.get_config_file("COCO-Detection/faster_rcnn_R_50_DC5_3x.yaml"))
    cfg.OUTPUT_DIR = os.path.join("app", "models")
    cfg.MODEL.WEIGHTS = os.path.join(cfg.OUTPUT_DIR, "model_final.pth")
    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.3
    cfg.MODEL.ROI_HEADS.NUM_CLASSES = 18
    cfg.MODEL.DEVICE = "cpu"

    thing_classes = [
        "advertisement", "chaine", "commentaire", "description", "header", "footer", "left sidebar",
        "logo", "likes", "media", "pop up", "recommendations", "right sidebar", "suggestions",
        "title", "vues", "none access", "other"
    ]
    unique_class_limit = {
        "footer", "header", "chaine", "commentaire", "description",
        "left sidebar", "likes", "recommendations", "vues", "title", "right sidebar"
    }
    to_ignore_classes = {"pop up", "logo", "other" ,"none access","suggestions"}

    MetadataCatalog.get("web_custom").thing_classes = thing_classes
    metadata = MetadataCatalog.get("web_custom")
    cfg.DATASETS.TEST = ("web_custom",)
    predictor = DefaultPredictor(cfg)

    img = cv2.imread(original_image_path)
    outputs = predictor(img)
    instances = outputs["instances"].to("cpu")

    boxes = instances.pred_boxes.tensor.numpy()
    labels = instances.pred_classes.numpy()
    scores = instances.scores.numpy()

    annotated = img.copy()
    detected_boxes = []
    annotations = []

    kept = {}  # pour unique box per class

    for i, box in enumerate(boxes):
        class_id = int(labels[i])
        class_name = thing_classes[class_id]
        score = float(scores[i])

        if class_name in to_ignore_classes:
            continue

        if class_name in unique_class_limit:
            if class_name in kept:
                if score > kept[class_name]["score"]:
                    kept[class_name] = {"index": i, "score": score}
                continue
            else:
                kept[class_name] = {"index": i, "score": score}
        else:
            kept[f"{class_name}_{i}"] = {"index": i, "score": score}

    CLASS_COLORS = {
        "advertisement": (255, 0, 0), "chaine": (0, 255, 0), "commentaire": (0, 0, 255),
        "description": (255, 255, 0), "header": (255, 0, 255), "footer": (0, 255, 255),
        "left sidebar": (128, 0, 0), "logo": (0, 128, 0), "likes": (0, 0, 128),
        "media": (128, 128, 0), "po pup": (128, 0, 128), "recommendations": (0, 128, 128),
        "right sidebar": (64, 0, 0), "suggestions": (0, 64, 0), "title": (0, 0, 64),
        "vues": (64, 64, 0), "none access": (64, 0, 64), "other": (0, 64, 64)
    }

    for key, val in kept.items():
        i = val["index"]
        class_id = int(labels[i])
        class_name = thing_classes[class_id]
        score = float(scores[i])
        box_id = f"box{i+1}"

        x1, y1, x2, y2 = map(int, boxes[i])
        color = CLASS_COLORS.get(class_name, (0, 255, 0))
        cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
        cv2.putText(annotated, f"{class_name} {score:.2f}", (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

        detected_boxes.append({"id": box_id, "class": class_name, "coords": [x1, y1, x2, y2], "score": score})
        annotations.append({
            "id": i + 1,
            "image_id": capture_id,
            "category_id": class_id,
            "bbox": [x1, y1, x2 - x1, y2 - y1],
            "score": score
        })

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
    flash(f"Choix des boîtes enregistrés ({len(kept_box_ids)} gardées). Veuillez donner votre feedback.", "info")

    return redirect(url_for("user_feedback", capture_id=capture_id))

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
            flash("Feedback enregistré. Données envoyées pour validation.", "success")
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

    dst_image = os.path.join(save_dir, f"{image_id}.png")
    shutil.copy(src_image, dst_image)

    json_path = os.path.join(save_dir, f"{image_id}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(annotations, f, indent=2, ensure_ascii=False)

    # 📦 COCO format
    coco_path = os.path.join(save_dir, f"{image_id}_coco.json")
    save_annotations_as_coco(image_id, annotations, dst_image, coco_path)

    # 🎯 Dessin avec CV2
    image_out = os.path.join(base_dir, "app", "data", "annoted_by_human", f"annotated_{image_id}.jpg")
    draw_boxes_cv2(dst_image, annotations, image_out)

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

    if not os.path.exists(json_path) or not os.path.exists(img_path):
        flash("Fichiers manquants.", "danger")
        return redirect(url_for("user_capture"))

    if request.method == "POST":
        kept_ids = request.form.getlist("keep_manual_box")
        with open(json_path, "r") as f:
            annotations = json.load(f)

        filtered = [ann for ann in annotations if str(ann.get("id")) in kept_ids]
        with open(json_path, "w") as f:
            json.dump(filtered, f, indent=2)

        # 🧽 Nettoyage des zones supprimées
        output_dir = os.path.join(base_dir, "app", "data", "suppresion_human")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{capture_id}_filtered.jpg")

        remove_zones_from_image(img_path, filtered, output_path)

        return redirect(url_for("manual_display_final_annotation", capture_id=capture_id))

    # → GET
    with open(json_path, "r") as f:
        annotations = json.load(f)

    vis_path = os.path.join(base_dir, "app", "data", "annoted_by_human", f"annotated_{capture_id}.jpg")
    return render_template("user_manual_remove_boxes.html",
                           capture_info=find_capture_by_id(capture_id),
                           annotated_image_path=url_for("serve_manual_annotated_image", filename=f"annotated_{capture_id}.jpg"),
                           manual_boxes=[{
                               "id": str(ann.get("id")),
                               "class": ann.get("value", {}).get("rectanglelabels", ["?"])[0]
                           } for ann in annotations])

@app.route("/user/manual/serve_filtered/<filename>")
def serve_filtered_manual_image(filename):

    base_dir = os.path.dirname(current_app.root_path)
    suppression_dir = os.path.join(base_dir, "app", "data", "suppresion_human")
    image_path = os.path.join(suppression_dir, filename)

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

    output_dir = os.path.join(base_dir, "app", "data", "suppresion_human")
    os.makedirs(output_dir, exist_ok=True)
    output_filename = f"{capture_id}_filtered.jpg"
    output_path = os.path.join(output_dir, output_filename)

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
    base_dir = os.path.dirname(current_app.root_path)
    path = os.path.join(base_dir, "app", "data", "suppresion_human", f"{capture_id}_filtered.jpg")
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


def remove_uniform_bands(img, tolerance=5):
    """
    Supprime les bandes horizontales uniformes (blancs) après la suppression.
    """
    h, w = img.shape[:2]
    keep_rows = []

    for y in range(h):
        row = img[y, :, :]  # ligne entière
        max_diff = np.max(np.abs(row - row[0]))
        if max_diff > tolerance:
            keep_rows.append(y)

    if len(keep_rows) == h:
        return img  # rien à supprimer

    # Reconstruction image nettoyée
    new_img = img[keep_rows, :, :]
    return new_img

def save_manual_annotation_to_human_data(capture_id):
    img_extensions = [".png", ".jpg", ".jpeg"]
    src_img = None

    for ext in img_extensions:
        candidate = os.path.join("static", "images", f"{capture_id}{ext}")
        if os.path.exists(candidate):
            src_img = candidate
            break

    if not src_img:
        raise FileNotFoundError(f"Aucune image trouvée dans static/images pour : {capture_id}")

    src_json = os.path.join("static", "annotations", f"{capture_id}.json")
    if not os.path.exists(src_json):
        raise FileNotFoundError(f"Annotation JSON introuvable pour : {capture_id}")

    dest_dir = os.path.join("data", "human_data", "manual", capture_id)
    os.makedirs(dest_dir, exist_ok=True)

    shutil.copy(src_img, os.path.join(dest_dir, f"{capture_id}.jpg"))  # Toujours enregistrée en .jpg
    shutil.copy(src_json, os.path.join(dest_dir, f"{capture_id}.json"))




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

    image = Image.open(image_path).convert("RGB")
    image_np = np.array(image)
    height, width = image_np.shape[:2]

    for ann in annotations:
        value = ann.get("value") or ann.get("result", [{}])[0].get("value", {})
        label = value.get("rectanglelabels", ["?"])[0]
        x = int(value["x"] / 100.0 * width)
        y = int(value["y"] / 100.0 * height)
        w = int(value["width"] / 100.0 * width)
        h = int(value["height"] / 100.0 * height)

        cv2.rectangle(image_np, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(image_np, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    cv2.imwrite(output_path, image_np)


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
