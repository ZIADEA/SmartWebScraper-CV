SmartWebScraper-CV Documentation
==================================

.. image:: _static/logo.png
   :width: 200px
   :align: center
   :alt: SmartWebScraper-CV Logo

Application intelligente d'annotation de pages web par Computer Vision, OCR, NLP et LLM

.. note::
   Ce projet a été réalisé dans le cadre de la formation d'ingénieur à l'ENSAM Meknès, 
   au sein de la filière IATD-SI (Ingénierie de l'Intelligence Artificielle et des 
   Technologies de la Donnée pour les Systèmes Industriels).

**Auteurs:** DJERI-ALASSANI OUBENOUPOU & EL MAJDI WALID

**Encadré par:** Professeur Tawfik MASROUR

**Date:** 16 Juin 2025

Aperçu du Projet
================

SmartWebScraper-CV est une application complète qui combine plusieurs technologies 
d'intelligence artificielle pour extraire, comprendre et structurer automatiquement 
le contenu de pages web capturées sous forme d'images.

.. image:: _static/architecture_overview.png
   :width: 600px
   :align: center
   :alt: Architecture générale du système

Technologies Clés
==================

* **Computer Vision** : Detectron2 (Faster R-CNN) pour la détection d'objets
* **OCR** : PaddleOCR pour l'extraction de texte
* **NLP** : NLTK, spaCy, TF-IDF pour le traitement du langage naturel  
* **LLM** : Gemini API et Mistral via Ollama
* **Web Framework** : Flask avec interface responsive

Fonctionnalités Principales
============================

.. grid:: 2

   .. grid-item-card:: 🖼️ Capture Intelligente
      :text-align: center
      
      Capture automatique de pages web avec gestion du contenu dynamique

   .. grid-item-card:: 🎯 Détection Automatique
      :text-align: center
      
      Détection des zones fonctionnelles (header, footer, content, ads, etc.)

   .. grid-item-card:: 📝 OCR Avancé
      :text-align: center
      
      Extraction précise du texte avec prétraitement intelligent

   .. grid-item-card:: 🤖 Analyse NLP
      :text-align: center
      
      Résumé automatique, Q&A et analyse sémantique

Table des Matières
==================

.. toctree::
   :maxdepth: 2
   :caption: Introduction
   
   introduction/contexte
   introduction/objectifs
   introduction/technologies
   introduction/historique

.. toctree::
   :maxdepth: 2
   :caption: Acquisition des Données
   
   data/constitution
   data/capture
   data/limites

.. toctree::
   :maxdepth: 2
   :caption: Annotation et Dataset
   
   annotation/objectifs
   annotation/roboflow
   annotation/structuration
   annotation/slicing
   annotation/manuel

.. toctree::
   :maxdepth: 2
   :caption: Modélisation
   
   modeling/detection
   modeling/entrainement
   modeling/finetuning
   modeling/integration

.. toctree::
   :maxdepth: 2
   :caption: OCR et NLP
   
   nlp/ocr
   nlp/traitement
   nlp/qa
   nlp/llm

.. toctree::
   :maxdepth: 2
   :caption: Architecture Application
   
   architecture/structure
   architecture/composants
   architecture/roles
   architecture/navigation

.. toctree::
   :maxdepth: 2
   :caption: Résultats et Évaluation
   
   results/performances
   results/metriques
   results/evaluation

.. toctree::
   :maxdepth: 2
   :caption: Usage et Perspectives
   
   usage/public
   usage/cas_usage
   usage/perspectives

.. toctree::
   :maxdepth: 2
   :caption: Problèmes et Solutions
   
   problems/capture
   problems/detection
   problems/ocr
   problems/solutions

.. toctree::
   :maxdepth: 2
   :caption: API et Références
   
   api/reference
   installation/guide
   deployment/docker

Indices et tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
