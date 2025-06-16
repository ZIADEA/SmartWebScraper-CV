Traitement NLP des Textes Extraits
===================================

Une fois le texte extrait par OCR des zones sélectionnées, un pipeline NLP complet prend le relais 
pour analyser, structurer et permettre l'interaction intelligente avec le contenu.

Architecture du Système NLP
============================

Le module central ``CompleteOCRQASystem`` implémente une approche hybride combinant :

* **Traitement local** via NLTK, spaCy et Scikit-learn
* **Modèles de langage externes** (Gemini, Mistral) pour les requêtes complexes
* **Préservation intégrale** du contenu sans perte d'information

.. mermaid::

   flowchart TD
       A[Texte OCR Brut] --> B[Nettoyage & Prétraitement]
       B --> C[Segmentation en Phrases]
       C --> D[Vectorisation TF-IDF]
       D --> E[Indexation Complète]
       E --> F{Type de Requête}
       F -->|Simple| G[Traitement Local]
       F -->|Complexe| H[LLM Externe]
       G --> I[Réponse Structurée]
       H --> I
       E --> J[Résumé Automatique]
       E --> K[Extraction Entités]

Principe de Préservation à 100%
================================

.. important::
   **Philosophie du système :** Contrairement aux approches qui tronquent ou échantillonnent 
   le contenu, notre système préserve l'intégralité du texte extrait par OCR. 
   
   L'échantillonnage n'intervient que pour les calculs intensifs (vectorisation TF-IDF) 
   tout en gardant le texte complet accessible pour les requêtes.

.. code-block:: python

   class CompleteOCRQASystem:
       def __init__(self):
           # Conservation intégrale du contenu
           self.all_sentences = []  # JAMAIS tronqué
           self.sample_sentences = []  # Échantillon pour calculs
           
       def preserve_full_content(self, text):
           """Préservation complète sans perte"""
           sentences = self.segment_sentences(text)
           self.all_sentences.extend(sentences)
           
           # Échantillonnage seulement si nécessaire
           if len(sentences) > 400:
               self.sample_sentences = random.sample(sentences, 400)
           else:
               self.sample_sentences = sentences

Étapes de Traitement
====================

1. Nettoyage et Pré-traitement
-------------------------------

La classe ``TextCleaner`` effectue un nettoyage robuste :

.. code-block:: python

   class TextCleaner:
       def __init__(self):
           # Corrections OCR pré-compilées
           self.ocr_fixes = {
               r'\brn\b': 'm',      # rn → m
               r'\bvv\b': 'w',      # vv → w  
               r'\b1\b': 'l',       # 1 → l (contexte)
               r'\b0\b': 'o',       # 0 → o (contexte)
           }
           
       def clean_ocr_text(self, text):
           # Application des corrections OCR
           for pattern, replacement in self.ocr_fixes.items():
               text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
           
           # Normalisation générale
           text = text.lower()
           text = re.sub(r'[^\w\s]', ' ', text)  # Suppression ponctuation
           text = re.sub(r'\s+', ' ', text)      # Espaces multiples
           
           return text.strip()

**Processus de Nettoyage :**

.. list-table:: Étapes de Nettoyage
   :header-rows: 1
   :widths: 30 70

   * - **Étape**
     - **Action**
   * - Corrections OCR
     - Remplacement des erreurs fréquentes (rn→m, vv→w)
   * - Normalisation casse
     - Conversion en minuscules
   * - Suppression ponctuation
     - Garde uniquement alphanumérique et espaces
   * - Filtrage stop-words
     - Suppression mots vides (français/anglais)
   * - Lemmatisation
     - Réduction aux formes canoniques (optionnel)

2. Segmentation en Phrases
---------------------------

.. code-block:: python

   def segment_sentences
