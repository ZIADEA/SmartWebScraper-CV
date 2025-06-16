Annotation et Structuration du Dataset
=====================================

L'annotation des images constitue l'étape cruciale pour transformer nos captures brutes en données 
d'entraînement exploitables par les modèles de Computer Vision.

Objectif de l'Annotation
=========================

L'objectif principal est de permettre au modèle de détecter visuellement les **zones fonctionnelles** 
d'une page web capturée. Cette détection automatique remplace l'analyse traditionnelle du DOM HTML, 
souvent compromise par l'obfuscation ou le contenu dynamique.

.. mermaid::

   flowchart TD
       A[Image de page web] --> B[Annotation manuelle]
       B --> C[Zones fonctionnelles identifiées]
       C --> D[Format COCO JSON]
       D --> E[Entraînement Detectron2]
       E --> F[Modèle de détection]

Évolution des Classes d'Annotation
===================================

Classes Initiales (Version 1.0)
--------------------------------

Lors du premier test d'annotation, 7 classes avaient été établies :

.. list-table:: Classes V1 - Test Initial
   :header-rows: 1
   :widths: 20 80

   * - **Classe**
     - **Description**
   * - ``title``
     - Titre principal de la page
   * - ``content``
     - Zone de texte central (article, fiche produit, etc.)
   * - ``media``
     - Image, vidéo ou lecteur embarqué
   * - ``header``
     - Bandeau supérieur, souvent identique sur toutes les pages
   * - ``footer``
     - Bas de page contenant liens, mentions, etc.
   * - ``ads``
     - Publicités et contenus sponsorisés
   * - ``sidebar``
     - Barres latérales (menus ou contenus annexes)

.. note::
   Ces 7 classes ont permis d'annoter 14 images de test et de valider la faisabilité 
   de l'approche par Computer Vision.

Classes Étendues (Version 4.0)
-------------------------------

Au cours du développement, l'objectif s'est élargi pour couvrir des cas d'usage plus spécifiques, 
notamment les plateformes vidéo comme YouTube. Le schéma de classes a été étendu à **18 classes** :

.. grid:: 2

   .. grid-item-card:: 🌐 Éléments Génériques Web
      
      * ``header`` - En-tête du site
      * ``footer`` - Pied de page  
      * ``logo`` - Logo du site/plateforme
      * ``media`` - Contenu multimédia principal
      * ``advertisement`` - Zones publicitaires
      * ``left sidebar`` / ``right sidebar`` - Barres latérales
      * ``pop up`` - Fenêtres surgissantes
      * ``none access`` - Zones inaccessibles/masquées
      * ``other`` - Éléments non classés

   .. grid-item-card:: 🎥 Éléments Spécifiques YouTube
      
      * ``title`` - Titre du contenu
      * ``chaine`` - Nom de la chaîne
      * ``description`` - Description du contenu
      * ``likes`` - Système de mentions "j'aime"
      * ``vues`` - Compteur de vues
      * ``commentaire`` - Section commentaires
      * ``recommendations`` - Contenu recommandé
      * ``suggestions`` - Suggestions associées

Justification de l'Extension
=============================

L'extension du nombre de classes répond à plusieurs besoins :

**1. Spécialisation Plateforme**

Les plateformes comme YouTube ont des éléments spécifiques (likes, vues, recommandations) 
qui nécessitent une détection précise pour des analyses d'engagement ou de contenu.

**2. Granularité Fonctionnelle**

La distinction entre ``left sidebar`` et ``right sidebar`` permet une analyse plus fine 
de la mise en page et des stratégies UX.

**3. Robustesse du Modèle**

Plus le modèle est entraîné sur des classes variées, plus il devient robuste 
pour détecter des layouts non-vus pendant l'entraînement.

Défis de l'Annotation Multi-Classes
===================================

Ambiguïtés Inter-Classes
------------------------

.. warning::
   **Difficultés d'annotation identifiées :**

   * **Chevauchement spatial** : ``media`` parfois inclus dans ``content``
   * **Ambiguïté fonctionnelle** : ``advertisement`` vs ``suggestions``
   * **Variabilité contextuelle** : ``header`` peut contenir ``logo`` et navigation
   * **Granularité subjective** : différence entre ``other`` et classes spécifiques

Solutions Adoptées
------------------

.. code-block:: text

   Règles d'annotation établies :
   
   1. Priorité au contenu principal (content > sidebar)
   2. Segmentation propre sans chevauchement
   3. Annotation de la zone englobante complète
   4. Cohérence inter-annotateur via validation croisée

Format d'Annotation COCO
=========================

Toutes les annotations suivent le standard **COCO** (Common Objects in Context) :

.. code-block:: json

   {
     "info": {
       "description": "SmartWebScraper-CV Dataset",
       "version": "4.0",
       "year": 2025
     },
     "categories": [
       {"id": 1, "name": "header", "supercategory": "web_element"},
       {"id": 2, "name": "title", "supercategory": "content"},
       {"id": 3, "name": "content", "supercategory": "content"},
       {"id": 18, "name": "suggestions", "supercategory": "recommendation"}
     ],
     "annotations": [
       {
         "id": 1,
         "image_id": 1,
         "category_id": 2,
         "bbox": [x, y, width, height],
         "area": 15680,
         "iscrowd": 0
       }
     ]
   }

Avantages du Format COCO
-------------------------

.. grid:: 3

   .. grid-item-card:: 🔧 Compatibilité
      :text-align: center
      
      Compatible Detectron2, YOLOv5, etc.

   .. grid-item-card:: 📊 Métriques Standard
      :text-align: center
      
      mAP, IoU, précision/rappel

   .. grid-item-card:: 🔄 Extensibilité
      :text-align: center
      
      Ajout facile de nouvelles classes

Processus d'Annotation
======================

Workflow Complet
----------------

.. mermaid::

   flowchart LR
       A[Images brutes] --> B[Sélection échantillon]
       B --> C[Annotation Roboflow]
       C --> D[Validation qualité]
       D --> E[Export COCO]
       E --> F[Préparation entraînement]
       F --> G{Résultats satisfaisants?}
       G -->|Non| H[Annotation supplémentaire]
       G -->|Oui| I[Modèle final]
       H --> C

Métriques de Qualité d'Annotation
==================================

.. list-table:: Indicateurs de Qualité
   :header-rows: 1
   :widths: 30 25 45

   * - **Métrique**
     - **Valeur Cible**
     - **Description**
   * - Cohérence inter-annotateur
     - > 85%
     - Accord entre différents annotateurs
   * - Précision des boîtes
     - IoU > 0.8
     - Alignement précis des bounding boxes
   * - Couverture des classes
     - Toutes représentées
     - Chaque classe a ≥ 10 exemples
   * - Équilibrage dataset
     - Ratio 3:1 max
     - Éviter les classes sur-représentées

.. tip::
   **Leçons apprises de l'annotation :**
   
   * Commencer par un jeu de classes simple et l'étendre progressivement
   * Définir des règles d'annotation claires dès le début
   * Valider régulièrement la cohérence des annotations
   * Équilibrer précision et efficacité selon les contraintes du projet
