# 📦 Modèle de détection - SmartWebScraper-CV

![Hugging Face Model](https://img.shields.io/badge/HuggingFace-Model-orange?logo=huggingface)

Ce dossier contient le modèle fine-tuné `faster_rcnn_R_101_FPN_3x` basé sur [Detectron2 (Facebook AI)](https://github.com/facebookresearch/detectron2), utilisé pour détecter automatiquement les éléments visuels d’une page web (headers, footers, médias, publicités, etc.).

- 🔍 **Modèle fine-tuné (Version 1)** sur 200 images contenant au total **19 classes annotées** :
  👉 [Accès Hugging Face - Modèle](https://huggingface.co/DJERI-ALASSANI/MINESMARTWEBSCRAPERCV)

- 🧾 **Dataset utilisé pour l'entraînement** (format COCO) :
  👉 [Accès Hugging Face - Dataset](https://huggingface.co/datasets/DJERI-ALASSANI/MINESMARTWEBSCRAPERCV-datasetV2/tree/main)
consulte https://github.com/ZIADEA/SmartWebScraper-CV/tree/main/data for more info about the data 
---

## 📊 Résultats du modèle

Notre modèle a été entraîné sur un petit dataset, ce qui limite actuellement ses performances. Nous comptons l’**agrandir prochainement in shaa Allah** pour améliorer l’**AP global**.

### 🔢 Métriques COCO (bbox)

| Métrique | Valeur |
|----------|--------|
| AP | 10.39 |
| AP50 | 21.51 |
| AP75 | 8.17 |
| APs | 0.88 |
| APm | 16.92 |
| APl | 18.32 |

### 📌 AP par classe (principaux résultats)

| Classe | AP (%) |
|------------------|---------|
| `footer` | 53.62 |
| `header` | 33.79 |
| `right sidebar` | 30.10 |
| `pop up` | 26.05 |
| `advertisement` | 21.72 |
| `media` | 12.43 |
| `title` | 6.44 |
| `logo` | 2.82 |
| Autres classes | 0.00 |

### 📉 Métriques de formation

| Métrique | Valeur |
|-------------------------------|----------------|
| `loss_box_reg` | 0.1857 |
| `loss_cls` | 2.8791 |
| `loss_rpn_cls` | 0.7188 |
| `loss_rpn_loc` | 0.0695 |
| `total_loss` | 3.8531 |
| `lr` | 2.5e-07 |
| `data_time` | 0.7916 |
| `fast_rcnn/cls_accuracy` | 0.0156 |
| `fast_rcnn/fg_cls_accuracy` | 0.2500 |
| `roi_head/num_bg_samples` | 60.0 |
| `roi_head/num_fg_samples` | 4.0 |
| `rpn/num_neg_anchors` | 229.0 |
| `rpn/num_pos_anchors` | 27.0 |

Les pertes (`loss`) ont diminué régulièrement jusqu'à atteindre **~1.13** en `total_loss`, avec une réduction constante de `loss_cls`, `loss_box_reg`, `loss_rpn_cls`, ce qui montre un bon apprentissage progressif.

---

## 🪪 Licence

Ce modèle est mis à disposition sous la **Licence DJERI**, c’est-à-dire :
> **Libre pour usage personnel, académique et collaboratif. Toute réutilisation dans un cadre commercial ou sans citation est interdite.**

---

📩 Pour toute question ou collaboration :
**djeryala@gmail.com**
