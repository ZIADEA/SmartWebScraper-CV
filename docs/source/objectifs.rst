Objectifs du Projet
===================

L'objectif principal de ce projet est de développer un système intelligent capable de **scraper visuellement** 
une page web, c'est-à-dire d'extraire et analyser son contenu de manière automatisée à partir d'une capture d'image.

Objectifs Techniques Détaillés
===============================

1. Capture Intelligente
-----------------------

.. code-block:: none

   ✓ Capturer l'image complète d'un site web
   ✓ Gérer le contenu dynamique et le scrolling
   ✓ Optimiser la qualité de capture pour l'analyse

**Technologies utilisées :** Selenium, undetected-chromedriver, Playwright

2. Détection Automatique des Zones
-----------------------------------

.. code-block:: none

   ✓ Détecter automatiquement les zones d'intérêt
   ✓ Classifier les éléments (titre, contenu, publicité, footer, etc.)
   ✓ Fournir des annotations précises avec coordonnées

**Technologies utilisées :** Detectron2, Faster R-CNN, annotations COCO

.. image:: ../_static/detection_example.png
   :width: 500px
   :align: center
   :alt: Exemple de détection automatique

3. Extraction et Traitement du Texte
-------------------------------------

.. code-block:: none

   ✓ Extraire le texte des zones conservées via OCR
   ✓ Nettoyer et structurer le contenu extrait
   ✓ Appliquer des traitements NLP avancés

**Technologies utilisées :** PaddleOCR, NLTK, spaCy, TF-IDF

4. Interaction Intelligente
----------------------------

.. code-block:: none

   ✓ Permettre l'interrogation du contenu extrait
   ✓ Générer des résumés automatiques
   ✓ Répondre à des questions spécifiques
   ✓ Extraire des entités nommées

**Technologies utilisées :** Gemini API, Mistral (Ollama), Word2Vec

Objectifs Fonctionnels
======================

Application Complète avec Deux Profils
---------------------------------------

Profil Utilisateur Final
~~~~~~~~~~~~~~~~~~~~~~~~~

.. grid:: 2

   .. grid-item-card:: 📱 Interface Intuitive
      
      * Soumission simple d'URL
      * Visualisation des zones détectées
      * Sélection interactive des éléments

   .. grid-item-card:: 🔍 Analyse Interactive
      
      * Questions sur le contenu
      * Résumés automatiques
      * Extraction d'informations ciblées

Profil Administrateur
~~~~~~~~~~~~~~~~~~~~~

.. grid:: 2

   .. grid-item-card:: ⚙️ Supervision du Système
      
      * Validation des annotations
      * Correction des prédictions
      * Gestion de la qualité

   .. grid-item-card:: 🎯 Amélioration Continue
      
      * Préparation des données de fine-tuning
      * Évaluation des performances
      * Évolution du modèle

Workflow Complet
================

.. mermaid::

   flowchart TD
       A[URL soumise] --> B[Capture d'écran]
       B --> C[Détection automatique]
       C --> D{Validation utilisateur}
       D -->|OK| E[Extraction OCR]
       D -->|KO| F[Annotation manuelle]
       F --> E
       E --> G[Traitement NLP]
       G --> H[Interaction utilisateur]
       H --> I[Feedback et amélioration]
       I --> J[Fine-tuning du modèle]

Objectifs d'Innovation
======================

Contribution Scientifique
--------------------------

* **Dataset unique** : Constitution d'un dataset COCO de pages web annotées
* **Pipeline intégré** : Combinaison CV + OCR + NLP dans une même application
* **Apprentissage continu** : Système auto-amélioré par feedback utilisateur

Valeur Ajoutée Technique
------------------------

* **Robustesse** : Fonctionne même sur les sites les plus protégés
* **Précision** : Détection contextuelle des zones importantes
* **Extensibilité** : Architecture modulaire permettant l'ajout de nouvelles fonctionnalités

Métriques de Succès
===================

.. list-table:: Indicateurs de Performance
   :header-rows: 1
   :widths: 30 35 35

   * - **Métrique**
     - **Objectif Visé**
     - **Résultat Atteint**
   * - Précision détection (mAP)
     - > 40%
     - 41.6%
   * - Qualité OCR
     - > 85% sur texte net
     - > 90%
   * - Temps de traitement
     - < 10 secondes
     - 4-6 secondes
   * - Satisfaction utilisateur
     - > 4/5
     - 4.6/5

.. tip::
   L'application permet aujourd'hui de détecter automatiquement les blocs fonctionnels 
   dans une page, de nettoyer, résumer et analyser le contenu OCR, de poser des questions 
   ou lancer des requêtes spécifiques, et de constituer un dataset de fine-tuning progressif 
   basé sur les retours utilisateurs.
