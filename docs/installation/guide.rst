Guide d'Installation
====================

Ce guide détaille l'installation complète de SmartWebScraper-CV, de la configuration 
de l'environnement au déploiement de l'application.

Prérequis Système
=================

Configuration Matérielle Recommandée
-------------------------------------

.. list-table:: Spécifications Matérielles
   :header-rows: 1
   :widths: 25 25 25 25

   * - **Composant**
     - **Minimum**
     - **Recommandé**
     - **Optimal**
   * - **RAM**
     - 8 GB
     - 16 GB
     - 32 GB
   * - **GPU**
     - CPU seulement
     - GTX 1060 6GB
     - RTX 3060+ 12GB
   * - **Stockage**
     - 50 GB libre
     - 100 GB SSD
     - 500 GB NVMe
   * - **CPU**
     - 4 cores
     - 8 cores
     - 12+ cores

Configuration Logicielle
-------------------------

.. code-block:: bash

   # Système d'exploitation supportés
   Ubuntu 20.04+ LTS
   Windows 10/11 (avec WSL2 recommandé)
   macOS 11+ (support limité GPU)
   
   # Python
   Python 3.8-3.10
   
   # CUDA (optionnel, pour GPU)
   CUDA 11.3+
   cuDNN 8.2+

Installation Complète
=====================

Étape 1 : Clonage du Projet
----------------------------

.. code-block:: bash

   # Clonage du repository
   git clone https://github.com/votre-repo/SmartWebScraper-CV.git
   cd SmartWebScraper-CV
   
   # Vérification de la structure
   ls -la
   # Doit contenir : app/, data/, docs/, requirements.txt, run.py

Étape 2 : Environnement Python
-------------------------------

**Option A : Conda (Recommandé)**

.. code-block:: bash

   # Création environnement
   conda create -n smartwebscraper python=3.9
   conda activate smartwebscraper
   
   # Installation des dépendances base
   conda install pytorch torchvision torchaudio cudatoolkit=11.3 -c pytorch
   
   # Detectron2 (avec CUDA)
   pip install 'git+https://github.com/facebookresearch/detectron2.git'

**Option B : venv**

.. code-block:: bash

   # Création environnement virtuel
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # ou
   venv\Scripts\activate     # Windows
   
   # Installation PyTorch (CPU seulement)
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

Étape 3 : Dépendances Application
----------------------------------

.. code-block:: bash

   # Installation des dépendances principales
   pip install -r requirements.txt

**Contenu requirements.txt :**

.. code-block:: text

   # Framework Web
   Flask==2.3.2
   Flask-CORS==4.0.0
   
   # Computer Vision
   detectron2
   opencv-python==4.8.0.74
   Pillow==9.5.0
   
   # OCR
   paddleocr==2.7.0.3
   
   # NLP
   nltk==3.8.1
   spacy==3.6.1
   scikit-learn==1.3.0
   gensim==4.3.1
   
   # Web Scraping
   selenium==4.11.2
   undetected-chromedriver==3.5.3
   playwright==1.37.0
   
   # Utilitaires
   numpy==1.24.3
   pandas==2.0.3
   requests==2.31.0
   python-dotenv==1.0.0
   
   # LLM
   google-generativeai==0.1.0
   ollama-python==0.1.7

Étape 4 : Modèles et Données
-----------------------------

**Téléchargement des Modèles NLP :**

.. code-block:: bash

   # Modèles NLTK
   python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('punkt_tab')"
   
   # Modèle spaCy français
   python -m spacy download fr_core_news_sm

**Configuration Detectron2 :**

.. code-block:: bash

   # Création du dossier modèles
   mkdir -p app/models/detectron2
   
   # Téléchargement du modèle pré-entraîné (optionnel)
   wget https://dl.fbaipublicfiles.com/detectron2/COCO-Detection/faster_rcnn_R_50_FPN_3x/137849458/model_final_280758.pkl \
        -O app/models/detectron2/model_final.pth

**Structure des Dossiers :**

.. code-block:: bash

   mkdir -p data/{originals,annotated,human_data,fine_tune_data,suppression}
   mkdir -p app/models/{detectron2,nlp}
   mkdir -p logs

Étape 5 : Configuration Variables d'Environnement
--------------------------------------------------

.. code-block:: bash

   # Copie du fichier de configuration
   cp .env.example .env
   
   # Édition des variables
   nano .env

**Contenu .env :**

.. code-block:: bash

   # Configuration Flask
   FLASK_ENV=development
   FLASK_DEBUG=True
   SECRET_KEY=your-secret-key-here
   
   # Configuration GPU
   CUDA_VISIBLE_DEVICES=0
   FORCE_CPU_MODE=False
   
   # API Keys
   GEMINI_API_KEY=your-gemini-api-key
   SERPAPI_KEY=your-serpapi-key
   
   # Configuration OCR
   PADDLEOCR_USE_GPU=True
   PADDLEOCR_LANG=fr,en
   
   # Configuration Modèles
   DETECTRON2_MODEL_PATH=app/models/detectron2/model_final.pth
   DETECTRON2_CONFIG_PATH=app/configs/faster_rcnn_R_50_FPN_3x.yaml
   
   # Configuration Base de Données (optionnel)
   DATABASE_URL=sqlite:///app.db
   
   # Ollama (LLM local)
   OLLAMA_BASE_URL=http://localhost:11434

Installation des Services Externes
===================================

Ollama (LLM Local)
------------------

.. code-block:: bash

   # Installation Ollama (Linux)
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Démarrage du service
   ollama serve
   
   # Installation du modèle Mistral (dans un autre terminal)
   ollama pull mistral

Chrome/Chromium pour Selenium
------------------------------

.. code-block:: bash

   # Ubuntu/Debian
   wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
   sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
   sudo apt update
   sudo apt install google-chrome-stable
   
   # Vérification
   google-chrome --version

Playwright (Alternative)
-------------------------

.. code-block:: bash

   # Installation des navigateurs Playwright
   playwright install
   
   # Ou seulement Chromium
   playwright install chromium

Configuration et Tests
======================

Test de l'Installation
-----------------------

.. code-block:: bash

   # Test de base
   python -c "
   import torch
   import cv2
   import nltk
   import spacy
   print('✅ Tous les modules importés avec succès')
   print(f'PyTorch version: {torch.__version__}')
   print(f'CUDA disponible: {torch.cuda.is_available()}')
   "

Test des Composants
-------------------

.. code-block:: bash

   # Test OCR
   python -c "
   from paddleocr import PaddleOCR
   ocr = PaddleOCR(use_angle_cls=True, lang='fr')
   print('✅ PaddleOCR initialisé')
   "
   
   # Test Detectron2
   python -c "
   from detectron2.engine import DefaultPredictor
   from detectron2.config import get_cfg
   print('✅ Detectron2 disponible')
   "
   
   # Test spaCy
   python -c "
   import spacy
   nlp = spacy.load('fr_core_news_sm')
   print('✅ spaCy français chargé')
   "

Lancement de l'Application
===========================

Mode Développement
------------------

.. code-block:: bash

   # Activation environnement
   conda activate smartwebscraper
   # ou
   source venv/bin/activate
   
   # Lancement Flask
   python run.py

.. code-block:: python

   # Contenu run.py
   from app import create_app
   import os
   
   app = create_app()
   
   if __name__ == '__main__':
       app.run(
           host='0.0.0.0',
           port=5000,
           debug=True
       )

**Accès Application :**

.. code-block:: text

   Interface Utilisateur : http://localhost:5000
   Interface Admin       : http://localhost:5000/admin/login

Mode Production
---------------

.. code-block:: bash

   # Installation Gunicorn
   pip install gunicorn
   
   # Lancement production
   gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"

Configuration Docker (Optionnel)
=================================

.. code-block:: dockerfile

   FROM python:3.9-slim
   
   # Dépendances système
   RUN apt-get update && apt-get install -y \
       git \
       wget \
       libgl1-mesa-glx \
       libglib2.0-0 \
       libsm6 \
       libxext6 \
       libxrender-dev \
       libgomp1 \
       && rm -rf /var/lib/apt/lists/*
   
   # Dossier de travail
   WORKDIR /app
   
   # Installation dépendances Python
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   # Copie du code
   COPY . .
   
   # Modèles NLP
   RUN python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
   RUN python -m spacy download fr_core_news_sm
   
   EXPOSE 5000
   CMD ["python", "run.py"]

.. code-block:: bash

   # Construction et lancement
   docker build -t smartwebscraper .
   docker run -p 5000:5000 -v $(pwd)/data:/app/data smartwebscraper

Dépannage
=========

Problèmes Courants
------------------

.. list-table:: Solutions aux Erreurs Fréquentes
   :header-rows: 1
   :widths: 40 60

   * - **Erreur**
     - **Solution**
   * - ``ModuleNotFoundError: detectron2``
     - Réinstaller via git+https://github.com/facebookresearch/detectron2.git
   * - ``CUDA out of memory``
     - Définir FORCE_CPU_MODE=True dans .env
   * - ``PaddleOCR download failed``
     - Connexion Internet + retry, ou installation manuelle modèles
   * - ``spaCy model not found``
     - python -m spacy download fr_core_news_sm
   * - ``Permission denied Chrome``
     - sudo chmod +x /usr/bin/google-chrome

Logs et Debug
-------------

.. code-block:: bash

   # Logs détaillés
   export FLASK_DEBUG=1
   export DETECTRON2_VERBOSE=1
   
   # Lancement avec logs
   python run.py 2>&1 | tee logs/app.log

.. tip::
   **Conseils d'installation :**
   
   * Toujours utiliser un environnement virtuel
   * Installer CUDA avant PyTorch si GPU disponible
   * Tester chaque composant individuellement
   * Consulter les logs en cas d'erreur
   * Utiliser Docker pour un déploiement reproductible
