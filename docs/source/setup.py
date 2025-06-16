#!/usr/bin/env python3
"""
Script d'installation automatique pour SmartWebScraper-CV
Auteurs: DJERI-ALASSANI OUBENOUPOU & EL MAJDI WALID
ENSAM Meknès - 2025
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

class SmartWebScraperInstaller:
    def __init__(self):
        self.system = platform.system().lower()
        self.python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        self.project_root = Path(__file__).parent.absolute()
        self.venv_path = self.project_root / "venv"
        
    def print_header(self):
        """Affiche l'en-tête d'installation"""
        print("=" * 60)
        print("  SmartWebScraper-CV - Installation Automatique")
        print("  ENSAM Meknès - IATD-SI 2025")
        print("=" * 60)
        print(f"Système détecté: {platform.system()} {platform.release()}")
        print(f"Python version: {self.python_version}")
        print(f"Répertoire projet: {self.project_root}")
        print()

    def check_python_version(self):
        """Vérifie la version Python"""
        if sys.version_info < (3, 9) or sys.version_info >= (3, 11):
            print("❌ Python 3.9-3.10 requis")
            print(f"   Version actuelle: {self.python_version}")
            sys.exit(1)
        print(f"✅ Python {self.python_version} compatible")

    def create_virtual_environment(self):
        """Création de l'environnement virtuel"""
        print("\n🐍 Création de l'environnement virtuel...")
        
        if self.venv_path.exists():
            print("ℹ️  Environnement virtuel existant détecté")
            response = input("   Supprimer et recréer? (y/N): ")
            if response.lower() == 'y':
                shutil.rmtree(self.venv_path)
            else:
                print("✅ Utilisation de l'environnement existant")
                return

        try:
            subprocess.run([sys.executable, '-m', 'venv', str(self.venv_path)], check=True)
            print("✅ Environnement virtuel créé")
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur création environnement virtuel: {e}")
            sys.exit(1)

    def get_pip_command(self):
        """Retourne la commande pip pour l'environnement virtuel"""
        if self.system == 'windows':
            return str(self.venv_path / "Scripts" / "pip.exe")
        else:
            return str(self.venv_path / "bin" / "pip")

    def install_requirements(self):
        """Installation des dépendances principales"""
        print("\n📦 Installation des dépendances Python...")
        pip_cmd = self.get_pip_command()
        
        requirements_file = self.project_root / "requirements.txt"
        if not requirements_file.exists():
            print("⚠️  Fichier requirements.txt manquant - création automatique")
            self.create_requirements_file()
        
        try:
            subprocess.run([pip_cmd, "install", "-r", str(requirements_file)], check=True)
            print("✅ Dépendances installées avec succès")
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur installation dépendances: {e}")
            sys.exit(1)

    def create_requirements_file(self):
        """Crée le fichier requirements.txt si manquant"""
        requirements_content = """# SmartWebScraper-CV Requirements
Flask==2.3.2
Flask-CORS==4.0.0
opencv-python==4.8.0.74
Pillow==9.5.0
paddleocr==2.7.0.3
nltk==3.8.1
spacy==3.6.1
scikit-learn==1.3.0
gensim==4.3.1
selenium==4.11.2
undetected-chromedriver==3.5.3
playwright==1.37.0
numpy==1.24.3
pandas==2.0.3
requests==2.31.0
python-dotenv==1.0.0
google-generativeai==0.1.0
tqdm==4.65.0
"""
        
        with open(self.project_root / "requirements.txt", "w") as f:
            f.write(requirements_content)
        print("✅ Fichier requirements.txt créé")

    def download_nlp_models(self):
        """Téléchargement des modèles NLP"""
        print("\n🧠 Téléchargement des modèles NLP...")
        python_cmd = self.get_python_command()
        
        # Modèles NLTK
        try:
            nltk_cmd = [
                python_cmd, "-c", 
                "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
            ]
            subprocess.run(nltk_cmd, check=True)
            print("✅ Modèles NLTK téléchargés")
        except subprocess.CalledProcessError:
            print("⚠️  Erreur téléchargement modèles NLTK")

        # Modèle spaCy français
        try:
            spacy_cmd = [python_cmd, "-m", "spacy", "download", "fr_core_news_sm"]
            subprocess.run(spacy_cmd, check=True)
            print("✅ Modèle spaCy français téléchargé")
        except subprocess.CalledProcessError:
            print("⚠️  Erreur téléchargement modèle spaCy")

    def get_python_command(self):
        """Retourne la commande python pour l'environnement virtuel"""
        if self.system == 'windows':
            return str(self.venv_path / "Scripts" / "python.exe")
        else:
            return str(self.venv_path / "bin" / "python")

    def create_directory_structure(self):
        """Création de la structure de dossiers"""
        print("\n📁 Création de la structure de dossiers...")
        
        directories = [
            "data/originals",
            "data/annotated", 
            "data/human_data/manual",
            "data/human_data/model",
            "data/fine_tune_data",
            "data/suppression",
            "logs"
        ]
        
        for directory in directories:
            dir_path = self.project_root / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"✅ {directory}")

    def create_env_file(self):
        """Création du fichier .env"""
        print("\n⚙️  Création du fichier de configuration...")
        
        env_file = self.project_root / ".env"
        if env_file.exists():
            print("ℹ️  Fichier .env existant trouvé")
            response = input("   Écraser? (y/N): ")
            if response.lower() != 'y':
                return

        gpu_available = self.check_cuda_availability()
        
        env_content = f"""# SmartWebScraper-CV Configuration
# Généré automatiquement par setup.py

# Configuration Flask
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=smartwebscraper-secret-key-{os.urandom(8).hex()}

# Configuration GPU/CPU
CUDA_VISIBLE_DEVICES=0
FORCE_CPU_MODE={'False' if gpu_available else 'True'}

# API Keys (à configurer manuellement)
GEMINI_API_KEY=your-gemini-api-key-here
SERPAPI_KEY=your-serpapi-key-here

# Configuration OCR
PADDLEOCR_USE_GPU={'True' if gpu_available else 'False'}
PADDLEOCR_LANG=fr,en

# Configuration Modèles
DETECTRON2_MODEL_PATH=app/models/detectron2/model_final.pth
DETECTRON2_CONFIG_PATH=app/configs/faster_rcnn_R_50_FPN_3x.yaml

# Ollama (LLM local)
OLLAMA_BASE_URL=http://localhost:11434

# Configuration Application
MAX_CONTENT_LENGTH=16777216
UPLOAD_FOLDER=temp/uploads
"""
        
        with open(env_file, "w") as f:
            f.write(env_content)
        print("✅ Fichier .env créé")

    def install_chrome_driver(self):
        """Installation du driver Chrome"""
        print("\n🌐 Configuration du driver Chrome...")
        
        try:
            # Vérification de Chrome
            if self.system == 'linux':
                chrome_check = subprocess.run(['google-chrome', '--version'], 
                                            capture_output=True, text=True)
            elif self.system == 'windows':
                chrome_check = subprocess.run(['chrome', '--version'], 
                                            capture_output=True, text=True)
            elif self.system == 'darwin':  # macOS
                chrome_check = subprocess.run(['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '--version'], 
                                            capture_output=True, text=True)
            
            if chrome_check.returncode == 0:
                print("✅ Google Chrome détecté")
                print(f"   Version: {chrome_check.stdout.strip()}")
            else:
                print("⚠️  Google Chrome non détecté")
                self.install_chrome()
                
        except FileNotFoundError:
            print("⚠️  Google Chrome non trouvé")
            self.install_chrome()

    def install_chrome(self):
        """Installation de Google Chrome"""
        print("📥 Installation de Google Chrome...")
        
        if self.system == 'linux':
            try:
                commands = [
                    "wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -",
                    "sudo sh -c 'echo \"deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main\" >> /etc/apt/sources.list.d/google-chrome.list'",
                    "sudo apt update",
                    "sudo apt install -y google-chrome-stable"
                ]
                
                for cmd in commands:
                    subprocess.run(cmd, shell=True, check=True)
                print("✅ Google Chrome installé")
            except subprocess.CalledProcessError:
                print("❌ Erreur installation Chrome")
        else:
            print("💡 Veuillez installer Google Chrome manuellement:")
            print("   https://www.google.com/chrome/")

    def run_tests(self):
        """Tests de validation de l'installation"""
        print("\n🧪 Tests de validation...")
        python_cmd = self.get_python_command()
        
        tests = [
            ("Import PyTorch", "import torch; print(f'PyTorch: {torch.__version__}')"),
            ("Import OpenCV", "import cv2; print(f'OpenCV: {cv2.__version__}')"),
            ("Import NLTK", "import nltk; print('NLTK: OK')"),
            ("Import spaCy", "import spacy; print('spaCy: OK')"),
            ("Import Flask", "from flask import Flask; print('Flask: OK')"),
            ("Test PaddleOCR", "from paddleocr import PaddleOCR; print('PaddleOCR: OK')"),
        ]
        
        for test_name, test_code in tests:
            try:
                result = subprocess.run([python_cmd, "-c", test_code], 
                                      capture_output=True, text=True, check=True)
                print(f"✅ {test_name}: {result.stdout.strip()}")
            except subprocess.CalledProcessError:
                print(f"❌ {test_name}: ÉCHEC")

    def print_next_steps(self):
        """Affiche les étapes suivantes"""
        print("\n" + "=" * 60)
        print("🎉 Installation terminée avec succès!")
        print("=" * 60)
        print("\n📋 Étapes suivantes:")
        print()
        print("1. Activer l'environnement virtuel:")
        if self.system == 'windows':
            print(f"   {self.venv_path}\\Scripts\\activate")
        else:
            print(f"   source {self.venv_path}/bin/activate")
        
        print("\n2. Configurer les clés API dans .env:")
        print("   - GEMINI_API_KEY (pour l'IA générative)")
        print("   - SERPAPI_KEY (pour la collecte d'URLs)")
        
        print("\n3. Lancer l'application:")
        print("   python run.py")
        
        print("\n4. Accéder à l'interface:")
        print("   http://localhost:5000")
        
        print("\n💡 Pour Ollama (LLM local):")
        print("   curl -fsSL https://ollama.ai/install.sh | sh")
        print("   ollama pull mistral")

    def run(self):
        """Exécute l'installation complète"""
        try:
            self.print_header()
            self.check_python_version()
            self.check_system_dependencies()
            self.create_virtual_environment()
            self.install_pytorch()
            self.install_requirements()
            self.install_detectron2()
            self.download_nlp_models()
            self.create_directory_structure()
            self.create_env_file()
            self.install_chrome_driver()
            self.run_tests()
            self.print_next_steps()
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Installation interrompue par l'utilisateur")
            sys.exit(1)
        except Exception as e:
            print(f"\n\n❌ Erreur inattendue: {e}")
            sys.exit(1)


if __name__ == "__main__":
    installer = SmartWebScraperInstaller()
    installer.run()
            dir_path = self.project_root / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"✅ {directory}")

    def create_env_file(self):
        """Création du fichier .env"""
        print("\n⚙️  Création du fichier de configuration...")
        
        env_file = self.project_root / ".env"
        if env_file.exists():
            print("ℹ️  Fichier .env existant trouvé")
            response = input("   Écraser? (y/N): ")
            if response.lower() != 'y':
                return

        env_content = f"""# SmartWebScraper-CV Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=smartwebscraper-secret-key-{os.urandom(8).hex()}

# API Keys (à configurer manuellement)
GEMINI_API_KEY=your-gemini-api-key-here

# Configuration Admin
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=your_password

# Ollama (LLM local)
OLLAMA_BASE_URL=http://localhost:11434
"""
        
        with open(env_file, "w") as f:
            f.write(env_content)
        print("✅ Fichier .env créé")

    def print_next_steps(self):
        """Affiche les étapes suivantes"""
        print("\n" + "=" * 60)
        print("🎉 Installation terminée avec succès!")
        print("=" * 60)
        print("\n📋 Étapes suivantes:")
        print()
        print("1. Activer l'environnement virtuel:")
        if self.system == 'windows':
            print(f"   {self.venv_path}\\Scripts\\activate")
        else:
            print(f"   source {self.venv_path}/bin/activate")
        
        print("\n2. Configurer votre clé API Gemini dans .env")
        print("   Guide: https://dev.to/explinks/how-to-obtain-a-gemini-api-key-step-by-step-guide-4m97")
        
        print("\n3. Installer Detectron2 selon votre OS:")
        print("   - Windows: Voir guides dans le repository")
        print("   - Linux: pip install 'git+https://github.com/facebookresearch/detectron2.git'")
        
        print("\n4. Optionnel - Installer Ollama pour LLM local:")
        print("   https://ollama.com/")
        
        print("\n5. Lancer l'application:")
        print("   python run.py")
        
        print("\n6. Accéder à l'interface:")
        print("   http://localhost:5000")

    def run(self):
        """Exécute l'installation complète"""
        try:
            self.print_header()
            self.check_python_version()
            self.create_virtual_environment()
            self.install_requirements()
            self.download_nlp_models()
            self.create_directory_structure()
            self.create_env_file()
            self.print_next_steps()
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Installation interrompue par l'utilisateur")
            sys.exit(1)
        except Exception as e:
            print(f"\n\n❌ Erreur inattendue: {e}")
            sys.exit(1)


if __name__ == "__main__":
    installer = SmartWebScraperInstaller()
    installer.run()
            dir_path = self.project_root / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"✅ {directory}")

    def create_env_file(self):
        """Création du fichier .env"""
        print("\n⚙️  Création du fichier de configuration...")
        
        env_file = self.project_root / ".env"
        if env_file.exists():
            print("ℹ️  Fichier .env existant trouvé")
            response = input("   Écraser? (y/N): ")
            if response.lower() != 'y':
                return

        gpu_available = self.check_cuda_availability()
        
        env_content = f"""# SmartWebScraper-CV Configuration
# Généré automatiquement par setup.py

# Configuration Flask
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=smartwebscraper-secret-key-{os.urandom(8).hex()}

# Configuration GPU/CPU
CUDA_VISIBLE_DEVICES=0
FORCE_CPU_MODE={'False' if gpu_available else 'True'}

# API Keys (à configurer manuellement)
GEMINI_API_KEY=your-gemini-api-key-here
SERPAPI_KEY=your-serpapi-key-here

# Configuration OCR
PADDLEOCR_USE_GPU={'True' if gpu_available else 'False'}
PADDLEOCR_LANG=fr,en

# Configuration Modèles
DETECTRON2_MODEL_PATH=app/models/detectron2/model_final.pth
DETECTRON2_CONFIG_PATH=app/configs/faster_rcnn_R_50_FPN_3x.yaml

# Ollama (LLM local)
OLLAMA_BASE_URL=http://localhost:11434

# Configuration Application
MAX_CONTENT_LENGTH=16777216
UPLOAD_FOLDER=temp/uploads
"""
        
        with open(env_file, "w") as f:
            f.write(env_content)
        print("✅ Fichier .env créé")

    def install_chrome_driver(self):
        """Installation du driver Chrome"""
        print("\n🌐 Configuration du driver Chrome...")
        
        try:
            # Vérification de Chrome
            if self.system == 'linux':
                chrome_check = subprocess.run(['google-chrome', '--version'], 
                                            capture_output=True, text=True)
            elif self.system == 'windows':
                chrome_check = subprocess.run(['chrome', '--version'], 
                                            capture_output=True, text=True)
            elif self.system == 'darwin':  # macOS
                chrome_check = subprocess.run(['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '--version'], 
                                            capture_output=True, text=True)
            
            if chrome_check.returncode == 0:
                print("✅ Google Chrome détecté")
                print(f"   Version: {chrome_check.stdout.strip()}")
            else:
                print("⚠️  Google Chrome non détecté")
                self.install_chrome()
                
        except FileNotFoundError:
            print("⚠️  Google Chrome non trouvé")
            self.install_chrome()

    def install_chrome(self):
        """Installation de Google Chrome"""
        print("📥 Installation de Google Chrome...")
        
        if self.system == 'linux':
            try:
                commands = [
                    "wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -",
                    "sudo sh -c 'echo \"deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main\" >> /etc/apt/sources.list.d/google-chrome.list'",
                    "sudo apt update",
                    "sudo apt install -y google-chrome-stable"
                ]
                
                for cmd in commands:
                    subprocess.run(cmd, shell=True, check=True)
                print("✅ Google Chrome installé")
            except subprocess.CalledProcessError:
                print("❌ Erreur installation Chrome")
        else:
            print("💡 Veuillez installer Google Chrome manuellement:")
            print("   https://www.google.com/chrome/")

    def run_tests(self):
        """Tests de validation de l'installation"""
        print("\n🧪 Tests de validation...")
        python_cmd = self.get_python_command()
        
        tests = [
            ("Import PyTorch", "import torch; print(f'PyTorch: {torch.__version__}')"),
            ("Import OpenCV", "import cv2; print(f'OpenCV: {cv2.__version__}')"),
            ("Import NLTK", "import nltk; print('NLTK: OK')"),
            ("Import spaCy", "import spacy; print('spaCy: OK')"),
            ("Import Flask", "from flask import Flask; print('Flask: OK')"),
            ("Test PaddleOCR", "from paddleocr import PaddleOCR; print('PaddleOCR: OK')"),
        ]
        
        for test_name, test_code in tests:
            try:
                result = subprocess.run([python_cmd, "-c", test_code], 
                                      capture_output=True, text=True, check=True)
                print(f"✅ {test_name}: {result.stdout.strip()}")
            except subprocess.CalledProcessError:
                print(f"❌ {test_name}: ÉCHEC")

    def print_next_steps(self):
        """Affiche les étapes suivantes"""
        print("\n" + "=" * 60)
        print("🎉 Installation terminée avec succès!")
        print("=" * 60)
        print("\n📋 Étapes suivantes:")
        print()
        print("1. Activer l'environnement virtuel:")
        if self.system == 'windows':
            print(f"   {self.venv_path}\\Scripts\\activate")
        else:
            print(f"   source {self.venv_path}/bin/activate")
        
        print("\n2. Configurer les clés API dans .env:")
        print("   - GEMINI_API_KEY (pour l'IA générative)")
        print("   - SERPAPI_KEY (pour la collecte d'URLs)")
        
        print("\n3. Lancer l'application:")
        print("   python run.py")
        
        print("\n4. Accéder à l'interface:")
        print("   http://localhost:5000")
        
        print("\n💡 Pour Ollama (LLM local):")
        print("   curl -fsSL https://ollama.ai/install.sh | sh")
        print("   ollama pull mistral")

    def run(self):
        """Exécute l'installation complète"""
        try:
            self.print_header()
            self.check_python_version()
            self.check_system_dependencies()
            self.create_virtual_environment()
            self.install_pytorch()
            self.install_requirements()
            self.install_detectron2()
            self.download_nlp_models()
            self.create_directory_structure()
            self.create_env_file()
            self.install_chrome_driver()
            self.run_tests()
            self.print_next_steps()
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Installation interrompue par l'utilisateur")
            sys.exit(1)
        except Exception as e:
            print(f"\n\n❌ Erreur inattendue: {e}")
            sys.exit(1)


if __name__ == "__main__":
    installer = SmartWebScraperInstaller()
    installer.run()
