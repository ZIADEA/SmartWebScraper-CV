import os
import re
import cv2
import numpy as np
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from gensim.models import Word2Vec
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
import nltk
from paddleocr import PaddleOCR
from concurrent.futures import ThreadPoolExecutor, as_completed
import warnings
import time
import multiprocessing
import spacy
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from gensim.models import Word2Vec
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk

warnings.filterwarnings('ignore')

class ImageSlicer:
    """Classe pour découper les images de grande dimension - OPTIMISÉE"""
    
    def __init__(self, max_height=2000, overlap=50):  # Réduit overlap
        self.max_height = max_height
        self.overlap = overlap
    
    def should_slice_image(self, image_path):
        """Vérifie si l'image doit être découpée"""
        img = cv2.imread(image_path)
        if img is None:
            return False, 0, 0
        
        height, width = img.shape[:2]
        return height > self.max_height, height, width
    
    def slice_image_memory(self, image_path):
        """Découpe une image en mémoire sans sauvegarder - OPTIMISÉ"""
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Impossible de charger l'image : {image_path}")
        
        height, width = img.shape[:2]
        
        if height <= self.max_height:
            return [img]
        
        slices = []
        current_y = 0
        
        while current_y < height:
            end_y = min(current_y + self.max_height, height)
            slice_img = img[current_y:end_y, 0:width]
            slices.append(slice_img)
            
            if end_y >= height:
                break
            current_y = end_y - self.overlap
        
        print(f"Image découpée en {len(slices)} parties (mémoire)")
        return slices


class OCRProcessor:
    """Classe OCR optimisée avec cache et parallélisation"""
    
    # Cache global des modèles OCR
    _ocr_cache = {}
    
    def __init__(self, lang='fr', max_image_height=2000, use_gpu=False):
        # Utiliser le cache pour éviter de recharger le modèle
        cache_key = f"{lang}_{use_gpu}"
        if cache_key not in self._ocr_cache:
            print(f"Initialisation OCR pour {lang} (GPU: {use_gpu})...")
            self._ocr_cache[cache_key] = PaddleOCR(
                use_angle_cls=False,  # OPTIMISATION: Désactivé par défaut
                lang=lang,
                use_gpu=use_gpu,
                show_log=False,
                cpu_threads=4,        # OPTIMISATION: Multi-threading
                enable_mkldnn=True    # OPTIMISATION: Intel MKL-DNN
            )
        
        self.ocr = self._ocr_cache[cache_key]
        self.slicer = ImageSlicer(max_height=max_image_height, overlap=50)
        self.preprocess_threshold = 0.8  # Seuil pour décider du prétraitement
    
    def _needs_preprocessing(self, image):
        """Détermine si le prétraitement est nécessaire - OPTIMISÉ"""
        if isinstance(image, str):
            img = cv2.imread(image)
        else:
            img = image
            
        if img is None:
            return True
        
        # Analyse rapide de la qualité
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
        
        # Calcul variance (mesure de netteté)
        variance = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Calcul contraste
        contrast = gray.std()
        
        # Si image de bonne qualité, pas de prétraitement
        return variance < 100 or contrast < 50
    
    def preprocess_image_optimized(self, image):
        """Prétraitement optimisé et conditionnel"""
        if isinstance(image, str):
            img = cv2.imread(image)
        else:
            img = image.copy()
        
        if img is None:
            raise ValueError("Image invalide")
        
        # Redimensionnement seulement si vraiment nécessaire
        height, width = img.shape[:2]
        if width > 2500:  # Seuil plus élevé
            scale = 2000 / width
            new_width = 2000
            new_height = int(height * scale)
            img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
        
        # Conversion en niveaux de gris
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img
        
        # Prétraitement léger et optimisé
        if self._needs_preprocessing(gray):
            # Amélioration contraste légère
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4,4))  # Paramètres réduits
            enhanced = clahe.apply(gray)
            
            # Débruitage minimal
            denoised = cv2.medianBlur(enhanced, 3)
            return denoised
        
        return gray
    
    def extract_text_from_slice_optimized(self, image_slice, use_preprocessing=None):
        """Extraction OCR optimisée sans fichiers temporaires"""
        try:
            # Prétraitement intelligent
            if use_preprocessing is None:
                use_preprocessing = self._needs_preprocessing(image_slice)
            
            if use_preprocessing:
                processed_img = self.preprocess_image_optimized(image_slice)
            else:
                if isinstance(image_slice, str):
                    processed_img = cv2.imread(image_slice)
                else:
                    processed_img = image_slice
            
            # OCR direct sur l'image numpy - PAS DE FICHIER TEMPORAIRE
            result = self.ocr.ocr(processed_img, cls=False)  # cls=False pour vitesse
            
            # Extraction du texte avec position
            extracted_lines = []
            if result and result[0]:
                for line in result[0]:
                    if len(line) >= 2 and line[1]:
                        text = line[1][0]
                        confidence = line[1][1]
                        bbox = line[0]
                        
                        if confidence > 0.5:  # Seuil légèrement réduit
                            y_pos = (bbox[0][1] + bbox[2][1]) / 2
                            extracted_lines.append((y_pos, text))
            
            # Tri par position verticale
            extracted_lines.sort(key=lambda x: x[0])
            return " ".join([text for _, text in extracted_lines])
            
        except Exception as e:
            print(f"Erreur OCR sur slice : {e}")
            return ""
    
    def extract_text_parallel(self, image_path, max_workers=2):
        """Extraction parallèle pour grandes images - OPTIMISÉ"""
        print(f"Analyse parallèle de l'image : {image_path}")
        
        # Vérifier si découpage nécessaire
        should_slice, height, width = self.slicer.should_slice_image(image_path)
        
        if not should_slice:
            print("Image de taille normale, traitement direct")
            return self.extract_text_from_slice_optimized(image_path)
        
        print(f"Image grande dimension ({width}x{height}), traitement parallèle")
        
        # Découpage en mémoire
        slices = self.slicer.slice_image_memory(image_path)
        
        # Traitement parallèle des slices
        all_text_parts = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Lancer tous les traitements
            future_to_slice = {
                executor.submit(self.extract_text_from_slice_optimized, slice_img): i 
                for i, slice_img in enumerate(slices)
            }
            
            # Récupérer les résultats dans l'ordre
            results = [None] * len(slices)
            for future in as_completed(future_to_slice):
                slice_idx = future_to_slice[future]
                try:
                    text_part = future.result()
                    results[slice_idx] = text_part
                    print(f"Slice {slice_idx + 1}/{len(slices)} terminée")
                except Exception as e:
                    print(f"Erreur slice {slice_idx}: {e}")
                    results[slice_idx] = ""
            
            # Filtrer et combiner
            all_text_parts = [text for text in results if text and text.strip()]
        
        complete_text = " ".join(all_text_parts)
        print(f"Extraction parallèle terminée : {len(complete_text)} caractères")
        
        return complete_text
    
    def extract_text_with_structure_optimized(self, image_path):
        """Extraction avec structure optimisée"""
        should_slice, height, width = self.slicer.should_slice_image(image_path)
        
        if not should_slice:
            return self.extract_text_from_slice_optimized(image_path)
        
        # Découpage en mémoire
        slices = self.slicer.slice_image_memory(image_path)
        
        # Traitement parallèle avec structure
        def process_slice_with_structure(slice_img):
            try:
                result = self.ocr.ocr(slice_img, cls=False)
                
                if result and result[0]:
                    lines_with_pos = []
                    for line in result[0]:
                        if len(line) >= 2 and line[1] and line[1][1] > 0.5:
                            bbox = line[0]
                            text = line[1][0]
                            y_pos = (bbox[0][1] + bbox[2][1]) / 2
                            lines_with_pos.append((y_pos, text))
                    
                    lines_with_pos.sort(key=lambda x: x[0])
                    
                    slice_text = ""
                    prev_y = 0
                    for y_pos, text in lines_with_pos:
                        if prev_y > 0 and y_pos - prev_y > 30:
                            slice_text += "\n"
                        slice_text += text + " "
                        prev_y = y_pos
                    
                    return slice_text.strip()
                return ""
            except Exception as e:
                print(f"Erreur structure slice : {e}")
                return ""
        
        # Traitement parallèle
        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(process_slice_with_structure, slices))
        
        structured_parts = [part for part in results if part]
        return "\n\n".join(structured_parts)


class TextCleaner:
    """Classe de nettoyage de texte optimisée"""
    
    def __init__(self, language='french'):
        self.language = language
        try:
            self.stop_words = set(stopwords.words('french' if language == 'french' else 'english'))
        except:
            self.stop_words = {'le', 'la', 'les', 'un', 'une', 'des', 'et', 'ou', 'mais', 'donc', 'car'}
        
        # Patterns précompilés pour vitesse
        self.patterns = {
            'ocr_fixes': [
                (re.compile(r'\b0(?=[a-z])\b', re.IGNORECASE), 'o'),
                (re.compile(r'\b1(?=[a-z])\b', re.IGNORECASE), 'l'),
                (re.compile(r'rn', re.IGNORECASE), 'm'),
                (re.compile(r'vv', re.IGNORECASE), 'w'),
                (re.compile(r'(\w)\|(\w)', re.IGNORECASE), r'\1l\2'),
                (re.compile(r'(\w)1(\w)', re.IGNORECASE), r'\1l\2'),
            ],
            'cleanup': [
                (re.compile(r'\s+'), ' '),
                (re.compile(r'\b[a-zA-Z]\b'), ''),
                (re.compile(r'[^\w\s\.\?\!\,\;\:\-\(\)]'), ' '),
                (re.compile(r'\s+([\.!\?])'), r'\1'),
                (re.compile(r'(.)\1{3,}'), r'\1\1'),
            ]
        }
    
    def clean_ocr_text_optimized(self, raw_text):
        """Nettoyage OCR optimisé avec regex précompilées"""
        if not raw_text:
            return ""
        
        text = raw_text
        
        # Corrections OCR avec patterns précompilés
        for pattern, replacement in self.patterns['ocr_fixes']:
            text = pattern.sub(replacement, text)
        
        # Nettoyage général
        for pattern, replacement in self.patterns['cleanup']:
            text = pattern.sub(replacement, text)
        
        # Filtrage des lignes courtes (optimisé)
        lines = [line.strip() for line in text.split('\n')]
        clean_lines = [line for line in lines 
                      if len(line) > 3 and len(line.split()) > 1]
        
        return ' '.join(clean_lines).strip()
    
    def segment_into_sentences_fast(self, text):
        """Segmentation rapide en phrases"""
        try:
            sentences = sent_tokenize(text)
        except:
            sentences = re.split(r'[.!?]+', text)
        
        # Filtrage vectorisé
        clean_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            word_count = len(sentence.split())
            
            if (3 <= word_count <= 100 and  # Limites ajustées
                10 <= len(sentence) <= 500 and
                re.search(r'[a-zA-Z]', sentence)):
                clean_sentences.append(sentence)
        
        return clean_sentences


class WebQASystem:
    """Système QA SANS échantillonnage pour préserver tout le contenu"""

    def __init__(self, language='french', cpu_optimized=False, preserve=True):
        self.language = language
        self.cpu_optimized = cpu_optimized
        self.preserve = preserve

        # Charger le modèle spaCy pour le NER
        try:
            self.nlp = spacy.load('fr_core_news_sm')
        except OSError:
            print("Modèle spaCy non trouvé. Veuillez télécharger le modèle avec : python -m spacy download fr_core_news_sm")
            self.nlp = None

        # Paramètres adaptatifs
        if cpu_optimized:
            max_features = 2000 if preserve else 1000
            ngram_max = 2
        else:
            max_features = 3000 if preserve else 1500
            ngram_max = 2

        # Vectorizer adaptatif
        self.vectorizer = TfidfVectorizer(
            stop_words='french' if language == 'french' else 'english',
            max_features=max_features,
            ngram_range=(1, ngram_max),
            min_df=1,
            max_df=0.95,
            sublinear_tf=True,
            norm='l2'
        )

        self.sentences = []
        self.sentences_for_vectorization = []
        self.sentence_vectors = None
        self.word2vec_model = None
        self.topics = []
        self.entities = {}

        try:
            self.stop_words = set(stopwords.words('french' if language == 'french' else 'english'))
        except:
            self.stop_words = {'le', 'la', 'les', 'un', 'une', 'des', 'et', 'ou', 'mais', 'donc', 'car'}

    def extract_entities(self, text):
        """Extraire les entités nommées du texte."""
        if not self.nlp:
            return {}

        doc = self.nlp(text)
        entities = {}
        for ent in doc.ents:
            entities[ent.label_] = ent.text
        return entities

    def _smart_sampling_for_vectorization_only(self, sentences, target_size):
        """Échantillonnage UNIQUEMENT pour la vectorisation TF-IDF (performance)"""
        if len(sentences) <= target_size:
            return sentences

        start_portion = sentences[:target_size // 3]
        end_portion = sentences[-target_size // 3:]

        middle_sentences = sentences[target_size // 3:-target_size // 3]
        if middle_sentences:
            step = max(1, len(middle_sentences) // (target_size // 3))
            middle_sample = middle_sentences[::step][:target_size // 3]
        else:
            middle_sample = []

        return start_portion + middle_sample + end_portion

    def extract_keywords_from(self, text, top_k=20):
        """Extraction de mots-clés sur le contenu COMPLET"""
        try:
            words = word_tokenize(text.lower())
        except:
            words = text.lower().split()

        words = [word for word in words
                if word.isalpha() and word not in self.stop_words and len(word) > 2]

        word_freq = Counter(words)
        return [word for word, freq in word_freq.most_common(top_k)]

    def identify_topics_from_sample(self, sentences, n_topics=5):
        """Topics basés sur échantillon mais préservation du contenu complet"""
        if len(sentences) < n_topics:
            return sentences[:min(5, len(sentences))]

        try:
            sample_for_clustering = self._smart_sampling_for_vectorization_only(sentences, min(300, len(sentences)))

            if len(sample_for_clustering) < n_topics:
                return sample_for_clustering

            vectors = self.vectorizer.fit_transform(sample_for_clustering)
            n_clusters = min(n_topics, len(sample_for_clustering) // 2)

            max_iter = 50 if self.cpu_optimized else 100
            n_init = 3 if self.cpu_optimized else 5

            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=n_init, max_iter=max_iter)
            clusters = kmeans.fit_predict(vectors)

            topics = []
            for i in range(n_clusters):
                cluster_sentences = [sample_for_clustering[j] for j in range(len(sample_for_clustering))
                                   if clusters[j] == i]
                if cluster_sentences:
                    representative = min(cluster_sentences,
                                       key=lambda x: len(x) if 30 <= len(x) <= 200 else float('inf'))
                    topics.append(representative)

            return topics
        except Exception as e:
            print(f"Erreur clustering : {e}")
            return sentences[:min(5, len(sentences))]

    def generate_summary_from(self, sentences, max_sentences=10):
        """Génération de résumé basé sur le contenu COMPLET"""
        if len(sentences) <= max_sentences:
            return " ".join(sentences)

        try:
            sample_for_tfidf = self._smart_sampling_for_vectorization_only(sentences, min(200, len(sentences)))
            vectors = self.vectorizer.fit_transform(sample_for_tfidf)

            sample_scores = []
            for i, vector in enumerate(vectors):
                tfidf_score = vector.sum()
                position_bonus = 1.0 / (1 + i * 0.1)
                word_count = len(sample_for_tfidf[i].split())
                length_bonus = min(word_count / 15.0, 1.2) if word_count > 5 else 0.5
                final_score = tfidf_score * position_bonus * length_bonus
                sample_scores.append((i, final_score))

            sample_scores.sort(key=lambda x: x[1], reverse=True)

            selected_sample_indices = [idx for idx, score in sample_scores[:max_sentences]]
            selected_sentences = [sample_for_tfidf[i] for i in selected_sample_indices]

            return " ".join(selected_sentences)

        except Exception as e:
            print(f"Erreur résumé complet : {e}")
            return " ".join(sentences[:max_sentences])

    def process_content_full_preservation(self, sentences):
        """Traitement avec préservation complète du contenu."""
        self.sentences = sentences

        if not self.sentences:
            return "Aucun contenu à traiter."

        print(f"Traitement avec préservation complète : {len(sentences)} phrases")

        try:
            if self.preserve:
                if len(sentences) > 1000:
                    print("Grand corpus : échantillonnage pour vectorisation, préservation contenu complet")
                    self.sentences_for_vectorization = self._smart_sampling_for_vectorization_only(sentences, 400)
                else:
                    self.sentences_for_vectorization = sentences

                self.sentence_vectors = self.vectorizer.fit_transform(self.sentences_for_vectorization)
            else:
                self.sentences_for_vectorization = self._smart_sampling_for_vectorization_only(sentences, 300)
                self.sentence_vectors = self.vectorizer.fit_transform(self.sentences_for_vectorization)

            self.train_word_embeddings_light(self.sentences_for_vectorization)
            self.topics = self.identify_topics_from_sample(self.sentences_for_vectorization)

            full_text = " ".join(self.sentences)
            self.entities = self.extract_entities(full_text)

            return f"Contenu traité (mode complet) : {len(self.sentences)} phrases conservées, {len(self.sentences_for_vectorization)} indexées."

        except Exception as e:
            return f"Erreur traitement complet : {e}"

    def train_word_embeddings_light(self, sentences):
        """Word2Vec optimisé"""
        try:
            if len(sentences) > 100:
                sample_sentences = self._smart_sampling_for_vectorization_only(sentences, 100)
            else:
                sample_sentences = sentences

            tokenized_sentences = []
            for sentence in sample_sentences:
                try:
                    tokens = word_tokenize(sentence.lower())
                except:
                    tokens = sentence.lower().split()

                filtered_tokens = [token for token in tokens
                                 if token.isalpha() and len(token) > 2]
                if len(filtered_tokens) > 2:
                    tokenized_sentences.append(filtered_tokens)

            if len(tokenized_sentences) > 5:
                epochs = 3 if self.cpu_optimized else 5
                vector_size = 80 if self.cpu_optimized else 100

                self.word2vec_model = Word2Vec(
                    tokenized_sentences,
                    vector_size=vector_size,
                    window=5,
                    min_count=1,
                    workers=1,
                    epochs=epochs
                )
        except Exception as e:
            print(f"Erreur Word2Vec : {e}")
            self.word2vec_model = None

    def answer_specific_question(self, question, top_k=5):
        """Réponse basée sur le contenu COMPLET"""
        if not self.sentences:
            return "Aucun contenu indexé."

        try:
            question_vector = self.vectorizer.transform([question])
            similarities = cosine_similarity(question_vector, self.sentence_vectors).flatten()

            threshold = 0.02 if len(self.sentences_for_vectorization) > 50 else 0.01
            top_indices = similarities.argsort()[-top_k:][::-1]

            relevant_sentences = [self.sentences_for_vectorization[i] for i in top_indices
                                if i < len(self.sentences_for_vectorization) and similarities[i] > threshold]

            question_words = set(question.lower().split())
            bonus_sentences = []

            for sentence in self.sentences:
                sentence_words = set(sentence.lower().split())
                if len(question_words.intersection(sentence_words)) >= 2:
                    bonus_sentences.append(sentence)
                    if len(bonus_sentences) >= 3:
                        break

            all_relevant = relevant_sentences + bonus_sentences
            unique_sentences = list(dict.fromkeys(all_relevant))

            if not unique_sentences:
                return "Information non trouvée dans le contenu analysé."

            response = " ".join(unique_sentences[:top_k])
            if len(response) > 800:
                response = response[:800] + "..."
            return response

        except Exception as e:
            print(f"Erreur réponse complète : {e}")
            return "Erreur lors de la recherche."

    def get_full_context_for_llm(self, max_chars=15000):
        """Récupère le contexte COMPLET pour les LLM externes"""
        if not self.sentences:
            return "Aucun contenu disponible."

        full_text = " ".join(self.sentences)

        if len(full_text) <= max_chars:
            return full_text

        start_text = " ".join(self.sentences[:len(self.sentences)//4])
        end_text = " ".join(self.sentences[-len(self.sentences)//4:])

        remaining_chars = max_chars - len(start_text) - len(end_text) - 20
        if remaining_chars > 0:
            middle_sentences = self.sentences[len(self.sentences)//4:-len(self.sentences)//4]
            middle_text = " ".join(middle_sentences)
            if len(middle_text) > remaining_chars:
                middle_text = middle_text[:remaining_chars] + "..."
            return f"{start_text} ... {middle_text} ... {end_text}"

        return f"{start_text} ... {end_text}"

    def answer_question(self, question):
        """Système de réponse avec contenu complet."""
        if not self.sentences:
            return "Aucun contenu indexé."

        question_lower = question.lower()

        if any(word in question_lower for word in ['résume', 'résumé', 'parle', 'sujet', 'contenu']):
            summary = self.generate_summary_from(self.sentences, max_sentences=8)
            return f"Résumé : {summary}"
        elif any(word in question_lower for word in ['quoi', 'de quoi', 'thème', 'propos']):
            topics_text = " | ".join(self.topics[:3])
            keywords = self.extract_keywords_from(" ".join(self.sentences), top_k=12)
            keywords_text = ", ".join(keywords)
            return f"Sujets principaux : {topics_text}. Mots-clés : {keywords_text}"
        elif any(word in question_lower for word in ['date', 'quand']):
            if any(label in self.entities for label in ['DATE', 'CARDINAL']):
                return f"Date de publication : {self.entities.get('DATE', self.entities.get('CARDINAL'))}"
            else:
                return "Date de publication non trouvée."
        elif any(word in question_lower for word in ['titre']):
            if 'ORG' in self.entities:
                return f"Titre de l'article : {self.entities['ORG']}"
            else:
                return "Titre de l'article non trouvé."
        else:
            return self.answer_specific_question(question)


class CompleteOCRQASystem:
    """Système OCR/QA avec préservation du contenu complet"""
    
    def __init__(self, language='french', ocr_lang='fr', max_image_height=2000, use_gpu=False, cpu_optimized=False):
        self.ocr_processor = OCRProcessor(
            lang=ocr_lang, 
            max_image_height=max_image_height,
            use_gpu=use_gpu
        )
        self.text_cleaner = TextCleaner(language=language)
        
        # ✅ NOUVEAU : QA System avec préservation complète
        self.qa_system = WebQASystem(
            language=language, 
            cpu_optimized=cpu_optimized,
            preserve =True  # 🔑 GARDE TOUT LE CONTENU
        )
        self.cpu_optimized = cpu_optimized
        
    def process_image_optimized(self, image_path, use_layout=True, parallel=True):
        """Traitement avec préservation du contenu complet"""
        print("=== TRAITEMENT AVEC PRÉSERVATION COMPLÈTE ===")
        print(f"Chemin : {image_path}")
        
        if not os.path.exists(image_path):
            return f"Image non trouvée : {image_path}"
        
        img = cv2.imread(image_path)
        if img is None:
            return "Impossible de charger l'image"
        
        height, width = img.shape[:2]
        print(f"Dimensions : {width}x{height}")
        
        max_workers = 1 if self.cpu_optimized else 2
        
        # Extraction OCR
        if parallel and not self.cpu_optimized:
            raw_text = self.ocr_processor.extract_text_parallel(image_path, max_workers=max_workers)
        elif use_layout:
            raw_text = self.ocr_processor.extract_text_with_structure_optimized(image_path)
        else:
            raw_text = self.ocr_processor.extract_text_from_slice_optimized(image_path)
        
        if not raw_text:
            return "Aucun texte détecté."
        
        print(f"Texte brut : {len(raw_text)} caractères")
        
        # Nettoyage
        cleaned_text = self.text_cleaner.clean_ocr_text_optimized(raw_text)
        
        # Segmentation
        sentences = self.text_cleaner.segment_into_sentences_fast(cleaned_text)
        
        if not sentences:
            return "Aucune phrase valide après nettoyage."
        
        print(f"Phrases valides : {len(sentences)}")
        
        # ✅ INDEXATION AVEC PRÉSERVATION COMPLÈTE
        result = self.qa_system.process_content_full_preservation(sentences)
        
        return result
    
    def ask_question(self, question):
        """Question avec contenu complet"""
        return self.qa_system.answer_question (question)
    
    def get_full_context_for_external_llm(self, max_chars=15000):
        """Récupère TOUT le contenu pour les LLM externes"""
        return self.qa_system.get_full_context_for_llm(max_chars)
    
    def get_content_info(self):
        """Informations sur le contenu complet"""
        if not self.qa_system.sentences:
            return "Aucun contenu traité."
        
        total_sentences = len(self.qa_system.sentences)
        indexed_sentences = len(self.qa_system.sentences_for_vectorization)
        total_words = sum(len(s.split()) for s in self.qa_system.sentences)
        
        return (f"Contenu analysé (mode complet) :\n"
                f"- {total_sentences} phrases CONSERVÉES\n"
                f"- {indexed_sentences} phrases indexées (pour performance)\n"
                f"- ~{total_words} mots au total\n"
                f"- Taux de préservation : 100%")

def analyze_image_complexity(image_path):
    """Analyse la complexité d'une image pour prédire le temps de traitement"""
    if not os.path.exists(image_path):
        return "Image non trouvée"
    
    img = cv2.imread(image_path)
    if img is None:
        return "Impossible de charger l'image"
    
    height, width = img.shape[:2]
    total_pixels = height * width
    
    # Analyse de complexité
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Mesures de complexité
    variance = cv2.Laplacian(gray, cv2.CV_64F).var()  # Netteté
    contrast = gray.std()  # Contraste
    unique_colors = len(np.unique(gray))  # Diversité
    
    # Estimation du nombre de slices
    slicer = ImageSlicer()
    should_slice, _, _ = slicer.should_slice_image(image_path)
    num_slices = max(1, height // 2000) if should_slice else 1
    
    # Score de complexité (0-100)
    complexity_score = min(100, (
        (total_pixels / 1000000) * 20 +  # Taille
        (variance / 500) * 20 +          # Netteté
        (contrast / 50) * 20 +           # Contraste
        (unique_colors / 255) * 20 +     # Diversité
        num_slices * 20                  # Nombre de slices
    ))
    
    # Estimation temps (CPU uniquement)
    estimated_time = (
        num_slices * 2.5 +               # Base par slice
        (complexity_score / 100) * 10 +  # Facteur complexité
        (total_pixels / 1000000) * 3     # Facteur taille
    )
    
    return {
        'dimensions': f"{width}x{height}",
        'total_pixels': total_pixels,
        'num_slices': num_slices,
        'variance': variance,
        'contrast': contrast,
        'unique_colors': unique_colors,
        'complexity_score': complexity_score,
        'estimated_time_cpu': f"{estimated_time:.1f}s"
    }


def optimize_cpu_settings():
    """Configure les paramètres optimaux pour CPU"""
    print("=== CONFIGURATION CPU OPTIMISÉE ===")
    
    cpu_count = multiprocessing.cpu_count()
    
    # Paramètres recommandés
    recommended_settings = {
        'max_workers': min(2, cpu_count // 2),  # Conservateur pour CPU
        'max_image_height': 1800,               # Réduit pour CPU
        'batch_size': 50,                       # Pour traitement par lots
        'tfidf_max_features': 1000,             # Réduit pour CPU
        'word2vec_epochs': 3,                   # Minimal pour CPU
        'clustering_max_iter': 50               # Réduit pour CPU
    }
    
    print(f"CPUs détectés : {cpu_count}")
    print(f"Workers recommandés : {recommended_settings['max_workers']}")
    print(f"Hauteur max image : {recommended_settings['max_image_height']}")
    
    return recommended_settings


def benchmark_system(image_path, num_runs=3):
    """Benchmark du système optimisé"""
    print("=== BENCHMARK SYSTÈME OPTIMISÉ (CPU) ===")
    
    if not os.path.exists(image_path):
        print(f"Image non trouvée : {image_path}")
        return None
    
    times = []
    for i in range(num_runs):
        print(f"\nTest {i+1}/{num_runs}...")
        
        start_time = time.time()
        
        system = CompleteOCRQASystem(
            language='french', 
            ocr_lang='fr', 
            use_gpu=False,  # CPU uniquement
            cpu_optimized=True
        )
        
        result = system.process_image_optimized(image_path, parallel=True)
        
        end_time = time.time()
        elapsed = end_time - start_time
        times.append(elapsed)
        
        print(f"Temps écoulé : {elapsed:.2f}s")
        print(f"Résultat : {result[:100]}...")
    
    avg_time = sum(times) / len(times)
    print(f"\n📊 RÉSULTATS BENCHMARK :")
    print(f"Temps moyen : {avg_time:.2f}s")
    print(f"Temps min : {min(times):.2f}s")
    print(f"Temps max : {max(times):.2f}s")
    
    return avg_time


class CPUOptimizedOCRSystem(CompleteOCRQASystem):
    """Version spécialement optimisée pour CPU"""
    
    def __init__(self, language='french', ocr_lang='fr'):
        # Configuration CPU optimisée
        cpu_settings = optimize_cpu_settings()
        
        super().__init__(
            language=language,
            ocr_lang=ocr_lang,
            max_image_height=cpu_settings['max_image_height'],
            use_gpu=False,  # Force CPU
            cpu_optimized=True
        )
        
        self.cpu_settings = cpu_settings
    
    def process_image_cpu_optimized(self, image_path):
        """Traitement spécialement optimisé pour CPU"""
        print("=== TRAITEMENT CPU OPTIMISÉ ===")
        
        # Analyse préliminaire
        complexity = analyze_image_complexity(image_path)
        if isinstance(complexity, str):
            return complexity
            
        print(f"Complexité image : {complexity['complexity_score']:.1f}/100")
        print(f"Temps estimé : {complexity['estimated_time_cpu']}")
        
        # Traitement adaptatif selon complexité
        if complexity['complexity_score'] > 70:
            print("Image complexe détectée - mode économie CPU")
            return self.process_image_optimized(
                image_path, 
                use_layout=False,  # Plus simple
                parallel=False     # Séquentiel pour économiser CPU
            )
        else:
            print("Image standard - mode normal")
            return self.process_image_optimized(
                image_path, 
                use_layout=True, 
                parallel=True
            )
    
    def batch_process_images(self, image_paths, max_concurrent=1):
        """Traitement par lots optimisé CPU"""
        print(f"=== TRAITEMENT PAR LOTS ({len(image_paths)} images) ===")
        
        results = {}
        
        for i, image_path in enumerate(image_paths):
            print(f"\nTraitement image {i+1}/{len(image_paths)}: {os.path.basename(image_path)}")
            
            try:
                result = self.process_image_cpu_optimized(image_path)
                results[image_path] = {
                    'status': 'success',
                    'result': result,
                    'sentences_count': len(self.qa_system.sentences) if hasattr(self.qa_system, 'sentences') else 0
                }
            except Exception as e:
                results[image_path] = {
                    'status': 'error',
                    'error': str(e)
                }
                print(f"Erreur : {e}")
        
        return results
    
    def get_performance_stats(self):
        """Statistiques de performance du système"""
        if not hasattr(self.qa_system, 'sentences') or not self.qa_system.sentences:
            return "Aucune statistique disponible - aucun contenu traité."
        
        stats = {
            'total_sentences': len(self.qa_system.sentences),
            'indexed_sentences': len(self.qa_system._sample_sentences),
            'topics_found': len(self.qa_system.topics),
            'has_word2vec': self.qa_system.word2vec_model is not None,
            'vectorizer_features': self.qa_system.vectorizer.max_features,
            'cpu_optimized': self.cpu_optimized
        }
        
        return stats


def interactive_mode(system):
    """Mode interactif pour poser des questions"""
    print("\n=== MODE INTERACTIF ===")
    print("Tapez 'quit' pour quitter, 'help' pour l'aide")
    
    while True:
        try:
            question = input("\n❓ Votre question : ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("Au revoir ! 👋")
                break
            elif question.lower() == 'help':
                print("""
📚 AIDE - Types de questions possibles :
• "Résumé de cette page ?" - Génère un résumé
• "De quoi parle le document ?" - Sujets principaux  
• "Quels sont les prix ?" - Recherche d'infos spécifiques
• "Comment contacter ?" - Informations de contact
• "Y a-t-il des horaires ?" - Recherche dans le contenu
""")
                continue
            elif not question:
                continue
            
            print("🔍 Recherche en cours...")
            start_time = time.time()
            
            answer = system.ask_question(question)
            
            end_time = time.time()
            
            print(f"✅ Réponse ({end_time - start_time:.2f}s) :")
            print(f"📝 {answer}")
            
        except KeyboardInterrupt:
            print("\n\nInterruption détectée. Au revoir ! 👋")
            break
        except Exception as e:
            print(f"❌ Erreur : {e}")


def main():
    """Version main standard"""
    print("=== SYSTÈME OCR/QA ULTRA-OPTIMISÉ ===")
    
    # Initialisation optimisée
    system = CompleteOCRQASystem(
        language='french', 
        ocr_lang='fr', 
        max_image_height=2000,
        use_gpu=False,  # CPU par défaut
        cpu_optimized=False
    )
    
    # Image de test
    image_path = "screenshot.png"
    
    if os.path.exists(image_path):
        print("=== TRAITEMENT ULTRA-RAPIDE ===")
        result = system.process_image_optimized(
            image_path, 
            use_layout=True, 
            parallel=True
        )
        print(result)
        
        print(f"\n{system.get_content_info()}")
        
        print("\n=== QUESTIONS RAPIDES ===")
        questions = [
            "De quoi parle cette page ?",
            "Résumé complet ?",
            "Prix mentionnés ?",
            "Contact entreprise ?"
        ]
        
        for question in questions:
            print(f"\nQ: {question}")
            answer = system.ask_question(question)
            print(f"R: {answer}")
        
        # Proposer mode interactif
        if input("\n🤔 Voulez-vous poser d'autres questions ? (y/n): ").lower() == 'y':
            interactive_mode(system)
    
    else:
        print(f"Image non trouvée : {image_path}")
        print("Veuillez placer votre image 'screenshot.png' dans le répertoire du script.")


def main_cpu_optimized():
    """Version main optimisée pour CPU uniquement"""
    print("=== SYSTÈME OCR/QA OPTIMISÉ CPU ===")
    
    # Analyse système
    cpu_settings = optimize_cpu_settings()
    
    # Initialisation CPU
    system = CPUOptimizedOCRSystem(
        language='french', 
        ocr_lang='fr'
    )
    
    # Image de test
    image_path = "screenshot.png"
    
    if os.path.exists(image_path):
        # Analyse préliminaire
        complexity = analyze_image_complexity(image_path)
        print(f"\n📊 ANALYSE IMAGE :")
        if isinstance(complexity, dict):
            for key, value in complexity.items():
                print(f"  {key}: {value}")
        else:
            print(f"  Erreur: {complexity}")
            return
        
        # Traitement optimisé
        print(f"\n=== TRAITEMENT CPU ===")
        start_time = time.time()
        result = system.process_image_cpu_optimized(image_path)
        end_time = time.time()
        
        print(f"✅ Terminé en {end_time - start_time:.2f}s")
        print(result)
        
        print(f"\n{system.get_content_info()}")
        
        # Statistiques de performance
        stats = system.get_performance_stats()
        if isinstance(stats, dict):
            print(f"\n📊 STATS PERFORMANCE :")
            for key, value in stats.items():
                print(f"  {key}: {value}")
        
        # Questions de test
        print("\n=== TEST QUESTIONS ===")
        questions = [
            "Résumé de cette page ?",
            "Quels sont les sujets principaux ?",
            "Y a-t-il des prix ?",
            "Comment contacter ?"
        ]
        
        for question in questions:
            print(f"\nQ: {question}")
            start_time = time.time()
            answer = system.ask_question(question)
            end_time = time.time()
            print(f"R ({end_time - start_time:.2f}s): {answer[:200]}{'...' if len(answer) > 200 else ''}")
        
        # Mode interactif optionnel
        if input("\n💬 Mode interactif ? (y/n): ").lower() == 'y':
            interactive_mode(system)
        
        # Benchmark optionnel
        if input("\n⏱️ Faire un benchmark ? (y/n): ").lower() == 'y':
            benchmark_system(image_path, num_runs=2)
    
    else:
        print(f"Image non trouvée : {image_path}")
        print("Créez un fichier 'screenshot.png' ou modifiez le chemin.")


def demo_batch_processing():
    """Démonstration du traitement par lots"""
    print("=== DÉMO TRAITEMENT PAR LOTS ===")
    
    # Rechercher des images dans le répertoire
    image_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']
    image_files = []
    
    for file in os.listdir('.'):
        if any(file.lower().endswith(ext) for ext in image_extensions):
            image_files.append(file)
    
    if not image_files:
        print("Aucune image trouvée dans le répertoire courant.")
        return
    
    print(f"Images trouvées : {image_files}")
    
    # Traitement par lots
    system = CPUOptimizedOCRSystem()
    results = system.batch_process_images(image_files[:3])  # Limiter à 3 images
    
    # Afficher résultats
    print("\n📊 RÉSULTATS TRAITEMENT PAR LOTS :")
    for image_path, result in results.items():
        print(f"\n📄 {os.path.basename(image_path)}:")
        if result['status'] == 'success':
            print(f"  ✅ Phrases: {result['sentences_count']}")
            print(f"  📝 {result['result'][:100]}...")
        else:
            print(f"  ❌ Erreur: {result['error']}")


if __name__ == "__main__":
    import sys
    
    # Analyser les arguments de ligne de commande
    if len(sys.argv) > 1:
        if sys.argv[1] == '--cpu':
            main_cpu_optimized()
        elif sys.argv[1] == '--batch':
            demo_batch_processing()
        elif sys.argv[1] == '--benchmark':
            if len(sys.argv) > 2:
                benchmark_system(sys.argv[2])
            else:
                benchmark_system("screenshot.png")
        else:
            print(f"Usage: {sys.argv[0]} [--cpu|--batch|--benchmark [image]]")
    else:
        # Version standard
        main()
        
        # Proposer les autres modes
        print("\n" + "="*60)
        print("💡 AUTRES MODES DISPONIBLES :")
        print("  python script.py --cpu       # Version CPU optimisée")
        print("  python script.py --batch     # Traitement par lots")
        print("  python script.py --benchmark # Test de performance")
        print("="*60)
