Architecture du projet
=======================

Voici une vue d’ensemble de l’architecture du projet.

Structure du dépôt
------------------

.. code-block:: text

    SmartWebScraper-CV/
    ├── notebooks/               # Tests et démonstrations
    ├── script/                  # Scripts de traitement
    ├── modelExternUtiliser/    # Modèles pré-entraînés
    ├── data/                    # Données locales
    ├── docs/                    # Documentation
    └── app/                     # Application principale (Flask ou Streamlit)

Technologies utilisées
----------------------

- Python, Flask / Streamlit
- Detectron2 pour la détection d’objet
- PaddleOCR pour l’extraction de texte
- Playwright / Selenium pour la capture web
- Google Drive API pour le stockage cloud
