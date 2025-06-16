Constitution et Acquisition des Données
========================================

La constitution d'un dataset de qualité est fondamentale pour le succès d'un projet de Computer Vision. 
Cette section détaille notre approche pour collecter et préparer les données d'entraînement.

Stratégie d'Acquisition
=======================

Notre stratégie s'articule autour de trois axes principaux :

1. **Collecte automatisée** via des outils de scraping web
2. **Diversification** des sources et types de contenu  
3. **Validation manuelle** pour garantir la qualité

.. mermaid::

   flowchart LR
       A[SerpAPI] --> B[Liste d'URLs]
       B --> C[Selenium + Chrome]
       C --> D[Captures d'écran]
       D --> E[~3000 images brutes]
       E --> F[Nettoyage manuel]
       F --> G[~2663 images finales]

Début de Constitution du Dataset
===============================

Capture via Selenium + undetected-chromedriver
-----------------------------------------------

La capture est effectuée avec un navigateur piloté par Selenium, combiné à ``undetected-chromedriver`` 
pour éviter les blocages par Google ou les systèmes anti-automatisation.

.. code-block:: python

   from selenium import webdriver
   from undetected_chromedriver import Chrome
   
   # Configuration du navigateur
   options = webdriver.ChromeOptions()
   options.add_argument('--headless')
   options.add_argument('--window-size=1280,800')
   
   driver = Chrome(options=options)

Process de Collecte d'URLs
---------------------------

**Étape 1 : Génération d'URLs via SerpAPI**

.. code-block:: python

   # Requêtes utilisées pour la collecte
   queries = [
       "actualités france",
       "articles de blog",
       "sites d'information", 
       "pages produits e-commerce",
       "documentation technique",
       "forums de discussion"
   ]

.. note::
   SerpAPI génère des liens de pages existant sur internet à partir de nos requêtes. 
   Pour chaque requête, maximum 100 liens sont collectés et une sauvegarde des liens 
   est effectuée. Le code a été relancé 5 fois pour diversifier les sources.

**Étape 2 : Configuration de la Capture**

.. list-table:: Paramètres de Capture
   :header-rows: 1
   :widths: 30 70

   * - **Paramètre**
     - **Valeur**
   * - Largeur fenêtre
     - 1280 pixels
   * - Hauteur minimum
     - 800 pixels  
   * - Hauteur maximum
     - 10000 pixels
   * - Nombre de scrolls max
     - 30
   * - Temps de pause
     - 1 seconde

**Étape 3 : Capture avec Scroll Progressif**

.. code-block:: python

   def capture_with_scroll(driver, url):
       driver.get(url)
       
       # Scroll progressif et fluide
       total_height = driver.execute_script("return document.body.scrollHeight")
       current_position = 0
       scroll_step = total_height // 30  # Max 30 scrolls
       
       while current_position < total_height:
           driver.execute_script(f"window.scrollTo(0, {current_position});")
           time.sleep(1)  # Pause pour le chargement
           current_position += scroll_step
       
       # Capture d'écran complète
       return driver.get_screenshot_as_png()

**Étape 4 : Sauvegarde et Métadonnées**

Chaque capture est sauvegardée avec :

* L'image au format PNG
* L'URL correspondante
* La timestamp de capture
* Les dimensions de la page
* Le statut de chargement

.. code-block:: json

   {
       "filename": "capture_001.png",
       "url": "https://example.com/article",
       "timestamp": "2025-06-16T10:30:00Z",
       "dimensions": {"width": 1280, "height": 3500},
       "status": "success"
   }

Résultats de la Collecte
========================

**Volume de Données Collectées**

.. grid:: 3

   .. grid-item-card:: 📊 Images Brutes
      :text-align: center
      
      ~3000 captures initiales

   .. grid-item-card:: 🧹 Après Nettoyage
      :text-align: center
      
      2663 images conservées

   .. grid-item-card:: 🎯 Priorisées
      :text-align: center
      
      Articles et vidéos YouTube

Distribution des Tailles d'Images
----------------------------------

.. image:: ../_static/taille_distribution.png
   :width: 600px
   :align: center
   :alt: Distribution des tailles d'images collectées

.. warning::
   **Défis identifiés lors de la collecte :**
   
   * Certaines captures ont de très grandes tailles (> 5000px de hauteur)
   * Les captures très longues posaient des problèmes de RAM à l'ouverture
   * Aucun redimensionnement appliqué par choix (préservation de la résolution)

Types de Contenu Priorisés
===========================

1. **Articles de Presse et Blogs**
   
   * Structure claire avec titre, contenu, sidebar
   * Présence fréquente de publicités
   * Bon équilibre des classes d'annotation

2. **Pages de Visualisation YouTube**
   
   * Interface standardisée
   * Éléments spécifiques : likes, vues, commentaires, recommandations
   * Excellent pour tester la précision du modèle

3. **Sites E-commerce**
   
   * Mise en page complexe
   * Nombreux éléments visuels (images produits, prix, avis)
   * Cas d'usage réaliste pour l'application

Méthode de Nettoyage
====================

Le nettoyage manuel s'est concentré sur :

.. code-block:: none

   ✗ Suppression des erreurs de domaine (pages d'erreur 404, 500)
   ✗ Élimination des captures vides ou corrompues  
   ✗ Retrait des contenus non-pertinents (captchas, redirections)
   ✓ Conservation des pages avec structure web classique
   ✓ Priorisation du contenu textuel riche

**Critères de Conservation :**

* Présence de contenu textuel significatif
* Structure web reconnaissable (header, content, footer)
* Qualité de capture acceptable (pas de flou majeur)
* Diversité des mises en page
* Absence d'éléments perturbateurs (pop-ups bloquants, erreurs)

Traçabilité et Métadonnées
===========================

Un système complet de traçabilité a été mis en place :

.. code-block:: python

   metadata_structure = {
       "collection_info": {
           "date_start": "2025-01-15",
           "date_end": "2025-02-28", 
           "total_queries": 30,
           "urls_collected": 3000,
           "images_captured": 2980,
           "images_kept": 2663
       },
       "quality_metrics": {
           "success_rate": 0.89,
           "avg_loading_time": 3.2,
           "error_types": ["timeout", "404", "captcha", "blocked"]
       }
   }

Défis Techniques Rencontrés
============================

Gestion des Sites Modernes
---------------------------

.. list-table:: Problèmes et Solutions
   :header-rows: 1
   :widths: 40 60

   * - **Problème**
     - **Solution Adoptée**
   * - Contenu chargé en JavaScript
     - Attente supplémentaire après scroll
   * - Protection anti-bot
     - undetected-chromedriver + rotation User-Agent
   * - Infinite scroll
     - Limitation à 30 scrolls maximum
   * - Pop-ups cookies/RGPD
     - Script de fermeture automatique
   * - Redirections
     - Suivi et validation de l'URL finale

Performance et Optimisation
----------------------------

**Gestion de la Mémoire :**

.. code-block:: python

   # Optimisations appliquées
   def optimize_memory():
       # Nettoyage cache navigateur
       driver.delete_all_cookies()
       driver.execute_script("window.localStorage.clear();")
       
       # Limitation taille images
       max_height = 10000
       if image_height > max_height:
           # Scroll partiel uniquement
           pass

**Parallélisation :**

* Utilisation de plusieurs instances Chrome
* Traitement par lots de 50 URLs
* Gestion des timeouts et reprises automatiques

Validation de la Qualité
=========================

Métriques de Qualité Automatiques
----------------------------------

.. code-block:: python

   def validate_capture_quality(image_path):
       image = cv2.imread(image_path)
       
       # Vérifications automatiques
       checks = {
           "min_height": image.shape[0] > 600,
           "min_width": image.shape[1] > 800, 
           "not_blank": cv2.countNonZero(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)) > 1000,
           "has_content": detect_text_presence(image),
           "valid_format": image is not None
       }
       
       return all(checks.values())

Contrôle Qualité Manuel
-----------------------

Un échantillonnage de 10% des images a été vérifié manuellement pour :

* Cohérence de la structure de page
* Lisibilité du contenu textuel
* Présence des éléments web standard
* Absence d'artefacts de capture

.. tip::
   **Bonnes Pratiques Identifiées :**
   
   * Prioriser la diversité sur la quantité
   * Maintenir une traçabilité complète
   * Valider la qualité à chaque étape
   * Préserver la résolution originale pour l'annotation

Préparation pour l'Annotation
==============================

Les images validées sont organisées selon la structure suivante :

.. code-block:: text

   dataset_raw/
   ├── images/
   │   ├── capture_001.png
   │   ├── capture_002.png
   │   └── ...
   ├── metadata/
   │   ├── urls.json
   │   ├── capture_info.json
   │   └── quality_report.json
   └── logs/
       ├── collection.log
       └── errors.log

Cette organisation facilite l'étape suivante d'annotation manuelle via Roboflow et assure une transition fluide vers la phase de modélisation.
