Distribution et Support
=======================

.. raw:: html

   <div align="center">
     <img src="https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExNnpieHBhYTE4ZTB0MDBmNmEzN3hveWwxc3Q2OGVqanlrOGUzNjRiYyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/lJNoBCvQYp7nq/giphy.gif" alt="coming soon" width="300"/>
   </div>

Version française
=================

.. important::
   **[ Information ]**
   
   La version ``.exe`` de l'application sera disponible prochainement sur cette page.

.. raw:: html

   <div align="center">
     <img src="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExdzBxZ21uYTRzMHRyZW5hdzE3eGJja3FtdjF5eWpmZWZsdXV3czdwYSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/l0HlNQ03J5JxX6lva/giphy.gif" width="260" alt="Work in progress"/>
   </div>

Désolé pour le désagrément.  
En attendant, veuillez consulter le fichier ``README.md`` du dépôt. Il contient les étapes détaillées pour exécuter l'application en local.

Assistance à l'installation
----------------------------

Si vous avez des difficultés à installer l'application :

* Contactez-moi à l'adresse : djeryala@gmail.com
* Objet du mail : ``Scrapp LocalApp Problem installation``

Problème d'un composant spécifique ?
-------------------------------------

* Contactez-moi à l'adresse : djeryala@gmail.com
* Objet du mail : ``Scrapp LocalApp Problem composant``

Déploiement à venir
--------------------

Je travaille activement sur :

* Le déploiement de l'application via **Oracle Cloud**
* Une version ``.exe`` autonome pour une installation simplifiée

.. raw:: html

   <div align="center">
     <img src="https://media.giphy.com/media/h4OGa0npayr99WEO7z/giphy.gif" alt="Déploiement en cours" width="320"/>
   </div>

English Version
================

.. important::
   **[ Information ]**
   
   The ``.exe`` version of the application will be available soon on this page.

.. raw:: html

   <div align="center">
     <img src="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExZ3NqNmp3dGgwODN6Z2hrZWh0b2dwbjA3Mmc3NmVnM3ZtbGVwaWJxcyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/3ohhwF34cGDoFFhRfy/giphy.gif" width="260" alt="Deployment coming soon"/>
   </div>

Sorry for the inconvenience.  
In the meantime, please refer to the ``README.md`` file in the repository. It contains step-by-step instructions to run the app locally.

Installation Support
---------------------

If you encounter any installation issue:

* Contact me at: djeryala@gmail.com
* Email subject: ``Scrapp LocalApp Installation Problem``

A component not working properly?
----------------------------------

* Contact me at: djeryala@gmail.com
* Email subject: ``Scrapp LocalApp Component Issue``

Upcoming Deployment
--------------------

I'm currently working on:

* Deploying the app on **Oracle Cloud**
* A standalone ``.exe`` version to simplify installation

.. raw:: html

   <div align="center">
     <img src="https://media.giphy.com/media/l2R01JcZ0aWwKFOw0/giphy.gif" alt="Stay tuned" width="320"/>
   </div>

Options de Déploiement Actuelles
=================================

Installation Locale
--------------------

Actuellement, la méthode principale pour utiliser SmartWebScraper-CV est l'installation locale :

.. grid:: 2

   .. grid-item-card:: 🏠 Déploiement Local
      :text-align: center
      
      * Installation via Python et pip
      * Contrôle total de l'environnement
      * Aucune dépendance cloud
      * Performance optimale

   .. grid-item-card:: 🐳 Docker (Expérimental)
      :text-align: center
      
      * Container isolé
      * Installation reproductible
      * Compatible multi-plateforme
      * En cours de stabilisation

Installation via Git
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Méthode recommandée
   git clone https://github.com/ZIADEA/SmartWebScraper-CV.git
   cd SmartWebScraper-CV/LocalApp/SMARTWEBSCRAPPER-CV
   pip install -r requirements.txt
   python run.py

Pour plus de détails, consultez :doc:`../installation/local`.

Container Docker
~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Construction de l'image
   docker build -t smartwebscraper .
   
   # Lancement avec volumes persistants
   docker run -p 5000:5000 -v $(pwd)/data:/app/data smartwebscraper

.. warning::
   La version Docker est encore en phase expérimentale. 
   Utilisez l'installation locale pour une expérience optimale.

Roadmap de Distribution
=======================

Développements en Cours
------------------------

.. raw:: html

   <div align="center">
     <img src="https://media.giphy.com/media/h4OGa0npayr99WEO7z/giphy.gif" alt="Deployment in Progress" width="320"/>
   </div>

Je travaille activement sur plusieurs fronts :

Version Exécutable Autonome
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table:: Fonctionnalités Prévues Version .exe
   :header-rows: 1
   :widths: 30 70

   * - **Fonctionnalité**
     - **Description**
   * - **Installation Simple**
     - Un seul fichier .exe à télécharger et exécuter
   * - **Aucune Configuration**
     - Toutes les dépendances incluses
   * - **Interface Graphique**
     - Lanceur avec interface utilisateur intuitive
   * - **Auto-Updates**
     - Mise à jour automatique des modèles
   * - **Multi-langues**
     - Support français et anglais intégré

Déploiement Cloud
~~~~~~~~~~~~~~~~~

.. grid:: 2

   .. grid-item-card:: ☁️ Oracle Cloud
      :text-align: center
      
      * Déploiement gratuit
      * Haute disponibilité
      * Accès web universel
      * Pas d'installation requise

   .. grid-item-card:: 🌐 Version SaaS
      :text-align: center
      
      * Interface web complète
      * API REST publique
      * Gestion multi-utilisateurs
      * Plans gratuit et premium

Chronologie de Déploiement
---------------------------

.. mermaid::

   gantt
       title Roadmap de Distribution SmartWebScraper-CV
       dateFormat  YYYY-MM-DD
       section Version Locale
       Installation actuelle    :done, local, 2025-01-01, 2025-06-16
       Optimisations            :active, opt, 2025-06-16, 30d
       
       section Version Exécutable
       Développement .exe       :active, exe, 2025-06-16, 45d
       Tests & Debug            :test, after exe, 15d
       Release publique         :milestone, release, after test, 0d
       
       section Cloud
       Setup Oracle Cloud       :cloud, 2025-07-01, 30d
       Déploiement beta         :beta, after cloud, 15d
       Version production       :milestone, prod, after beta, 0d

.. tip::
   **Timeline estimée :**
   
   * **Version .exe** : Fin juillet 2025
   * **Déploiement cloud** : Septembre 2025
   * **Version SaaS complète** : Q4 2025

Support et Assistance
=====================

Canaux de Support Disponibles
------------------------------

Assistance Installation
~~~~~~~~~~~~~~~~~~~~~~~~

.. note::
   **Pour les problèmes d'installation :**
   
   * **📧 Email** : djeryala@gmail.com
   * **📝 Objet** : "Scrapp LocalApp Problem installation"
   * **📋 Inclure** :
     - Système d'exploitation et version
     - Version Python utilisée
     - Messages d'erreur complets
     - Étapes suivies avant l'erreur

Problèmes de Composants
~~~~~~~~~~~~~~~~~~~~~~~~

.. note::
   **Pour les dysfonctionnements spécifiques :**
   
   * **📧 Email** : djeryala@gmail.com
   * **📝 Objet** : "Scrapp LocalApp Problem composant"
   * **📋 Inclure** :
     - Description détaillée du problème
     - Composant affecté (OCR, détection, NLP, etc.)
     - Étapes de reproduction
     - Logs d'erreur si disponibles

Template de Rapport de Bug
---------------------------

.. code-block:: text

   Objet : Scrapp LocalApp Problem [composant]
   
   Bonjour,
   
   Je rencontre un problème avec SmartWebScraper-CV :
   
   **Environnement :**
   - OS : [Windows 11 / macOS 12 / Ubuntu 20.04]
   - Python : [3.9.x]
   - Version app : [commit hash ou date]
   
   **Problème rencontré :**
   [Description claire du problème]
   
   **Étapes de reproduction :**
   1. [Étape 1]
   2. [Étape 2]
   3. [Étape 3]
   
   **Comportement attendu :**
   [Ce qui devrait se passer]
   
   **Comportement observé :**
   [Ce qui se passe réellement]
   
   **Logs d'erreur :**
   ```
   [Coller les logs d'erreur ici]
   ```
   
   **Captures d'écran :**
   [Si applicable]
   
   Merci pour votre aide.

Ressources Complémentaires
===========================

Documentation Technique
------------------------

.. list-table:: Ressources Disponibles
   :header-rows: 1
   :widths: 30 40 30

   * - **Ressource**
     - **Description**
     - **Lien**
   * - **Documentation Complète**
     - Guide utilisateur et technique
     - :doc:`../index`
   * - **Guide Installation**
     - Instructions détaillées
     - :doc:`../installation/guide`
   * - **API Reference**
     - Documentation API REST
     - :doc:`../api/reference`
   * - **FAQ**
     - Questions fréquentes
     - :doc:`../problems/solutions`

Communauté et Contributions
----------------------------

.. grid:: 2

   .. grid-item-card:: 🐙 GitHub Repository
      :text-align: center
      
      * Code source complet
      * Issues et bug reports
      * Pull requests welcom
      * Discussions techniques

   .. grid-item-card:: 📚 Documentation
      :text-align: center
      
      * ReadTheDocs hébergé
      * Guides pas-à-pas
      * Exemples d'utilisation
      * API documentation

Futures Versions
-----------------

.. raw:: html

   <div align="center">
     <img src="https://media.giphy.com/media/l2R01JcZ0aWwKFOw0/giphy.gif" alt="Stay Tuned" width="320"/>
   </div>

**Restez informés des nouveautés :**

* **Notifications GitHub** : Suivez le repository pour les releases
* **Mailing List** : Inscription via djeryala@gmail.com
* **Documentation** : Mise à jour automatique sur ReadTheDocs

.. tip::
   **Prochaines améliorations prévues :**
   
   * Interface graphique native (Qt/Tkinter)
   * Support multi-GPU pour accélération
   * API REST publique avec authentification
   * Plugin navigateur pour capture directe
   * Dashboard analytics en temps réel
