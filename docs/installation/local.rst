Installation et Lancement de l'Application Locale
==============================================

Cette section détaille l'installation complète de l'application Flask locale SmartWebScraper-CV.

.. note::
   L'application locale vous permet de tester et utiliser SmartWebScraper-CV directement 
   sur votre machine, avec toutes les fonctionnalités de capture, annotation et analyse.

Prérequis Système
=================

Configuration Minimale
-----------------------

.. list-table:: Spécifications Requises
   :header-rows: 1
   :widths: 30 70

   * - **Composant**
     - **Exigence**
   * - **Python**
     - Version 3.9 ou supérieure
   * - **RAM**
     - 8 GB minimum (16 GB recommandé)
   * - **Stockage**
     - 10 GB d'espace libre minimum
   * - **Système d'exploitation**
     - Windows 10+, macOS 11+, Linux Ubuntu 18.04+
   * - **Navigateur**
     - Chrome/Chromium installé

Outils Supplémentaires
-----------------------

* **Terminal** : Command Prompt (Windows), Terminal (macOS/Linux)
* **Git** (optionnel) : Pour cloner le dépôt
* **Conda** (optionnel) : Pour la gestion d'environnements

Installation Étape par Étape
=============================

Étape 1 : Récupération du Projet
---------------------------------

Deux méthodes sont disponibles pour télécharger le projet :

**Méthode A : Via Git (Recommandée)**

.. code-block:: bash

   # Vérification de Git
   git --version
   
   # Si Git n'est pas installé, téléchargez depuis : https://git-scm.com/downloads
   
   # Clonage du projet
   git clone https://github.com/ZIADEA/SmartWebScraper-CV.git

**Méthode B : Téléchargement ZIP**

1. Aller sur le `dépôt GitHub du projet <https://github.com/ZIADEA/SmartWebScraper-CV>`_
2. Cliquer sur **"Code"** → **"Download ZIP"**
3. Extraire l'archive dans le dossier de votre choix

Étape 2 : Navigation vers l'Application
----------------------------------------

.. code-block:: bash

   # Accès au dossier de l'application locale
   cd SmartWebScraper-CV/LocalApp/SMARTWEBSCRAPPER-CV

.. important::
   Assurez-vous de vous placer dans ce dossier spécifique avant de continuer 
   avec l'installation des dépendances.

Étape 3 : Environnement Virtuel (Optionnel mais Recommandé)
------------------------------------------------------------

**Option A : Avec venv (Standard Python)**

.. code-block:: bash

   # Création de l'environnement virtuel
   python -m venv venv
   
   # Activation de l'environnement
   # Windows :
   venv\Scripts\activate
   
   # macOS/Linux :
   source venv/bin/activate

**Option B : Avec Conda**

.. code-block:: bash

   # Création de l'environnement
   conda create -n smartwebscraper python=3.10
   
   # Activation
   conda activate smartwebscraper

**Option C : À partir du fichier environment.yml**

.. code-block:: bash

   # Création automatique depuis le fichier de configuration
   conda env create -f environment.yml
   conda activate mon_env

Étape 4 : Installation des Dépendances
---------------------------------------

.. code-block:: bash

   # Installation des packages Python requis
   pip install -r requirements.txt

.. tip::
   L'installation peut prendre plusieurs minutes selon votre connexion Internet 
   et la puissance de votre machine.

Étape 5 : Installation de Detectron2
-------------------------------------

L'installation de Detectron2 varie selon votre système d'exploitation et configuration GPU :

**Windows (CPU seulement)**

Suivez le guide détaillé : 
`Detectron Installation Guide for CPU only on Windows <https://github.com/ZIADEA/SmartWebScraper-CV/blob/main/LocalApp/DetectronInstallationGuideForOnlyCPUonWindow.md>`_

**Windows (avec GPU)**

Suivez ce tutoriel Medium :
`How to install Detectron2 on Windows 10 or 11 <https://medium.com/@yogeshkumarpilli/how-to-install-detectron2-on-windows-10-or-11-2021-aug-with-the-latest-build-v0-5-c7333909676f>`_

**Linux (CPU et GPU)**

Suivez la documentation officielle :
`Detectron2 Installation Guide <https://detectron2.readthedocs.io/en/latest/tutorials/install.html>`_

**Installation Générique**

.. code-block:: bash

   # Installation depuis GitHub (recommandée)
   pip install 'git+https://github.com/facebookresearch/detectron2.git'
   
   # Ou installation via conda (si disponible)
   conda install detectron2 -c detectron2

Configuration de l'Application
===============================

Configuration Administrateur
-----------------------------

**Méthode 1 : Variables d'environnement**

.. code-block:: bash

   # macOS/Linux
   export ADMIN_EMAIL="admin@example.com"
   export ADMIN_PASSWORD="your_password"
   
   # Windows
   set ADMIN_EMAIL="admin@example.com"
   set ADMIN_PASSWORD="your_password"

**Méthode 2 : Fichier de configuration**

Modifiez le fichier ``admin_config.json`` :

.. code-block:: json

   {
     "admin_email": "admin@example.com",
     "admin_password": "your_secure_password",
     "admin_privileges": ["validate", "manage", "fine_tune"]
   }

Configuration des APIs
-----------------------

**Étape Obligatoire : Clé API Gemini**

1. Créez un fichier ``.env`` dans le répertoire racine :

.. code-block:: bash

   # Fichier .env
   GEMINI_API_KEY=your_gemini_api_key_here
   ADMIN_EMAIL=admin@example.com
   ADMIN_PASSWORD=your_password
   FLASK_ENV=development

2. Obtenez votre clé API Gemini en suivant ce guide :
   `How to obtain a Gemini API key <https://dev.to/explinks/how-to-obtain-a-gemini-api-key-step-by-step-guide-4m97>`_

**Modèle Local Mistral (Optionnel)**

1. Téléchargez et installez **Ollama** : https://ollama.com/
2. Lancez le modèle Mistral :

.. code-block:: bash

   # Installation du modèle
   ollama pull mistral
   
   # Lancement en arrière-plan
   ollama run mistral

.. note::
   Laissez Ollama tourner en arrière-plan pendant l'utilisation de l'application 
   pour bénéficier des fonctionnalités LLM locales.

Lancement de l'Application
===========================

Démarrage du Serveur
---------------------

.. code-block:: bash

   # Démarrage de l'application Flask
   python run.py

Vous devriez voir une sortie similaire à :

.. code-block:: text

   * Serving Flask app 'app'
   * Debug mode: on
   * Running on http://127.0.0.1:5000
   * Press CTRL+C to quit

Accès aux Interfaces
--------------------

.. list-table:: Interfaces Disponibles
   :header-rows: 1
   :widths: 30 40 30

   * - **Interface**
     - **URL**
     - **Description**
   * - **Utilisateur Principal**
     - http://localhost:5000
     - Capture et analyse de pages
   * - **Interface Admin**
     - http://localhost:5000/admin/login
     - Gestion et validation
   * - **API Documentation**
     - http://localhost:5000/api/docs
     - Documentation API REST

Arrêt de l'Application
----------------------

.. code-block:: bash

   # Dans le terminal où l'application tourne
   Ctrl + C

Structure des Données Générées
===============================

L'application crée automatiquement une structure de dossiers organisée :

.. code-block:: text

   app/
   ├── data/
   │   ├── originals/            # Captures d'écran brutes
   │   ├── model/                # Référentiel du modèle
   │   ├── annotated/            # Annotations automatiques
   │   ├── suppression/          # Images après suppression de zones
   │   ├── predictions_scaled/   # Coordonnées JSON mises à l'échelle
   │   ├── human_data/           # Annotations utilisateur
   │   │   ├── manual/           # Annotations manuelles brutes
   │   │   └── model/            # Annotations validées
   │   ├── annotated_by_human/   # Visualisations annotations utilisateur
   │   ├── suppression_human/    # Suppressions utilisateur
   │   ├── fine_tune_data/       # Données pour ré-entraînement
   │   └── fine_tune_backup/     # Archivage historique
   └── visited_link.json         # Journal des URLs visitées

Workflow d'Utilisation
=======================

Pour comprendre le fonctionnement global et l'enchaînement des interfaces, 
consultez le fichier ``WORKFLOW.md`` du projet.

.. mermaid::

   flowchart TD
       A[Accès Application] --> B[Soumission URL]
       B --> C[Capture Automatique]
       C --> D[Détection Zones]
       D --> E{Validation Utilisateur}
       E -->|OK| F[Extraction OCR]
       E -->|Correction| G[Annotation Manuelle]
       G --> F
       F --> H[Analyse NLP]
       H --> I[Interaction Utilisateur]
       I --> J[Feedback Admin]
       J --> K[Fine-tuning Modèle]

Résolution de Problèmes
========================

Problèmes Courants d'Installation
----------------------------------

.. list-table:: Solutions aux Erreurs Fréquentes
   :header-rows: 1
   :widths: 40 60

   * - **Erreur**
     - **Solution**
   * - ``Python not found``
     - Vérifier installation Python 3.9+ et PATH
   * - ``pip not recognized``
     - Réinstaller Python avec option "Add to PATH"
   * - ``git not found``
     - Installer Git depuis https://git-scm.com/
   * - ``requirements.txt not found``
     - Vérifier que vous êtes dans le bon dossier
   * - ``Detectron2 installation failed``
     - Suivre guides spécifiques OS ci-dessus

Problèmes de Lancement
-----------------------

.. code-block:: bash

   # Port déjà utilisé
   # Solution : changer le port dans run.py
   app.run(host='0.0.0.0', port=5001, debug=True)
   
   # Erreurs de permissions
   # Solution : lancer en administrateur ou ajuster permissions

.. code-block:: bash

   # Debug détaillé
   export FLASK_DEBUG=1
   python run.py

Support et Assistance
=====================

Si vous rencontrez des difficultés, plusieurs options s'offrent à vous :

Assistance Installation
-----------------------

.. note::
   **Contact pour problèmes d'installation :**
   
   * **Email** : djeryala@gmail.com
   * **Objet** : "Scrapp LocalApp Problem installation"
   * **Inclure** : OS, version Python, logs d'erreur

Problèmes de Composants
-----------------------

.. note::
   **Contact pour problèmes spécifiques :**
   
   * **Email** : djeryala@gmail.com  
   * **Objet** : "Scrapp LocalApp Problem composant"
   * **Inclure** : Description détaillée, étapes de reproduction

.. tip::
   **Bonnes pratiques pour signaler un problème :**
   
   * Inclure les logs d'erreur complets
   * Préciser votre système d'exploitation
   * Mentionner les étapes suivies avant l'erreur
   * Joindre une capture d'écran si pertinent
