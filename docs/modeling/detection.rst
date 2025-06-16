Détection d'Objets : Modélisation et Fine-Tuning
===============================================

Cette section détaille les choix architecturaux, l'entraînement et l'intégration des modèles 
de détection d'objets pour l'annotation automatique des pages web.

Choix du Modèle de Détection
=============================

Analyse Comparative des Architectures
--------------------------------------

Plusieurs architectures de détection d'objets ont été évaluées pour ce projet :

.. list-table:: Comparaison des Modèles Candidats
   :header-rows: 1
   :widths: 20 25 25 30

   * - **Architecture**
     - **Avantages**
     - **Inconvénients**
     - **Adaptation au Projet**
   * - **YOLOv5**
     - Vitesse d'inférence
     - Moins précis sur petites zones
     - ❌ Inadapté aux headers étroits
   * - **SSD MobileNet**
     - Léger, déployable mobile
     - Précision limitée
     - ❌ Imprécis sur zones complexes
   * - **Faster R-CNN**
     - Excellente précision
     - Plus lent que YOLO
     - ✅ **Choix retenu**

Justification du Choix : Faster R-CNN
--------------------------------------

.. grid:: 2

   .. grid-item-card:: 🎯 Précision Supérieure
      
      * Excellentes performances sur objets complexes
      * Gestion optimale des zones de tailles variées
      * ROI Pooling adapté aux layouts web

   .. grid-item-card:: 🔧 Facilité d'Intégration
      
      * Support natif du format COCO
      * Framework Detectron2 robuste
      * Configuration flexible via fichiers YAML

**Configuration Finale Sélectionnée :**

.. code-block:: yaml

   MODEL:
     META_ARCHITECTURE: "GeneralizedRCNN"
     BACKBONE:
       NAME: "build_resnet_fpn_backbone"
     RESNETS:
       DEPTH: 50
       OUT_FEATURES: ["res2", "res3", "res4", "res5"]
     FPN:
       IN_FEATURES: ["res2", "res3", "res4", "res5"]
     ROI_HEADS:
       NUM_CLASSES: 18  # 18 classes + background

Architecture Technique Détaillée
=================================

Faster R-CNN avec ResNet-50 + FPN
----------------------------------

.. mermaid::

   flowchart TD
       A[Image Input 1280×H] --> B[ResNet-50 Backbone]
       B --> C[Feature Pyramid Network]
       C --> D[Region Proposal Network]
       C --> E[ROI Head]
       D --> F[Object Proposals]
       F --> E
       E --> G[Classification + BBox Regression]
       G --> H[Final Detections]

**Composants Clés :**

1. **ResNet-50 Backbone**
   
   * 50 couches de convolution
   * Skip connections pour éviter la dégradation
   * Extraction de features multi-échelles

2. **Feature Pyramid Network (FPN)**
   
   * Fusion des features haute et basse résolution
   * Améliore la détection d'objets de tailles variées
   * Crucial pour header/footer étroits vs content large

3. **Region Proposal Network (RPN)**
   
   * Génère ~2000 propositions d'objets par image
   * Ancres de 3 échelles × 3 ratios d'aspect
   * Filtrage par score de "objectness"

4. **ROI Head**
   
   * Classification finale en 18+1 classes
   * Régression précise des bounding boxes
   * Non-Maximum Suppression pour éliminer les doublons

Entraînement Initial
====================

Configuration d'Entraînement
-----------------------------

.. code-block:: python

   # Configuration Detectron2
   from detectron2.config import get_cfg
   from detectron2 import model_zoo
   
   cfg = get_cfg()
   cfg.merge_from_file(model_zoo.get_config_file(
       "COCO-Detection/faster_rcnn_R_50_FPN_3x.yaml"))
   
   # Dataset personnalisé
   cfg.DATASETS.TRAIN = ("web_scraper_train",)
   cfg.DATASETS.TEST = ("web_scraper_val",)
   
   # Hyperparamètres
   cfg.SOLVER.MAX_ITER = 10000
   cfg.SOLVER.BASE_LR = 0.00025
   cfg.SOLVER.STEPS = (7000, 9000)
   cfg.SOLVER.GAMMA = 0.1
   cfg.MODEL.ROI_HEADS.BATCH_SIZE_PER_IMAGE = 256
   cfg.MODEL.ROI_HEADS.NUM_CLASSES = 18

Évolution des Modèles
---------------------

.. list-table:: Progression des Modèles Entraînés
   :header-rows: 1
   :widths: 25 15 15 15 30

   * - **Version**
     - **Dataset**
     - **Itérations**
     - **mAP@50**
     - **Observations**
   * - faster_rcnn_R_50_DC5_3x
     - 11 images
     - 1000
     - ~10%
     - Proof of concept, sous-ajusté
   * - faster_rcnn_R_50_FPN_3x
     - 200 images
     - 10000
     - **41.6%**
     - Modèle retenu, bon équilibre

Environnement d'Entraînement
=============================

Spécifications Matérielles
---------------------------

.. code-block:: text

   Configuration Locale :
   ├── GPU : NVIDIA RTX 3060 (12 GB VRAM)
   ├── CPU : Intel i7-11700K (8 cores)
   ├── RAM : 32 GB DDR4
   ├── Stockage : SSD NVMe 1TB
   └── OS : Ubuntu 20.04 LTS

.. code-block:: bash

   # Installation environnement
   conda create -n detectron2 python=3.8
   conda activate detectron2
   
   # CUDA 11.3 + PyTorch
   conda install pytorch torchvision torchaudio cudatoolkit=11.3 -c pytorch
   
   # Detectron2
   pip install 'git+https://github.com/facebookresearch/detectron2.git'

Métriques d'Évaluation
======================

Résultats Finaux du Modèle
---------------------------

.. code-block:: text

   Average Precision (AP) @[ IoU=0.50:0.95 ] = 0.416
   Average Precision (AP) @[ IoU=0.50      ] = 0.582
   Average Precision (AP) @[ IoU=0.75      ] = 0.461
   Average Precision (AP) @[ IoU=0.50:0.95 | area=small  ] = nan
   Average Precision (AP) @[ IoU=0.50:0.95 | area=medium ] = 0.202
   Average Precision (AP) @[ IoU=0.50:0.95 | area=large  ] = 0.453

**Performance par Classe :**

.. list-table:: AP par Catégorie (bbox)
   :header-rows: 1
   :widths: 30 20 30 20

   * - **Classe**
     - **AP**
     - **Classe**
     - **AP**
   * - ``header``
     - 63.6%
     - ``advertisement``
     - 16.2%
   * - ``title``
     - 37.3%
     - ``footer``
     - 44.0%
   * - ``media``
     - 63.3%
     - ``logo``
     - 27.3%
   * - ``chaine``
     - 80.0%
     - ``description``
     - 80.0%
   * - ``likes``
     - 30.0%
     - ``right sidebar``
     - 52.3%
   * - ``other``
     - 90.0%
     - ``pop up``
     - 55.3%

Analyse des Performances
=========================

Points Forts du Modèle
-----------------------

.. grid:: 2

   .. grid-item-card:: ✅ Classes Bien Détectées
      
      * ``other`` (90.0% AP) - Éléments génériques
      * ``chaine`` (80.0% AP) - Noms de chaînes YouTube  
      * ``description`` (80.0% AP) - Descriptions vidéos
      * ``header`` (63.6% AP) - En-têtes de sites

   .. grid-item-card:: ✅ Robustesse Spatiale
      
      * Bonne détection des grandes zones (content, media)
      * Gestion correcte des ratios d'aspect variés
      * Précision acceptable sur zones moyennes

Points Faibles Identifiés
--------------------------

.. warning::
   **Limitations observées :**

   * **Classes sous-représentées** : ``advertisement`` (16.2%), ``suggestions`` (18.7%)
   * **Confusions inter-classes** : ``advertisement`` ↔ ``right sidebar``
   * **Déséquilibre du dataset** : Certaines classes avec < 10 exemples
   * **Petits objets** : Difficulté sur logos et boutons de petite taille

Intégration dans l'Application
===============================

Pipeline de Prédiction
-----------------------

.. code-block:: python

   from detectron2.engine import DefaultPredictor
   import cv2
   
   class WebPageDetector:
       def __init__(self, model_path, config_path):
           self.cfg = get_cfg()
           self.cfg.merge_from_file(config_path)
           self.cfg.MODEL.WEIGHTS = model_path
           self.cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.4
           self.predictor = DefaultPredictor(self.cfg)
       
       def predict_boxes(self, image_path):
           image = cv2.imread(image_path)
           outputs = self.predictor(image)
           
           instances = outputs["instances"]
           boxes = instances.pred_boxes.tensor.cpu().numpy()
           classes = instances.pred_classes.cpu().numpy()
           scores = instances.scores.cpu().numpy()
           
           return self.format_predictions(boxes, classes, scores)

Visualisation Interactive
--------------------------

.. code-block:: python

   def visualize_predictions(image, predictions):
       visualizer = Visualizer(
           image[:, :, ::-1], 
           metadata=metadata, 
           scale=0.8
       )
       
       vis = visualizer.draw_instance_predictions(predictions)
       return vis.get_image()[:, :, ::-1]

Optimisations Appliquées
=========================

Filtrage Intelligent
--------------------

.. code-block:: python

   def filter_predictions(predictions, confidence_threshold=0.4):
       # Suppression des doublons par NMS
       keep_indices = nms(
           predictions.pred_boxes.tensor,
           predictions.scores,
           iou_threshold=0.5
       )
       
       # Filtrage par confiance
       high_conf_mask = predictions.scores > confidence_threshold
       
       return predictions[keep_indices & high_conf_mask]

Gestion Mémoire GPU
-------------------

.. code-block:: python

   # Libération mémoire après prédiction
   torch.cuda.empty_cache()
   
   # Traitement par batch pour images volumineuses
   if image_size > MAX_GPU_SIZE:
       predictions = process_in_tiles(image)
   else:
       predictions = predictor(image)

.. tip::
   **Bonnes pratiques identifiées :**
   
   * Seuil de confiance à 0.4 pour équilibrer précision/rappel
   * NMS avec IoU=0.5 pour éliminer les doublons
   * Préservation de la résolution originale pour la précision
   * Validation humaine systématique des prédictions critiques
