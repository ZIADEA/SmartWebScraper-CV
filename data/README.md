# 📊 Dataset Web Layout - SmartWebScraper

Bienvenue sur ce dépôt lié au projet **SmartWebScraper**, un outil d’intelligence artificielle pour la détection, l’annotation et le traitement automatique des zones visuelles d’un site web (headers, footers, contenus, publicités, etc.).

![Hugging Face Dataset](https://img.shields.io/badge/HuggingFace-Dataset-blue?logo=huggingface)

## 🔗 Accès aux Données

### 📁 Google Drive  
Les données utilisées dans ce projet (images annotées, JSON COCO, résultats OCR, etc.) sont disponibles à l'adresse suivante :

👉 [📂 Dossier Google Drive](https://drive.google.com/drive/folders/1u8VqWgju0zX3AU5XCkYyEgCmrMY14xB7?usp=sharing)

### 🤗 Hugging Face Dataset  
Le dataset utilisé pour le fine-tuning de notre modèle de détection est également publié sur Hugging Face :

👉 [📁 Dataset Hugging Face - MINESMARTWEBSCRAPERCV](https://huggingface.co/datasets/DJERI-ALASSANI/MINESMARTWEBSCRAPERCV-datasetV1)


---

## 🏷️ Classes Annotées

Le dataset comprend **19 classes de composants visuels** détectés sur des captures de pages web :

| ID | Classe               | Description courte                                      |
|----|----------------------|----------------------------------------------------------|
| 0  | `header`             | En-tête de page (logo, menu principal, etc.)            |
| 1  | `footer`             | Pied de page (liens utiles, droits, contacts, etc.)     |
| 2  | `advertisement`      | Publicités ou bannières promotionnelles                 |
| 3  | `media`              | Images, vidéos ou éléments multimédias                  |
| 4  | `title`              | Titre principal ou titre de section                     |
| 5  | `content`            | Texte principal ou corps de la page                     |
| 6  | `sidebar`            | Barre latérale (gauche ou droite)                       |
| 7  | `pop up`             | Fenêtres surgissantes ou modales                        |
| 8  | `logo`               | Logo du site ou de l'entreprise                         |
| 9  | `likes`              | Indicateurs de likes, cœurs, évaluations                |
| 10 | `commentaire`        | Zones de commentaires ou réactions utilisateurs         |
| 11 | `description`        | Descriptions courtes, métadonnées ou résumés            |
| 12 | `left sidebar`       | Barre latérale spécifique à gauche                      |
| 13 | `none access`        | Éléments bloqués/inaccessibles (zone restreinte)        |
| 14 | `chaine`             | Informations sur la chaîne, source ou média hébergeant  |
| 15 | `other`              | Autres éléments visuels non classifiables               |
| 16 | `recommendation`     | Suggestions de contenu (produits, vidéos, articles)     |
| 17 | `menu`               | Menu de navigation (généralement dans le header)        |
| 18 | `search bar`         | Barre de recherche                                      |

---

## ℹ️ À propos du projet

Ce projet s’inscrit dans une démarche de recherche autour de la **vision par ordinateur** appliquée au **web scraping visuel**.  
Il vise à créer un pipeline complet :
1. Capture des pages web via Selenium ou Playwright avec utilisation de serAPI et undetected chromedriver
2. Détection automatique des zones clés à l’aide d’un modèle Faster R-CNN (Detectron2)  
3. Annotation automatique ou manuelle  
4. OCR (PaddleOCR) pour extraire les textes utiles  
5. Interaction NLP (résumé automatique, classification de requêtes, etc.)

---

## 📬 Contact

Pour toute question, suggestion ou collaboration, contactez :

📧 **djeryala@gmail.com**

---

## 🪪 Licence

Ce jeu de données est mis à disposition sous la **Licence DJERI**, c’est-à-dire :  
> **Libre pour usage personnel, académique et collaboratif. Toute réutilisation dans un cadre commercial ou sans citation est interdite.**

---

**Merci de citer ce dépôt si vous utilisez ces données dans vos travaux académiques ou projets open source.**
