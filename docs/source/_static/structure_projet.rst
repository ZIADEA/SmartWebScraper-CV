Structure Complète du Projet
============================

Voici la structure complète des fichiers et dossiers générés automatiquement par l'application :

.. code-block:: text

   SmartWebScraper-CV/
   ├── 📁 LocalApp/
   │   └── SMARTWEBSCRAPPER-CV/           # Application Flask principale
   │       ├── 📁 app/                    # Code source principal
   │       │   ├── 📁 routes/             # Routes Flask (logique métier)
   │       │   ├── 📁 utils/              # Utilitaires (OCR, NLP, etc.)
   │       │   ├── 📁 models/             # Modèles entraînés
   │       │   ├── 📁 templates/          # Templates HTML
   │       │   ├── 📁 static/             # CSS, JS, images
   │       │   └── 📁 data/               # 🔄 Données générées automatiquement
   │       │       ├── 📁 originals/            # Captures d'écran brutes
   │       │       ├── 📁 model/                # Référentiel modèle + classes
   │       │       ├── 📁 annotated/            # Annotations automatiques
   │       │       ├── 📁 suppression/          # Images après suppression zones
   │       │       ├── 📁 predictions_scaled/   # JSON coordonnées mises à l'échelle
   │       │       ├── 📁 human_data/           # 👤 Annotations utilisateur
   │       │       │   ├── 📁 manual/           # Annotations manuelles brutes
   │       │       │   └── 📁 model/            # Annotations validées
   │       │       ├── 📁 annotated_by_human/   # Visualisations annotations utilisateur
   │       │       ├── 📁 suppression_human/    # Suppressions par utilisateur
   │       │       ├── 📁 fine_tune_data/       # 🎯 Données ré-entraînement
   │       │       └── 📁 fine_tune_backup/     # Archivage historique entraînement
   │       ├── 📄 run.py                  # Point d'entrée application
   │       ├── 📄 requirements.txt        # Dépendances Python
   │       ├── 📄 .env                    # Variables d'environnement
   │       ├── 📄 admin_config.json       # Configuration administrateur
   │       ├── 📄 visited_link.json       # Journal URLs visitées
   │       └── 📄 WORKFLOW.md             # Guide workflow détaillé
   │
   ├── 📁 docs/                           # 📖 Documentation ReadTheDocs
   │   ├── 📁 source/                     # Sources documentation
   │   │   ├── 📁 introduction/           # Introduction & contexte
   │   │   ├── 📁 data/                   # Acquisition données
   │   │   ├── 📁 annotation/             # Stratégies annotation
   │   │   ├── 📁 modeling/               # Modélisation CV
   │   │   ├── 📁 nlp/                    # Traitement NLP
   │   │   ├── 📁 architecture/           # Architecture app
   │   │   ├── 📁 results/                # Résultats & évaluation
   │   │   ├── 📁 usage/                  # Guides utilisation
   │   │   ├── 📁 problems/               # Résolution problèmes
   │   │   ├── 📁 api/                    # Documentation API
   │   │   ├── 📁 installation/           # Guides installation
   │   │   ├── 📁 deployment/             # Options déploiement
   │   │   ├── 📁 _static/                # Ressources statiques
   │   │   ├── 📄 index.rst               # Page d'accueil
   │   │   └── 📄 conf.py                 # Configuration Sphinx
   │   ├── 📁 build/                      # 🔄 Documentation générée
   │   └── 📄 requirements.txt            # Dépendances documentation
   │
   ├── 📄 .readthedocs.yaml               # Configuration ReadTheDocs
   ├── 📄 README.md                       # Documentation principale
   ├── 📄 setup.py                        # Script installation automatique
   ├── 📄 Makefile                        # Automatisation tâches
   ├── 📄 environment.yml                 # Configuration Conda
   └── 📄 LICENSE                         # Licence MIT

Détail des Dossiers de Données
===============================

.. list-table:: Description des Dossiers de Données
   :header-rows: 1
   :widths: 25 75

   * - **Dossier**
     - **Contenu et Utilisation**
   * - ``originals/``
     - Images capturées directement depuis les sites web (format PNG haute résolution)
   * - ``model/``
     - Images de référence + fichiers JSON avec toutes les classes détectables par le modèle
   * - ``annotated/``
     - Images avec annotations automatiques visualisées (boîtes colorées + labels)
   * - ``suppression/``
     - Images modifiées après suppression des zones sélectionnées par l'utilisateur
   * - ``predictions_scaled/``
     - Fichiers JSON contenant les coordonnées précises des boîtes prédites, mises à l'échelle
   * - ``human_data/manual/``
     - Annotations manuelles brutes : 1 image + 2 JSON (brut & filtré) par annotation utilisateur
   * - ``human_data/model/``
     - Annotations validées par l'utilisateur, prêtes pour la validation admin
   * - ``annotated_by_human/``
     - Visualisations finales des annotations créées manuellement par l'utilisateur
   * - ``suppression_human/``
     - Images éditées selon les choix de zones de l'utilisateur (workflow manuel)
   * - ``fine_tune_data/``
     - Dataset constitué pour le ré-entraînement : images + annotations JSON validées
   * - ``fine_tune_backup/``
     - Copie complète de sauvegarde du dataset de fine-tuning (historique)

Flux de Données
================

.. mermaid::

   flowchart TD
       A[URL Soumise] --> B[originals/]
       B --> C[Modèle Detectron2]
       C --> D[annotated/]
       C --> E[predictions_scaled/]
       
       D --> F{Utilisateur Valide?}
       F -->|Oui| G[Sélection Zones]
       F -->|Non| H[human_data/manual/]
       
       H --> I[Annotation Manuelle]
       I --> J[annotated_by_human/]
       J --> K[human_data/model/]
       
       G --> L[suppression/]
       K --> M{Admin Valide?}
       M -->|Oui| N[fine_tune_data/]
       M -->|Non| O[Correction Requise]
       
       N --> P[Fine-tuning Modèle]
       P --> Q[fine_tune_backup/]

Fichiers de Configuration
=========================

**.env (Variables d'Environnement)**

.. code-block:: bash

   # Configuration Flask
   FLASK_ENV=development
   FLASK_DEBUG=True
   SECRET_KEY=your-secret-key
   
   # APIs
   GEMINI_API_KEY=your-gemini-key
   SERPAPI_KEY=your-serpapi-key
   
   # GPU/CPU
   CUDA_VISIBLE_DEVICES=0
   FORCE_CPU_MODE=False
   
   # Modèles
   DETECTRON2_MODEL_PATH=app/models/detectron2/model_final.pth
   OLLAMA_BASE_URL=http://localhost:11434

**admin_config.json (Configuration Admin)**

.. code-block:: json

   {
     "admin_email": "admin@example.com",
     "admin_password": "secure_password",
     "validation_threshold": 0.8,
     "auto_backup": true,
     "fine_tune_min_samples": 50
   }

**visited_link.json (Journal des URLs)**

.. code-block:: json

   {
     "visited_urls": [
       {
         "url": "https://example.com",
         "timestamp": "2025-06-16T10:30:00Z",
         "status": "success",
         "capture_id": "capture_001"
       }
     ],
     "statistics": {
       "total_captures": 15,
       "success_rate": 0.93,
       "last_capture": "2025-06-16T15:45:00Z"
     }
   }

Gestion de l'Espace Disque
===========================

.. warning::
   **Surveillance de l'espace disque recommandée :**
   
   * Images haute résolution : 2-10 MB par capture
   * Annotations JSON : 10-50 KB par fichier
   * Croissance estimée : ~100 MB par 50 captures
   * Nettoyage périodique des dossiers temporaires conseillé

**Script de Nettoyage Automatique**

.. code-block:: python

   # Exemple de script maintenance
   import os
   from datetime import datetime, timedelta
   
   def cleanup_old_data(days=30):
       """Supprime les données de plus de X jours"""
       cutoff = datetime.now() - timedelta(days=days)
       
       cleanup_folders = [
           'data/originals/',
           'data/suppression/',
           'data/annotated/'
       ]
       
       for folder in cleanup_folders:
           for file in os.listdir(folder):
               file_path = os.path.join(folder, file)
               if os.path.getctime(file_path) < cutoff.timestamp():
                   os.remove(file_path)

Sauvegarde et Archivage
=======================

**Données Critiques à Sauvegarder**

.. list-table:: Priorités de Sauvegarde
   :header-rows: 1
   :widths: 30 20 50

   * - **Dossier**
     - **Priorité**
     - **Raison**
   * - ``fine_tune_data/``
     - **🔴 Critique**
     - Dataset validé pour entraînement
   * - ``human_data/model/``
     - **🔴 Critique**
     - Annotations humaines validées
   * - ``app/models/``
     - **🟡 Important**
     - Modèles entraînés personnalisés
   * - ``admin_config.json``
     - **🟡 Important**
     - Configuration système
   * - ``visited_link.json``
     - **🟢 Utile**
     - Historique et statistiques

**Commande de Sauvegarde Suggérée**

.. code-block:: bash

   # Sauvegarde automatisée
   tar -czf backup_$(date +%Y%m%d).tar.gz \
       data/fine_tune_data/ \
       data/human_data/model/ \
       app/models/ \
       admin_config.json \
       visited_link.json

.. tip::
   **Bonnes pratiques de gestion :**
   
   * Sauvegarde hebdomadaire des données critiques
   * Rotation des backups (garder 4 semaines)
   * Surveillance espace disque avec alertes
   * Documentation des modifications importantes
   * Tests périodiques de restauration
