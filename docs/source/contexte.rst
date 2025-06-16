Contexte Général
================

Dans un monde où le contenu numérique est massivement généré, stocké et diffusé via des interfaces web, 
la capacité à extraire, comprendre, organiser et exploiter automatiquement ces informations devient cruciale. 

C'est dans cette perspective que s'inscrit ce projet : **SmartWebScraper-CV**, une application intelligente 
combinant Computer Vision, OCR, NLP et LLM pour extraire, comprendre et structurer automatiquement le 
contenu de pages web capturées sous forme d'images.

Problématiques du Scrapping Traditionnel
=========================================

Le projet trouve son utilité dans les problèmes de scrapping textuel dus à :

.. warning::
   **Défis techniques majeurs :**

   * **Obfuscation du code HTML** : Code intentionnellement rendu illisible
   * **Obfuscation JavaScript lourde** : Scripts complexes bloquant l'extraction
   * **Texte rendu sous forme d'image** : PDF, images, contenu non-textuel
   * **Interfaces complexes ou graphiques** : Structures visuelles non-standards

Solutions Apportées par l'Approche Visuelle
===========================================

Notre approche par Computer Vision contourne ces limitations en :

1. **Capturant visuellement** la page complète
2. **Analysant l'image** avec des modèles de détection d'objets
3. **Extrayant le texte** via OCR sur les zones pertinentes
4. **Traitant intelligemment** le contenu avec NLP et LLM

.. mermaid::

   flowchart TD
       A[Page Web] --> B[Capture d'écran]
       B --> C[Détection Computer Vision]
       C --> D[Zones d'intérêt identifiées]
       D --> E[Extraction OCR]
       E --> F[Traitement NLP]
       F --> G[Analyse intelligente]

Avantages de Cette Approche
============================

.. grid:: 2

   .. grid-item-card:: 🚫 Contournement des Protections
      
      Évite les blocages anti-bot et l'obfuscation de code

   .. grid-item-card:: 🎯 Précision Contextuelle
      
      Détecte automatiquement les zones pertinentes (titre, contenu, publicités)

   .. grid-item-card:: 🔄 Adaptabilité
      
      Fonctionne sur tout type de site sans configuration spécifique

   .. grid-item-card:: 📊 Données Structurées
      
      Produit des annotations réutilisables pour l'entraînement de modèles

Contexte Académique
===================

Ce projet s'inscrit dans le cadre de la formation **IATD-SI** (Ingénierie de l'Intelligence Artificielle 
et des Technologies de la Donnée pour les Systèmes Industriels) à l'ENSAM Meknès.

Il représente une synthèse pratique des compétences acquises en :

* Intelligence Artificielle et Machine Learning
* Vision par Ordinateur
* Traitement du Langage Naturel
* Développement d'Applications Web
* Gestion de Projets Techniques

.. note::
   Ce travail marque une étape importante de notre formation, mais aussi une base concrète 
   sur laquelle nous comptons bâtir des solutions encore plus ambitieuses au croisement 
   de la vision par ordinateur, du traitement du langage et des systèmes intelligents.
