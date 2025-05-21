import os
import cv2
import torch
import pickle
import json
from detectron2.config import get_cfg
from detectron2.engine import DefaultPredictor
from detectron2.data import MetadataCatalog
from playwright.sync_api import sync_playwright
from PIL import Image

# ================================
#  Configuration générale
# ================================
INPUT_URL = "https://example.com"
SCREENSHOT_PATH = "screenshot.jpg"
RESIZED_IMAGE_PATH = "resized_input.jpg"
ANNOTATED_IMAGE_PATH = "annotated_output.jpg"
COCO_OUTPUT_PATH = "predictions_resize_coco.json"
TARGET_WIDTH, TARGET_HEIGHT = 1024, 1024
MODEL_DIR = "output_detectron_web"

# ================================
#  Capture d'écran avec Playwright
# ================================
def capture_screenshot(url, save_path, width=1583, height=2048):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": width, "height": height})
        page.goto(url, timeout=15000)
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(3000)
        page.screenshot(path=save_path, full_page=True)
        browser.close()
        print(f"[✅] Screenshot sauvegardé : {save_path}")

# ================================
# 🔧 Mise à l’échelle (resize image)
# ================================
def resize_image(image_path, target_w, target_h):
    image = cv2.imread(image_path)
    original_h, original_w = image.shape[:2]
    resized = cv2.resize(image, (target_w, target_h))
    cv2.imwrite(RESIZED_IMAGE_PATH, resized)
    return image, resized, original_w / target_w, original_h / target_h

# ================================
#  Chargement du modèle et prédiction
# ================================
def load_predictor(model_dir):
    with open(os.path.join(model_dir, "config.pkl"), "rb") as f:
        cfg = pickle.load(f)
    cfg.MODEL.WEIGHTS = os.path.join(model_dir, "model_final.pth")
    return DefaultPredictor(cfg), MetadataCatalog.get(cfg.DATASETS.TRAIN[0]), cfg

def predict_on_image(predictor, image):
    outputs = predictor(image)
    return outputs["instances"].to("cpu")

# ================================
#  Redimensionnement des prédictions
# ================================
def scale_boxes(boxes, scale_x, scale_y):
    scaled = boxes.tensor.numpy()
    scaled[:, [0, 2]] *= scale_x
    scaled[:, [1, 3]] *= scale_y
    return scaled.astype(int)

# ================================
#  Annotation avec OpenCV
# ================================
def annotate_image(image, boxes, classes, class_names, output_path):
    annotated = image.copy()
    for box, cls in zip(boxes, classes):
        x1, y1, x2, y2 = box
        label = class_names[cls]
        cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(annotated, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    cv2.imwrite(output_path, annotated)
    print(f"[🖼️] Image annotée sauvegardée : {output_path}")

# ================================
#  Export COCO (sur image RESIZE)
# ================================
def export_coco(instances, metadata, output_path, image_file, width, height):
    coco_output = {
        "images": [{"id": 1, "file_name": image_file, "width": width, "height": height}],
        "annotations": [],
        "categories": [{"id": i, "name": name} for i, name in enumerate(metadata.thing_classes)]
    }

    for i, box in enumerate(instances.pred_boxes.tensor.numpy()):
        x, y, x2, y2 = box
        coco_output["annotations"].append({
            "id": i,
            "image_id": 1,
            "category_id": int(instances.pred_classes[i]),
            "bbox": [float(x), float(y), float(x2 - x), float(y2 - y)],
            "area": float((x2 - x) * (y2 - y)),
            "iscrowd": 0
        })

    with open(output_path, "w") as f:
        json.dump(coco_output, f, indent=2)
        print(f"[📄] COCO JSON exporté : {output_path}")

# ================================
#  Pipeline complet
# ================================
if __name__ == "__main__":
    # Étape 1 : capture
    capture_screenshot(INPUT_URL, SCREENSHOT_PATH)

    # Étape 2 : resize
    img_orig, img_resized, scale_x, scale_y = resize_image(SCREENSHOT_PATH, TARGET_WIDTH, TARGET_HEIGHT)

    # Étape 3 : prédiction
    predictor, metadata, cfg = load_predictor(MODEL_DIR)
    instances = predict_on_image(predictor, img_resized)

    # Étape 4 : mise à l’échelle
    boxes_scaled = scale_boxes(instances.pred_boxes, scale_x, scale_y)
    class_ids = instances.pred_classes.numpy()

    # Étape 5 : annotation
    annotate_image(img_orig, boxes_scaled, class_ids, metadata.thing_classes, ANNOTATED_IMAGE_PATH)

    # Étape 6 : export COCO (sur image resize)
    export_coco(instances, metadata, COCO_OUTPUT_PATH, os.path.basename(RESIZED_IMAGE_PATH), TARGET_WIDTH, TARGET_HEIGHT)
