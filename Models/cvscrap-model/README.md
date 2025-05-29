# 📦 Modèle de détection - SmartWebScraper-CV

![Hugging Face Model](https://img.shields.io/badge/HuggingFace-Model-orange?logo=huggingface)

Ce dossier contient le modèle fine-tuné `Faster R-CNN` basé sur [Detectron2 (Facebook AI)](https://github.com/facebookresearch/detectron2), utilisé pour détecter automatiquement les éléments visuels d’une page web (headers, footers, médias, publicités, etc.).

- 🔍 **Modèle fine-tuné (Version 1)** sur 159 images contenant au total **19 classes annotées** :  
  👉 [Accès Hugging Face - Modèle](https://huggingface.co/DJERI-ALASSANI/MINESMARTWEBSCRAPERCV)

- 🧾 **Dataset utilisé pour l'entraînement** (format COCO) :  
  👉 [Accès Hugging Face - Dataset](https://huggingface.co/datasets/DJERI-ALASSANI/MINESMARTWEBSCRAPERCV-datasetV1)

---

## 📊 Résultats du modèle

Notre modèle a été entraîné sur un petit dataset, ce qui limite actuellement ses performances. Nous comptons l’**agrandir prochainement in shaa Allah** pour améliorer l’**AP global**.

### 🔢 Métriques COCO (bbox)

| Métrique | Valeur |
|----------|--------|
| AP       | 10.39  |
| AP50     | 21.51  |
| AP75     | 8.17   |
| APs      | 0.88   |
| APm      | 16.92  |
| APl      | 18.32  |

### 📌 AP par classe (principaux résultats)

| Classe           | AP (%)  |
|------------------|---------|
| `footer`         | 53.62   |
| `header`         | 33.79   |
| `right sidebar`  | 30.10   |
| `pop up`         | 26.05   |
| `advertisement`  | 21.72   |
| `media`          | 12.43   |
| `title`          | 6.44    |
| `logo`           | 2.82    |
| Autres classes   | 0.00    |

Les pertes (`loss`) ont diminué régulièrement jusqu'à atteindre **~1.13** en `total_loss`, avec une réduction constante de `loss_cls`, `loss_box_reg`, `loss_rpn_cls`, ce qui montre un bon apprentissage progressif.

---

## 🪪 Licence

Ce modèle est mis à disposition sous la **Licence DJERI**, c’est-à-dire :  
> **Libre pour usage personnel, académique et collaboratif. Toute réutilisation dans un cadre commercial ou sans citation est interdite.**

---

📩 Pour toute question ou collaboration :  
**djeryala@gmail.com**
