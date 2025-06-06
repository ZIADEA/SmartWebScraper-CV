Installation
============

Pour exécuter le projet en local, veuillez suivre les étapes suivantes :

Prérequis
---------
- Editeur de code (Visual Studio Code, Cursorai,  PyCharm, etc.)
- Python 3.10+ recommandé
- Git installé 
- Environnement virtuel (venv ou conda)
- Navigateur Chrome version 

Clonage du projet
-----------------
dans le terminal, exécutez la commande suivante pour cloner le dépôt :
.. code-block:: bash

    git clone https://github.com/ZIADEA/SmartWebScraper-CV.git
    cd SmartWebScraper-CV

Installation des dépendances
----------------------------

.. code-block:: bash

    python -m venv venv
    source venv/bin/activate  # ou venv\\Scripts\\activate sous Windows
    pip install -r requirements.txt

Ce fichier contient toutes les dépendances nécessaires au développement et à l'entraînement du projet. L'application Web située dans ``LocalApp/SMARTWEBSCRAPPER-CV`` possède son propre fichier ``requirements.txt`` dédié à son exécution locale.

environment activation
--------------------
.. code-block:: bash

     conda activate <nom_de_l_environnement>  # pour conda
     source venv/bin/activate  # pour venv

Compuer vision model demo
------------------------------------------------
make sure to install the required dependencies and activate the virtual environment before running the demo

you can open the demo notebook **CV_model_demo.ipynb** in the **notebooks** directory to test the computer vision model.
this notebook allows you to load an image and get the predictions of the trained detection model.

make sure to put an website URL  
.. code-block:: bash
     # in the notebook
    url = "https://exemple.com"
    
you will get the predictions of the CV trained model on the image of the website you provided link and the results will be displayed visually.

