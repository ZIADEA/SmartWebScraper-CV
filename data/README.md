# 📊 Dataset Web Layout - SmartWebScraper

Bienvenue sur ce dépôt lié au projet **SmartWebScraper**, un outil d’intelligence artificielle pour la détection, l’annotation et le traitement automatique des zones visuelles d’un site web (headers, footers, contenus, publicités, etc.).

## 🔗 Accès aux Données

### 📁 Google Drive
Les données utilisées dans ce projet (images annotées, JSON COCO, résultats OCR, etc.) sont disponibles à l'adresse suivante :

👉 [📂 Dossier Google Drive](https://drive.google.com/drive/folders/1u8VqWgju0zX3AU5XCkYyEgCmrMY14xB7?usp=sharing)

### 🤗 Hugging Face Dataset
Le dataset utilisé pour le fine-tuning de notre modèle de détection est également publié sur Hugging Face :

👉 [📁 Dataset Hugging Face - MINESMARTWEBSCRAPERCV](https://huggingface.co/datasets/DJERI-ALASSANI/MINESMARTWEBSCRAPERCV-datasetV1)

---

## 📂 Contenu du dossier

Le dossier contient :
- `images/` : les captures d’écran annotées de pages web
- `annotations_coco/` : les fichiers d’annotation au format COCO
- `ocr_results/` : les résultats OCR extraits des zones utiles
- `logs/` : les journaux de prédiction et d’exécution
- `README.txt` : description rapide des fichiers

---

## ℹ️ À propos du projet

Ce projet s’inscrit dans une démarche de recherche autour de la **vision par ordinateur** appliquée au **web scraping visuel**.  
Il vise à créer un pipeline complet :
1. Capture des pages web via Selenium/Playwright
2. Détection automatique de zones clés à l’aide de modèles fine-tunés (Detectron2, Faster R-CNN)
3. Annotation automatique ou manuelle
4. OCR pour extraire les textes visibles
5. Interaction NLP (question-réponse, résumé, etc.)

---

## 📬 Contact

Pour toute question ou suggestion, vous pouvez ouvrir une *issue* ou me contacter :

**djeryala@gmail.com**

---

**Merci de citer ce dépôt si vous utilisez ces données dans vos travaux.**
