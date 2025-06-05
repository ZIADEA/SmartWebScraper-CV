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
import warnings
warnings.filterwarnings('ignore')

class ImageSlicer:
    """Classe pour découper les images de grande dimension"""
    
    def __init__(self, max_height=2000, overlap=100):
        """
        Args:
            max_height: hauteur maximale d'une slice
            overlap: chevauchement entre les slices (en pixels)
        """
        self.max_height = max_height
        self.overlap = overlap
    
    def should_slice_image(self, image_path):
        """Vérifie si l'image doit être découpée"""
        img = cv2.imread(image_path)
        if img is None:
            return False, 0, 0
        
        height, width = img.shape[:2]
        return height > self.max_height, height, width
    
    def slice_image(self, image_path, save_slices=True):
        """
        Découpe une image en plusieurs parties
        Args:
            image_path: chemin vers l'image
            save_slices: sauvegarder les slices sur disque
        Returns:
            liste des chemins des slices ou des images numpy
        """
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Impossible de charger l'image : {image_path}")
        
        height, width = img.shape[:2]
        
        if height <= self.max_height:
            return [image_path] if save_slices else [img]
        
        slices = []
        slice_paths = []
        current_y = 0
        slice_num = 0
        
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        
        while current_y < height:
            # Calculer la fin de la slice
            end_y = min(current_y + self.max_height, height)
            
            # Extraire la slice
            slice_img = img[current_y:end_y, 0:width]
            
            if save_slices:
                # Sauvegarder la slice
                slice_filename = f"{base_name}_slice_{slice_num:03d}.png"
                slice_path = os.path.join(os.path.dirname(image_path), slice_filename)
                cv2.imwrite(slice_path, slice_img)
                slice_paths.append(slice_path)
            else:
                slices.append(slice_img)
            
            slice_num += 1
            
            # Calculer la position suivante avec chevauchement
            if end_y >= height:
                break
            current_y = end_y - self.overlap
        
        print(f"Image découpée en {slice_num} parties")
        return slice_paths if save_slices else slices
    
    def clean_slice_files(self, slice_paths):
        """Nettoie les fichiers de slices temporaires"""
        for path in slice_paths:
            if os.path.exists(path) and "_slice_" in path:
                try:
                    os.remove(path)
                except:
                    pass


class OCRProcessor:
    """Classe pour traiter l'OCR avec PaddleOCR et gestion des grandes images"""
    
    def __init__(self, lang='fr', max_image_height=2000):
        """
        Args:
            lang: langue ('fr', 'en', etc.)
            max_image_height: hauteur max avant découpage
        """
        self.ocr = PaddleOCR(
            use_angle_cls=True,
            lang=lang,
            use_gpu=False,
            show_log=False
        )
        self.slicer = ImageSlicer(max_height=max_image_height, overlap=100)
    
    def preprocess_image(self, image):
        """
        Prétraite une image (numpy array ou chemin)
        Args:
            image: image numpy ou chemin
        Returns:
            image prétraitée
        """
        if isinstance(image, str):
            img = cv2.imread(image)
        else:
            img = image.copy()
        
        if img is None:
            raise ValueError("Image invalide")
        
        # Redimensionner si trop large (pour optimiser l'OCR)
        height, width = img.shape[:2]
        if width > 2000:
            scale = 2000 / width
            new_width = 2000
            new_height = int(height * scale)
            img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
        
        # Convertir en niveaux de gris
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img
        
        # Améliorer le contraste
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        
        # Débruitage léger
        denoised = cv2.medianBlur(enhanced, 3)
        
        # Binarisation adaptative
        binary = cv2.adaptiveThreshold(
            denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        return binary
    
    def extract_text_from_slice(self, image_slice, preprocess=True):
        """Extrait le texte d'une slice d'image"""
        try:
            if preprocess:
                if isinstance(image_slice, str):
                    processed_img = self.preprocess_image(image_slice)
                    temp_path = f"temp_slice_{np.random.randint(1000, 9999)}.png"
                    cv2.imwrite(temp_path, processed_img)
                    result = self.ocr.ocr(temp_path, cls=True)
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                else:
                    processed_img = self.preprocess_image(image_slice)
                    temp_path = f"temp_slice_{np.random.randint(1000, 9999)}.png"
                    cv2.imwrite(temp_path, processed_img)
                    result = self.ocr.ocr(temp_path, cls=True)
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
            else:
                if isinstance(image_slice, str):
                    result = self.ocr.ocr(image_slice, cls=True)
                else:
                    temp_path = f"temp_slice_{np.random.randint(1000, 9999)}.png"
                    cv2.imwrite(temp_path, image_slice)
                    result = self.ocr.ocr(temp_path, cls=True)
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
            
            # Extraire le texte avec position
            extracted_lines = []
            if result and result[0]:
                for line in result[0]:
                    if len(line) >= 2 and line[1]:
                        text = line[1][0]
                        confidence = line[1][1]
                        bbox = line[0]
                        
                        if confidence > 0.6:  # Seuil de confiance
                            # Position verticale moyenne
                            y_pos = (bbox[0][1] + bbox[2][1]) / 2
                            extracted_lines.append((y_pos, text))
            
            # Trier par position verticale
            extracted_lines.sort(key=lambda x: x[0])
            
            return " ".join([text for _, text in extracted_lines])
            
        except Exception as e:
            print(f"Erreur OCR sur slice : {e}")
            return ""
    
    def extract_text_from_large_image(self, image_path, preprocess=True):
        """
        Extrait le texte d'une image de grande dimension
        Args:
            image_path: chemin vers l'image
            preprocess: appliquer le prétraitement
        Returns:
            texte complet extrait
        """
        print(f"Analyse de l'image : {image_path}")
        
        # Vérifier si l'image doit être découpée
        should_slice, height, width = self.slicer.should_slice_image(image_path)
        
        if not should_slice:
            print("Image de taille normale, traitement direct")
            return self.extract_text_from_slice(image_path, preprocess)
        
        print(f"Image de grande dimension ({width}x{height}), découpage nécessaire")
        
        # Découper l'image
        slice_paths = self.slicer.slice_image(image_path, save_slices=True)
        
        # Traiter chaque slice
        all_text_parts = []
        for i, slice_path in enumerate(slice_paths):
            print(f"Traitement slice {i+1}/{len(slice_paths)}")
            text_part = self.extract_text_from_slice(slice_path, preprocess)
            if text_part.strip():
                all_text_parts.append(text_part)
        
        # Nettoyer les fichiers temporaires
        self.slicer.clean_slice_files(slice_paths)
        
        # Combiner tout le texte
        complete_text = " ".join(all_text_parts)
        print(f"Extraction terminée : {len(complete_text)} caractères")
        
        return complete_text
    
    def extract_text_with_structure(self, image_path):
        """Extrait le texte en préservant la structure des grandes images"""
        should_slice, height, width = self.slicer.should_slice_image(image_path)
        
        if not should_slice:
            return self.extract_text_from_slice(image_path, preprocess=True)
        
        # Pour les grandes images, traiter par slices avec structure
        slice_paths = self.slicer.slice_image(image_path, save_slices=True)
        
        structured_parts = []
        for slice_path in slice_paths:
            try:
                result = self.ocr.ocr(slice_path, cls=True)
                
                if result and result[0]:
                    lines_with_pos = []
                    for line in result[0]:
                        if len(line) >= 2 and line[1] and line[1][1] > 0.6:
                            bbox = line[0]
                            text = line[1][0]
                            y_pos = (bbox[0][1] + bbox[2][1]) / 2
                            lines_with_pos.append((y_pos, text))
                    
                    # Trier par position verticale
                    lines_with_pos.sort(key=lambda x: x[0])
                    
                    # Reconstituer avec sauts de ligne
                    slice_text = ""
                    prev_y = 0
                    for y_pos, text in lines_with_pos:
                        if prev_y > 0 and y_pos - prev_y > 30:
                            slice_text += "\n"
                        slice_text += text + " "
                        prev_y = y_pos
                    
                    if slice_text.strip():
                        structured_parts.append(slice_text.strip())
            
            except Exception as e:
                print(f"Erreur sur slice : {e}")
                continue
        
        # Nettoyer les fichiers temporaires
        self.slicer.clean_slice_files(slice_paths)
        
        return "\n\n".join(structured_parts)


class TextCleaner:
    """Classe pour nettoyer le texte OCR"""
    
    def __init__(self, language='french'):
        self.language = language
        try:
            self.stop_words = set(stopwords.words('french' if language == 'french' else 'english'))
        except:
            self.stop_words = {'le', 'la', 'les', 'un', 'une', 'des', 'et', 'ou', 'mais', 'donc', 'car'}
    
    def clean_ocr_text(self, raw_text):
        """Nettoie le texte OCR avec gestion des grandes extractions"""
        if not raw_text:
            return ""
        
        # Corrections OCR spécifiques
        text = self.fix_common_ocr_errors(raw_text)
        
        # Normalisation des espaces multiples
        text = re.sub(r'\s+', ' ', text)
        
        # Supprimer les lignes très courtes (souvent du bruit)
        lines = text.split('\n')
        clean_lines = []
        for line in lines:
            line = line.strip()
            if len(line) > 3 and len(line.split()) > 1:
                clean_lines.append(line)
        
        text = ' '.join(clean_lines)
        
        # Supprimer les caractères isolés
        text = re.sub(r'\b[a-zA-Z]\b', '', text)
        
        # Nettoyer les caractères spéciaux
        text = re.sub(r'[^\w\s\.\?\!\,\;\:\-\(\)]', ' ', text)
        
        # Corriger la ponctuation
        text = re.sub(r'\s+([\.!\?])', r'\1', text)
        text = re.sub(r'([\.!\?])\s*([A-Z])', r'\1 \2', text)
        
        # Supprimer les répétitions excessives
        text = re.sub(r'(.)\1{3,}', r'\1\1', text)
        
        return text.strip()
    
    def fix_common_ocr_errors(self, text):
        """Corrige les erreurs OCR courantes"""
        corrections = {
            r'\b0(?=[a-z])\b': 'o',     # 0 -> o devant lettre
            r'\b1(?=[a-z])\b': 'l',     # 1 -> l devant lettre
            r'rn': 'm',                  # rn -> m
            r'vv': 'w',                  # vv -> w
            r'(\w)\|(\w)': r'\1l\2',    # | -> l entre lettres
            r'(\w)1(\w)': r'\1l\2',     # 1 -> l entre lettres
            r'\b5(?=[a-z])\b': 's',     # 5 -> s dans certains cas
            r'(?<=\w)0(?=\w)': 'o',     # 0 -> o entre lettres
        }
        
        for pattern, replacement in corrections.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text
    
    def segment_into_sentences(self, text):
        """Segmente en phrases avec filtrage intelligent"""
        try:
            sentences = sent_tokenize(text)
        except:
            sentences = re.split(r'[.!?]+', text)
        
        clean_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            
            # Critères de qualité pour les phrases
            word_count = len(sentence.split())
            if (word_count >= 3 and                    # Au moins 3 mots
                len(sentence) >= 10 and                # Au moins 10 caractères
                len(sentence) <= 500 and               # Pas trop long
                not re.match(r'^[^a-zA-Z]*$', sentence)): # Contient des lettres
                
                clean_sentences.append(sentence)
        
        return clean_sentences


class WebQASystem:
    """Système QA optimisé pour grandes extractions"""
    
    def __init__(self, language='french'):
        self.language = language
        self.vectorizer = TfidfVectorizer(
            stop_words='french' if language == 'french' else 'english',
            max_features=2000,  # Augmenté pour grandes extractions
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.95
        )
        self.sentences = []
        self.sentence_vectors = None
        self.word2vec_model = None
        self.topics = []
        
        try:
            self.stop_words = set(stopwords.words('french' if language == 'french' else 'english'))
        except:
            self.stop_words = {'le', 'la', 'les', 'un', 'une', 'des', 'et', 'ou', 'mais', 'donc', 'car'}
    
    def extract_keywords(self, text, top_k=15):
        """Extrait plus de mots-clés pour grandes extractions"""
        try:
            words = word_tokenize(text.lower())
        except:
            words = text.lower().split()
        
        words = [word for word in words 
                if word.isalpha() and word not in self.stop_words and len(word) > 2]
        
        word_freq = Counter(words)
        return [word for word, freq in word_freq.most_common(top_k)]
    
    def identify_topics(self, sentences, n_topics=5):
        """Identifie plus de sujets pour contenu riche"""
        if len(sentences) < n_topics:
            return sentences[:min(5, len(sentences))]
        
        try:
            vectors = self.vectorizer.fit_transform(sentences)
            n_clusters = min(n_topics, len(sentences) // 3)  # Adapter le nb de clusters
            
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            clusters = kmeans.fit_predict(vectors)
            
            topics = []
            for i in range(n_clusters):
                cluster_sentences = [sentences[j] for j in range(len(sentences)) 
                                   if clusters[j] == i]
                if cluster_sentences:
                    # Prendre la phrase la plus représentative
                    representative = min(cluster_sentences, 
                                       key=lambda x: len(x) if len(x) > 50 else float('inf'))
                    topics.append(representative)
            
            return topics
        except Exception as e:
            print(f"Erreur clustering : {e}")
            return sentences[:min(5, len(sentences))]
    
    def generate_summary(self, sentences, max_sentences=7):
        """Génère un résumé plus long pour grandes extractions"""
        if len(sentences) <= max_sentences:
            return " ".join(sentences)
        
        try:
            vectors = self.vectorizer.fit_transform(sentences)
            
            sentence_scores = []
            for i, vector in enumerate(vectors):
                tfidf_score = vector.sum()
                position_bonus = 1.0 / (1 + i * 0.05)  # Bonus position moins agressif
                
                word_count = len(sentences[i].split())
                length_bonus = min(word_count / 20.0, 1.2) if word_count > 8 else 0.7
                
                # Bonus pour phrases avec mots-clés importants
                important_words = ['prix', 'contact', 'service', 'produit', 'offre', 'entreprise']
                keyword_bonus = 1.0
                sentence_lower = sentences[i].lower()
                for word in important_words:
                    if word in sentence_lower:
                        keyword_bonus += 0.1
                
                final_score = tfidf_score * position_bonus * length_bonus * keyword_bonus
                sentence_scores.append((i, final_score))
            
            sentence_scores.sort(key=lambda x: x[1], reverse=True)
            selected_indices = sorted([idx for idx, score in sentence_scores[:max_sentences]])
            
            return " ".join([sentences[i] for i in selected_indices])
            
        except Exception as e:
            print(f"Erreur résumé : {e}")
            return " ".join(sentences[:max_sentences])
    
    def train_word_embeddings(self, sentences):
        """Entraîne Word2Vec avec plus de données"""
        try:
            tokenized_sentences = []
            for sentence in sentences:
                try:
                    tokens = word_tokenize(sentence.lower())
                except:
                    tokens = sentence.lower().split()
                
                # Filtrer les tokens
                filtered_tokens = [token for token in tokens 
                                 if token.isalpha() and len(token) > 2]
                if len(filtered_tokens) > 2:
                    tokenized_sentences.append(filtered_tokens)
            
            if len(tokenized_sentences) > 5:
                self.word2vec_model = Word2Vec(
                    tokenized_sentences,
                    vector_size=150,  # Augmenté
                    window=7,         # Fenêtre plus large
                    min_count=2,      # Mots apparaissant au moins 2 fois
                    workers=1,
                    epochs=10
                )
        except Exception as e:
            print(f"Erreur Word2Vec : {e}")
            self.word2vec_model = None
    
    def classify_question_type(self, question):
        """Classification améliorée"""
        question_lower = question.lower()
        
        summary_keywords = ['résume', 'résumé', 'parle', 'sujet', 'contenu', 'principal', 'essentiel', 'synthèse']
        topic_keywords = ['quoi', 'de quoi', 'thème', 'sujet', 'propos', 'traite']
        specific_keywords = ['prix', 'coût', 'tarif', 'contact', 'téléphone', 'email', 'adresse', 'horaire']
        
        if any(keyword in question_lower for keyword in summary_keywords):
            return 'summary'
        elif any(keyword in question_lower for keyword in topic_keywords):
            return 'topic'
        elif any(keyword in question_lower for keyword in specific_keywords):
            return 'specific_info'
        else:
            return 'general'
    
    def answer_specific_question(self, question, top_k=5):
        """Réponses spécifiques avec plus de contexte"""
        if not hasattr(self, 'sentence_vectors') or self.sentence_vectors is None:
            return "Aucun contenu indexé."
        
        try:
            question_vector = self.vectorizer.transform([question])
            similarities = cosine_similarity(question_vector, self.sentence_vectors).flatten()
            
            # Seuil adaptatif selon la longueur du corpus
            threshold = 0.05 if len(self.sentences) > 50 else 0.01
            
            top_indices = similarities.argsort()[-top_k:][::-1]
            relevant_sentences = [self.sentences[i] for i in top_indices 
                                if similarities[i] > threshold]
            
            if not relevant_sentences:
                return "Je n'ai pas trouvé d'information pertinente pour cette question dans le contenu analysé."
            
            # Limiter la longueur de la réponse
            response = " ".join(relevant_sentences)
            if len(response) > 800:
                response = response[:800] + "..."
            
            return response
            
        except Exception as e:
            print(f"Erreur réponse spécifique : {e}")
            return "Erreur lors de la recherche."
    
    def process_content(self, sentences):
        """Traite le contenu avec optimisations pour grandes extractions"""
        self.sentences = sentences
        
        if not self.sentences:
            return "Aucun contenu à traiter."
        
        print(f"Traitement de {len(sentences)} phrases...")
        
        try:
            # Vectorisation avec gestion mémoire
            if len(sentences) > 1000:
                print("Grand corpus détecté, optimisation en cours...")
                # Pour très gros corpus, prendre un échantillon représentatif
                step = max(1, len(sentences) // 500)
                sample_sentences = sentences[::step]
                self.sentence_vectors = self.vectorizer.fit_transform(sample_sentences)
                # Mais garder toutes les phrases pour les réponses
            else:
                self.sentence_vectors = self.vectorizer.fit_transform(self.sentences)
            
            # Word2Vec
            self.train_word_embeddings(self.sentences)
            
            # Topics
            self.topics = self.identify_topics(self.sentences)
            
            return f"Contenu traité : {len(self.sentences)} phrases, {len(self.topics)} sujets identifiés."
            
        except Exception as e:
            return f"Erreur traitement : {e}"
    
    def answer_question(self, question):
        """Réponse adaptée au type de question"""
        if not self.sentences:
            return "Aucun contenu indexé."
        
        question_type = self.classify_question_type(question)
        
        if question_type == 'summary':
            summary = self.generate_summary(self.sentences, max_sentences=7)
            return f"Résumé du contenu : {summary}"
        
        elif question_type == 'topic':
            topics_text = " | ".join(self.topics[:3])  # Limiter à 3 sujets principaux
            keywords = self.extract_keywords(" ".join(self.sentences[:100]), top_k=10)  # Échantillon pour mots-clés
            keywords_text = ", ".join(keywords)
            return f"Ce contenu traite principalement de : {topics_text}. Mots-clés importants : {keywords_text}"
        
        else:
            return self.answer_specific_question(question)


class CompleteOCRQASystem:
    """Système complet optimisé pour grandes images"""
    
    def __init__(self, language='french', ocr_lang='fr', max_image_height=2000):
        self.ocr_processor = OCRProcessor(lang=ocr_lang, max_image_height=max_image_height)
        self.text_cleaner = TextCleaner(language=language)
        self.qa_system = WebQASystem(language=language)
        
    def process_image(self, image_path, use_layout=True):
        """Traite une image de n'importe quelle taille"""
        print(f"=== TRAITEMENT DE L'IMAGE ===")
        print(f"Chemin : {image_path}")
        
        if not os.path.exists(image_path):
            return f"Image non trouvée : {image_path}"
        
        # Vérifier les dimensions
        img = cv2.imread(image_path)
        if img is None:
            return "Impossible de charger l'image"
        
        height, width = img.shape[:2]
        print(f"Dimensions : {width}x{height}")
        
        # Extraction OCR adaptée
        if use_layout:
            raw_text = self.ocr_processor.extract_text_with_structure(image_path)
        else:
            raw_text = self.ocr_processor.extract_text_from_large_image(image_path)
        
        if not raw_text:
            return "Aucun texte détecté dans l'image."
        
        print(f"Texte brut : {len(raw_text)} caractères")
        
        # Nettoyage
        cleaned_text = self.text_cleaner.clean_ocr_text(raw_text)
        
        # Segmentation
        sentences = self.text_cleaner.segment_into_sentences(cleaned_text)
        
        if not sentences:
            return "Aucune phrase valide après nettoyage."
        
        print(f"Phrases valides : {len(sentences)}")
        
        # Indexation
        result = self.qa_system.process_content(sentences)
        
        return result
    
    def ask_question(self, question):
        """Pose une question"""
        return self.qa_system.answer_question(question)
    
    def get_content_info(self):
        """Informations sur le contenu"""
        if not self.qa_system.sentences:
            return "Aucun contenu traité."
        
        num_sentences = len(self.qa_system.sentences)
        num_words = sum(len(sentence.split()) for sentence in self.qa_system.sentences)
        avg_sentence_length = num_words / num_sentences if num_sentences > 0 else 0
        
        return (f"Contenu analysé :\n"
                f"- {num_sentences} phrases\n"
                f"- ~{num_words} mots\n"
                f"- Longueur moyenne : {avg_sentence_length:.1f} mots/phrase")


def main():
    """Test du système avec grande image"""
    # Initialisation
    system = CompleteOCRQASystem(
        language='french', 
        ocr_lang='fr', 
        max_image_height=2000  # Hauteur max par slice
    )
    
    # REMPLACER PAR VOTRE CHEMIN D'IMAGE
    image_path = "screenshot.png"  # Votre image 1280x14054
    
    if os.path.exists(image_path):
        print("=== TRAITEMENT IMAGE GRANDE DIMENSION ===")
        result = system.process_image(image_path, use_layout=True)
        print(result)
        
        print(f"\n{system.get_content_info()}")
        
        print("\n=== QUESTIONS TEST ===")
        questions = [
            "De quoi parle cette page ?",
            "Peux-tu me faire un résumé complet ?",
            "Quels sont les prix mentionnés ?",
            "Comment contacter l'entreprise ?",
            "Quels services sont proposés ?",
            "Y a-t-il des horaires d'ouverture ?"
        ]
        
        for question in questions:
            print(f"\nQ: {question}")
            answer = system.ask_question(question)
            print(f"R: {answer}")
    
    else:
        print(f"Veuillez placer votre image dans : {image_path}")
        print("Ou modifier le chemin dans le code.")


if __name__ == "__main__":
    main()
