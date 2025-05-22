Architecture du projet
=======================

Voici une vue d’ensemble de l’architecture du projet.

Structure du dépôt
------------------

.. code-block:: text

    SmartWebScraper-CV/
    ├── README.md                # Présentation du projet
    ├── requirement.txt          # Dépendances du projet
    ├── notebooks/               # Tests et démonstrations
    ├── script/                  # Scripts de traitement
    ├── modelExternUtiliser/    # Modèles pré-entraînés
    ├──fintunningmodel/       # Modèles fine-tunés
    ├── data/                    # Données utiliser pour l entrainement du model computer vision
    ├── docs/                    # Documentation
    └── app/                     # Application principale (Flask )

Technologies utilisées
----------------------

- Python langage de programmation principal
- Flask pour le développement de l’application web
- SerAPI pour Récupérer automatiquement les URLs des résultats Google pour une requête, sans navigateur.
- Selenium / Playwright pour l’automatisation de la navigation web et la capture d images de sites web
- Undetected Chrome Driver pour contourner les protections anti-bot lors de la navigation pour la collect d images 
- OpenCV pour le traitement d’image , l annotation et la visualisation
- PyTorch pour le fine-tuning du modèle de vision par ordinateur
- Detectron2 pour la détection d’objet
- PaddleOCR pour l’extraction de texte
- Playwright / Selenium pour la capture web
- (la partie NLP est en cours de développement)
- (la partie de l’interface utilisateur est en cours de développement)

