Installation et Lancement de l'Application Locale
==============================================

.. raw:: html

   <div align="center">
     <img src="https://media.giphy.com/media/SWoSkN6DxTszqIKEqv/giphy.gif" alt="SmartWebScraper demonstration" width="500"/>
   </div>

Ce dossier contient l'interface web Flask pour **SmartWebScraper-CV**.  
L'application permet de capturer des pages web, d'annoter automatiquement ou manuellement les éléments détectés, et de gérer les données nécessaires à l'entraînement de modèles de détection.

Prérequis
=========

* **Python 3.9 ou supérieur** installé
* Un terminal (Command Prompt sur Windows, Terminal sur macOS/Linux)
* **Git** (optionnel) pour cloner le dépôt

Installation
============

Étape 1 : Téléchargement du projet
-----------------------------------

Il existe deux méthodes pour récupérer le projet SmartWebScraper-CV sur votre machine :

**a) Via Git (recommandé)**

Cette méthode vous permet de télécharger tout le projet et son historique Git (commits, branches, etc.). Elle est idéale si vous souhaitez contribuer ou maintenir une version synchronisée avec le projet d'origine.

Prérequis :

Avoir Git installé sur votre machine. Pour vérifier, tapez :

.. code-block:: bash

   git --version

Si Git n'est pas installé, téléchargez-le depuis : https://git-scm.com/downloads

Commande :

Dans un terminal (ou directement depuis VSCode) :

.. code-block:: bash

   git clone https://github.com/ZIADEA/SmartWebScraper-CV.git

Cela va créer un dossier SmartWebScraper-CV/ contenant tout le projet.

**b) Via le téléchargement ZIP (alternative)**

Si vous ne souhaitez pas utiliser Git, vous pouvez simplement :

1. Aller sur le dépôt GitHub du projet
2. Cliquer sur le bouton "Code", puis "Download ZIP"
3. Extraire l'archive ZIP dans le dossier de votre choix

Étape 2 : Accéder au dossier de l'application locale
-----------------------------------------------------

Une fois le projet cloné ou extrait, vous devez accéder à l'application Flask locale.

Dans votre terminal :

.. code-block:: bash

   cd SmartWebScraper-CV/LocalApp/SMARTWEBSCRAPPER-CV

Ce dossier contient l'application principale que vous pourrez exécuter localement.

.. note::
   Assurez-vous de vous placer dans ce dossier avant de continuer avec l'installation des dépendances ou le lancement du serveur Flask.

Étape 3 : (Optionnel) Créez un environnement virtuel
-----------------------------------------------------

**Avec venv (standard Python)**

Exécuter dans le terminal la commande suivante :

.. code-block:: bash

   python -m venv venv

et tu actives l'environnement avec :

* Windows : ``venv\Scripts\activate``
* macOS/Linux : ``source venv/bin/activate``

**Ou Avec Conda (si tu utilises Anaconda ou Miniconda)**

.. code-block:: bash

   conda create -n nom_env python=3.10

et tu actives l'environnement avec :

.. code-block:: bash

   conda activate nom_env

Étape 4 : Installez les dépendances
------------------------------------

.. code-block:: bash

   pip install -r requirements.txt

ou vous pouvez aussi créer un environnement local à partir du .yml du dépôt avec :

.. code-block:: bash

   conda env create -f environment.yml && conda activate mon_env

Étape 5 : Installez detectron2 (nécessaire uniquement la première fois)
------------------------------------------------------------------------

* Pour les utilisateurs de Windows veuillez suivre ce guide (compatible uniquement pour CPU only) : https://github.com/ZIADEA/SmartWebScraper-CV/blob/main/LocalApp/DetectronInstallationGuideForOnlyCPUonWindow.md

* Pour les utilisateurs de Windows veuillez suivre ce guide (compatible uniquement pour GPU) : https://medium.com/@yogeshkumarpilli/how-to-install-detectron2-on-windows-10-or-11-2021-aug-with-the-latest-build-v0-5-c7333909676f

* Pour les utilisateurs de linux veuillez suivre ce guide (compatible pour CPU et GPU) : https://detectron2.readthedocs.io/en/latest/tutorials/install.html

Étape 6 : Configurez le compte admin
-------------------------------------

Vous pouvez définir les variables d'environnement dans le fichier ``.env`` comme ce qui suit :

* macOS/Linux :

.. code-block:: bash

   export ADMIN_EMAIL="admin@example.com"
   export ADMIN_PASSWORD="your_password"

* Windows :

.. code-block:: cmd

   ADMIN_EMAIL="admin@example.com"
   ADMIN_PASSWORD="your_password"

et modifier le fichier ``admin_config.json``

Lancement de l'application
===========================

Étape 0 — Clé API Gemini (obligatoire)
---------------------------------------

Créez un fichier ``.env`` et ajoutez votre clé API Gemini.  
Suivez ce guide : `How to obtain a Gemini API key <https://dev.to/explinks/how-to-obtain-a-gemini-api-key-step-by-step-guide-4m97>`_

Étape 1 — Modèle local Mistral
-------------------------------

Téléchargez et installez **Ollama** : https://ollama.com/  
Puis lancez dans un terminal :

.. code-block:: bash

   ollama run mistral

et laissez le tourner en backend 

Étape 2 — Démarrer le serveur Flask
------------------------------------

.. code-block:: bash

   python run.py

Étape 3 — Accéder à l'application
----------------------------------

Ouvrez votre navigateur et allez sur : http://localhost:5000

Étape 4 — Arrêter l'application
--------------------------------

Dans le terminal où vous avez démarré le terminal, utilisez ``Ctrl + C`` pour interrompre l'exécution.

Dossiers générés
=================

L'application crée automatiquement un dossier ``data/`` contenant les sous-dossiers suivants :

.. code-block:: text

   app/
   ├── data/
   │   ├── originals/            # Captures d'écran brutes prises depuis le web
   │   ├── model/                # Images + toutes les classes prédictibles possibles (référentiel du modèle)
   │   ├── annotated/            # Captures annotées automatiquement (prédictions du modèle)
   │   ├── suppression/          # Images éditées après suppression des zones sélectionnées dans les prédictions
   │   ├── predictions_scaled/   # JSON contenant les coordonnées des boîtes prédictes mises à l'échelle
   │   ├── human_data/           # Annotations manuelles de l'utilisateur
   │   │   ├── manual/           # 1 image + 2 JSON (brut & filtré) par image, créés par l'utilisateur
   │   │   └── model/            # Images et JSON contenant les coordonnées des boîtes prédictes mises à l'échelle  qui ont été validées par l'utilisateur
   │   ├── annotated_by_human/   # Images annotées par l'utilisateur (visuel final des boîtes)
   │   ├── suppression_human/    # Images éditées après suppression des zones choisies par l'utilisateur
   │   ├── fine_tune_data/       # Données (images + JSON) sélectionnées pour le ré-entraînement
   │   └── fine_tune_backup/     # Copie intégrale de fine_tune_data pour archivage (historique de train)
   └── visited_link.json         # Journal des URLs déjà visitées pour éviter les doublons

Workflow
========

Pour comprendre le fonctionnement global de l'application et l'enchaînement des pages/interfaces, veuillez consulter le fichier ``WORKFLOW.md``.
