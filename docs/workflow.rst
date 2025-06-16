Workflow et Guide d'Utilisation
================================

Cette section détaille le workflow complet d'utilisation de SmartWebScraper-CV, 
de la capture d'une page web à l'analyse finale du contenu.

Vue d'Ensemble du Workflow
===========================

.. mermaid::

   flowchart TD
       A[Accès Application] --> B[Soumission URL]
       B --> C[Capture Automatique]
       C --> D[Détection Zones]
       D --> E{Validation Utilisateur}
       E -->|✅ Prédiction OK| F[Sélection Zones]
       E -->|❌ Correction Requise| G[Annotation Manuelle]
       G --> H[Validation Annotation]
       H --> F
       F --> I[Extraction OCR]
       I --> J[Traitement NLP]
       J --> K[Interface d'Analyse]
       K --> L[Résultats & Export]
       L --> M[Feedback Admin]
       M --> N[Amélioration Modèle]

Étapes Détaillées
==================

Phase 1 : Capture et Détection
-------------------------------

**Étape 1.1 : Accès à l'Application**

.. code-block:: text

   URL : http://localhost:5000
   Interface : Page d'accueil utilisateur

Actions disponibles :

* Saisie d'URL à analyser
* Accès à l'historique des captures
* Configuration des paramètres de capture

**Étape 1.2 : Soumission d'URL**

.. list-table:: Paramètres de Capture
   :header-rows: 1
   :widths: 30 70

   * - **Paramètre**
     - **Description**
   * - **URL Target**
     - Adresse web à capturer et analyser
   * - **Scroll Mode**
     - Automatique (recommandé) ou manuel
   * - **Wait Time**
     - Temps d'attente pour le chargement (défaut: 3s)
   * - **Viewport Size**
     - Résolution de capture (défaut: 1280x800)

**Étape 1.3 : Capture Automatique**

Le système effectue automatiquement :

.. code-block:: python

   # Processus de capture
   1. Lancement navigateur (Chrome/Playwright)
   2. Navigation vers l'URL
   3. Attente chargement complet
   4. Scroll progressif intelligent
   5. Capture screenshot haute résolution
   6. Sauvegarde en data/originals/

**Étape 1.4 : Détection des Zones**

Application du modèle Faster R-CNN :

.. grid:: 2

   .. grid-item-card:: 🤖 Détection Automatique
      
      * 18 classes de zones détectées
      * Seuil de confiance : 0.4
      * Filtrage des doublons (NMS)
      * Génération coordonnées précises

   .. grid-item-card:: 📊 Résultats Visualisés
      
      * Boîtes colorées par classe
      * Labels avec score de confiance
      * Interface de validation interactive
      * Options d'édition en temps réel

Phase 2 : Validation et Annotation
-----------------------------------

**Étape 2.1 : Interface de Validation**

L'utilisateur accède à une interface permettant de :

.. list-table:: Actions de Validation
   :header-rows: 1
   :widths: 25 75

   * - **Action**
     - **Description**
   * - **Valider**
     - Approuver les prédictions automatiques
   * - **Corriger**
     - Modifier les boîtes existantes
   * - **Ajouter**
     - Dessiner de nouvelles zones
   * - **Supprimer**
     - Éliminer les fausses détections

**Étape 2.2 : Annotation Manuelle (si nécessaire)**

Interface Canvas HTML5 avec :

.. code-block:: javascript

   // Fonctionnalités d'annotation
   - Dessin de rectangles au clic-glissé
   - Sélection de classe via dropdown
   - Redimensionnement des boîtes
   - Suppression par double-clic
   - Export JSON automatique

**Étape 2.3 : Validation Final**

.. mermaid::

   flowchart LR
       A[Annotations Finalisées] --> B{Contrôle Qualité}
       B -->|✅ OK| C[Sauvegarde Validée]
       B -->|❌ Erreurs| D[Retour Correction]
       C --> E[data/human_data/validated/]
       D --> A

Phase 3 : Extraction et Traitement
-----------------------------------

**Étape 3.1 : Sélection des Zones à Traiter**

Interface de sélection permettant de :

* Cocher/décocher les zones détectées
* Prévisualiser le contenu de chaque zone
* Définir l'ordre de traitement
* Exclure les zones non-pertinentes (ads, footer, etc.)

**Étape 3.2 : Extraction OCR**

.. code-block:: python

   # Pipeline OCR avec PaddleOCR
   for zone in zones_selectionnees:
       1. Découpe de l'image selon coordonnées
       2. Prétraitement (contraste, binarisation)
       3. Application PaddleOCR
       4. Nettoyage et correction du texte
       5. Structuration en blocs cohérents

**Étape 3.3 : Traitement NLP**

Le système ``CompleteOCRQASystem`` effectue :

.. list-table:: Traitements NLP Automatiques
   :header-rows: 1
   :widths: 30 70

   * - **Traitement**
     - **Description**
   * - **Nettoyage**
     - Correction erreurs OCR, normalisation
   * - **Segmentation**
     - Division en phrases cohérentes
   * - **Vectorisation**
     - TF-IDF + Word2Vec pour recherche
   * - **Indexation**
     - Préservation 100% du contenu
   * - **Entités**
     - Extraction NER (personnes, lieux, dates)

Phase 4 : Analyse et Interaction
---------------------------------

**Étape 4.1 : Interface d'Analyse**

L'utilisateur accède à un dashboard avec :

.. grid:: 2

   .. grid-item-card:: 📝 Analyse Automatique
      
      * Résumé extractif du contenu
      * Mots-clés principaux (top 20)
      * Sujets dominants (clustering)
      * Entités nommées détectées

   .. grid-item-card:: 🤖 Interaction Intelligente
      
      * Zone de questions libres
      * Suggestions de requêtes
      * Choix LLM (Gemini/Mistral)
      * Historique des interactions

**Étape 4.2 : Système Question-Réponse**

.. mermaid::

   flowchart TD
       A[Question Utilisateur] --> B[Classification Intention]
       B --> C{Type de Question}
       C -->|Simple| D[Traitement Local NLP]
       C -->|Complexe| E[Appel LLM Externe]
       D --> F[Recherche Similarité TF-IDF]
       E --> G[Contexte Complet + Prompt]
       F --> H[Réponse Structurée]
       G --> H
       H --> I[Affichage Utilisateur]

**Types de Questions Supportées :**

.. code-block:: text

   Exemples de questions traitées :
   
   📊 Analytiques :
   - "Résume le contenu principal"
   - "Quels sont les mots-clés importants ?"
   - "Quels sujets sont abordés ?"
   
   🔍 Factuelles :
   - "Qui est l'auteur de cet article ?"
   - "Quelle est la date de publication ?"
   - "Où se déroule l'événement ?"
   
   💡 Conceptuelles :
   - "Explique le concept principal"
   - "Comment fonctionne cette technologie ?"
   - "Pourquoi cette décision a été prise ?"

**Étape 4.3 : Choix du Moteur LLM**

.. list-table:: Comparaison des Moteurs
   :header-rows: 1
   :widths: 20 40 40

   * - **Moteur**
     - **Avantages**
     - **Cas d'Usage Recommandés**
   * - **Local NLP**
     - Rapide, gratuit, hors-ligne
     - Questions simples, résumés
   * - **Mistral (Local)**
     - Privé, bon français, gratuit
     - Analyse approfondie, confidentialité
   * - **Gemini (API)**
     - Très performant, multimodal
     - Questions complexes, créativité

Phase 5 : Résultats et Export
------------------------------

**Étape 5.1 : Visualisation des Résultats**

Interface de présentation avec :

.. code-block:: text

   Sections d'affichage :
   ├── 📊 Résumé Exécutif
   ├── 🏷️ Zones Détectées (avec métadonnées)
   ├── 📝 Texte Extrait (par zone)
   ├── 🧠 Analyse NLP Complète
   ├── 💬 Historique Q&A
   └── 📈 Métriques de Qualité

**Étape 5.2 : Options d'Export**

.. grid:: 3

   .. grid-item-card:: 📄 Formats Texte
      :text-align: center
      
      * TXT (texte brut)
      * MD (Markdown)
      * JSON (structuré)

   .. grid-item-card:: 📊 Formats Données
      :text-align: center
      
      * CSV (entités, mots-clés)
      * COCO (annotations)
      * Excel (rapport complet)

   .. grid-item-card:: 🖼️ Formats Visuels
      :text-align: center
      
      * PNG (image annotée)
      * PDF (rapport complet)
      * HTML (page interactive)

Phase 6 : Workflow Administrateur
----------------------------------

**Étape 6.1 : Accès Interface Admin**

.. code-block:: text

   URL : http://localhost:5000/admin/login
   Authentification : email/password depuis .env

**Étape 6.2 : Dashboard de Validation**

.. list-table:: Fonctionnalités Admin
   :header-rows: 1
   :widths: 30 70

   * - **Section**
     - **Actions Disponibles**
   * - **Annotations en Attente**
     - Valider/Rejeter les soumissions utilisateur
   * - **Contrôle Qualité**
     - Vérifier cohérence des annotations
   * - **Gestion Dataset**
     - Organiser données fine-tuning
   * - **Métriques Système**
     - Suivre performances modèle
   * - **Fine-tuning**
     - Lancer ré-entraînement

**Étape 6.3 : Processus de Validation**

.. mermaid::

   flowchart TD
       A[Nouvelle Annotation] --> B[Contrôle Automatique]
       B --> C{Qualité OK?}
       C -->|✅ Passe| D[Queue Validation Admin]
       C -->|❌ Échec| E[Retour Utilisateur]
       D --> F[Examen Manuel Admin]
       F --> G{Décision Admin}
       G -->|✅ Approuvé| H[data/fine_tune_data/]
       G -->|❌ Rejeté| I[Feedback Utilisateur]
       H --> J[Entraînement Disponible]

**Étape 6.4 : Fine-tuning du Modèle**

.. code-block:: python

   # Processus automatisé de fine-tuning
   1. Vérification minimum 50 nouvelles annotations
   2. Préparation dataset (train/val split)
   3. Configuration Detectron2
   4. Lancement entraînement (1000-5000 itérations)
   5. Évaluation métriques (mAP, IoU)
   6. Déploiement nouveau modèle si amélioration

Bonnes Pratiques d'Utilisation
===============================

Pour l'Utilisateur Final
-------------------------

.. tip::
   **Optimiser la qualité des résultats :**
   
   * Choisir des pages avec contenu textuel riche
   * Éviter les sites avec trop de JavaScript dynamique
   * Valider soigneusement les détections automatiques
   * Poser des questions précises et contextualisées
   * Utiliser Gemini pour l'analyse créative, Mistral pour la confidentialité

Pour l'Administrateur
---------------------

.. tip::
   **Maintenir la qualité du système :**
   
   * Valider régulièrement les annotations (objectif: 1/jour)
   * Maintenir un équilibre entre les classes du dataset
   * Lancer le fine-tuning tous les 100 nouvelles annotations
   * Surveiller les métriques de performance
   * Archiver régulièrement les données importantes

Gestion des Erreurs et Edge Cases
==================================

Problèmes Courants et Solutions
--------------------------------

.. list-table:: Résolution de Problèmes Workflow
   :header-rows: 1
   :widths: 30 35 35

   * - **Problème**
     - **Cause Probable**
     - **Solution**
   * - **Capture échoue**
     - Site protégé, timeout
     - Retry avec délai, vérifier URL
   * - **Pas de détection**
     - Layout non-standard
     - Annotation manuelle requise
   * - **OCR vide**
     - Zone sans texte/illisible
     - Ajuster prétraitement image
   * - **Réponse NLP incohérente**
     - Texte de mauvaise qualité
     - Nettoyer extraction OCR
   * - **LLM timeout**
     - Texte trop long/API surchargée
     - Diviser en segments plus petits

Monitoring et Métriques
-----------------------

.. code-block:: text

   Indicateurs à surveiller :
   
   📈 Performance Technique :
   - Temps de capture moyen : < 10s
   - Précision détection : > 40% mAP
   - Qualité OCR : > 85% mots corrects
   - Temps réponse NLP : < 5s
   
   👥 Usage Utilisateur :
   - Taux validation annotations : > 70%
   - Satisfaction questions répondues : > 80%
   - Utilisation fonctionnalités : équilibrée
   
   🔧 Système :
   - Utilisation GPU/CPU : optimale
   - Espace disque : surveillé
   - Erreurs critiques : < 1%

.. note::
   **Workflow en amélioration continue :**
   
   Ce workflow évolue avec les retours utilisateurs et les améliorations techniques. 
   Les mises à jour de la documentation reflètent les dernières optimisations 
   et nouvelles fonctionnalités disponibles.
