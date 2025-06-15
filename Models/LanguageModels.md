#  Modèle de traitement de langage - SmartWebScraper-CV

##  Processing

## LanguageModels

## Grand modèle de langage


# Rapport Technique : SmartWebScraper-CV avec Moteur NLP Intégré

## Présentation Générale

**SmartWebScraper-CV** est une application complète de vision par ordinateur et de traitement de texte destinée à l’analyse intelligente des pages web capturées sous forme d’images. L’objectif est double : (1) détecter et annoter les zones importantes d’une page web (en-tête, publicité, contenu, etc.) à l’aide d’un modèle de détection entraîné, puis (2) extraire le texte via OCR et permettre une interaction intelligente avec ce contenu via un moteur NLP interne, sans dépendance à des API cloud.

Le projet est découpé en plusieurs modules bien structurés :

* **Capture et découpage d’images**
* **OCR optimisé (PaddleOCR)**
* **Nettoyage et structuration du texte**
* **Indexation et Vectorisation (TF-IDF, Word2Vec)**
* **Résumé automatique et extraction de sujets**
* **Moteur de question-réponse basé sur la similarité**
* **NER (reconnaissance d'entités nommées) avec spaCy**

---

## Pipeline Technique Complet

### 1. Capture d'image et prétraitement visuel

* Utilisation de **Playwright** ou **Selenium** pour capturer des captures d’écran de pages web.
* Découpage intelligent des images de grande taille via le module `ImageSlicer`.
* Prétraitement adaptatif des images : redimensionnement conditionnel, conversion en niveaux de gris, amélioration du contraste par **CLAHE**, débruitage léger.

### 2. Reconnaissance de texte (OCR)

* Le moteur OCR repose sur **PaddleOCR**, configuré en mode CPU ou GPU.
* Le système peut :

  * détecter le besoin de prétraitement via des heuristiques (variance de Laplacien, contraste).
  * découper l’image pour traitement parallèle.
  * extraire du texte avec position verticale pour reconstruction structurée.
* Optimisations : cache global OCR, multithreading avec `ThreadPoolExecutor`, exécution sans sauvegarde de fichiers intermédiaires.

### 3. Nettoyage du texte OCR

* Nettoyage intelligent avec expressions régulières :

  * Correction des erreurs courantes (`rn → m`, `1 → l`, `vv → w`, etc.)
  * Suppression des artefacts OCR, des mots trop courts, ponctuation parasite.
* Utilisation de **NLTK** pour :

  * la suppression des stopwords (`stopwords.words()`)
  * la tokenisation (`sent_tokenize`, `word_tokenize`)

### 4. Segmentation et structuration du contenu

* Le texte est segmenté en phrases à l’aide de NLTK ou fallback regex.
* Les phrases sont filtrées selon : longueur, nombre de mots, présence de lettres.

### 5. Vectorisation du texte

#### a) TF-IDF (scikit-learn)

* Création d’un modèle **TF-IDF adaptatif** selon :

  * Langue (stopwords fr/en)
  * Nombre de phrases disponibles
  * Objectif CPU vs GPU
* Échantillonnage intelligent (début, milieu, fin) pour réduire la charge sans perdre le sens global du document.

#### b) Word2Vec (Gensim)

* Entraînement léger d’un modèle **Word2Vec** local sur le corpus tokenisé.
* Permet d’enrichir l’analyse sémantique, en complément de TF-IDF.

### 6. Extraction de sujets (Topics) et résumé

#### a) Clustering KMeans

* Application de **KMeans** sur les vecteurs TF-IDF pour regrouper les phrases en `n_clusters` (représentant des sujets).
* Représentant du sujet choisi selon la phrase la plus courte et représentative.

#### b) Résumé

* Score de chaque phrase = TF-IDF total \* bonus de position \* bonus de longueur.
* Sélection des `n` phrases les plus représentatives.

### 7. Extraction d’entités nommées (NER)

* Utilisation de **spaCy** (`fr_core_news_sm`) pour détecter des entités :

  * `DATE`, `ORG`, `CARDINAL`, etc.
* Permet de répondre à des questions spécifiques comme "Quelle est la date ?", "Quel est le titre ?"

---

## Système de Question-Réponse (QA System)

Le module `WebQASystem` permet de répondre à des requêtes utilisateur sans API externe, en utilisant uniquement le texte OCR extrait.

### Fonctionnalités :

* **Résumé du contenu**
* **Thèmes principaux / mots-clés**
* **Questions spécifiques avec réponses extraites**
* **Extraction directe d’entités**
* **Renvoi de tout le contexte pour un LLM externe**

### Méthodologie QA :

* Vectorisation de la question avec TF-IDF.
* Calcul de la **similarité cosinus** entre la question et chaque phrase indexée.
* Bonus de pertinence si chevauchement lexical important.
* Fusion des réponses les plus pertinentes, avec limitation de la longueur finale.

---

## Architecture Modulaire

```text
SmartWebScraper-CV/
├── app/
│   ├── routes/               # Routes Flask
│   ├── templates/            # Interface HTML
│   ├── utils/
│   │   ├── ocr.py            # PaddleOCR wrapper + découpage
│   │   ├── nlp_cleaner.py    # Nettoyage de texte OCR
│   │   ├── qa_engine.py      # Moteur NLP complet
│   ├── models/
│   │   └── modelcv/          # Modèle de détection d’objet
│   └── data/
│       ├── originals/        # Captures d’écran originales
│       ├── annotated/        # Résultats visuels annotés
│       ├── human_data/       # Annotations manuelles validées
│       ├── fine_tune_data/   # Données destinées au retrain
```

---

## Performances et Optimisation

* **Traitement OCR parallèle** : gain de 30–50% sur grandes images.
* **Découpage intelligent** : évite les limites de PaddleOCR sur très grandes dimensions.
* **Indexation rapide** : TF-IDF sur échantillon réduit.
* **Traitement 100% local** : aucune dépendance à une API LLM.
* **Modes CPU/GPU adaptatifs** : nombre de workers, batch size, dimensions images.

---

## Limitations & Améliorations Possibles

* Intégrer un résumé **neural abstractive** (ex. BART ou T5).
* Ajouter une interface graphique de **visualisation de topics**.
* Implémenter un système de **feedback utilisateur supervisé** (renforcement).
* Permettre la **traduction multilingue automatique**.
* Ajouter des **features de recherche contextuelle** (ex: BM25, Dense Vectors).

---

## Conclusion

Ce module NLP intégré à SmartWebScraper-CV constitue un moteur complet d’analyse documentaire, capable de traiter un site web capturé en image, d’en extraire le texte, de structurer l’information, d’en proposer une synthèse et de répondre à des questions. Il repose uniquement sur des bibliothèques open-source puissantes : PaddleOCR, scikit-learn, NLTK, spaCy, Gensim, etc.

Cette architecture offre une solution robuste, extensible, optimisée pour le CPU, et capable d’être embarquée dans une application finale **sans dépendre du cloud**.

Un moteur NLP **pratique, intelligent et local**.
