# SmartWebScraper-CV - Application Locale (Flask)

<div align="center">
  <img src="https://media.giphy.com/media/SWoSkN6DxTszqIKEqv/giphy.gif" alt="SmartWebScraper demonstration" width="500"/>
</div>

Ce dossier contient l’interface web Flask pour **SmartWebScraper-CV**.  
L'application permet de capturer des pages web, d’annoter automatiquement ou manuellement les éléments détectés, et de gérer les données nécessaires à l'entraînement de modèles de détection.

## :dart: Prérequis

- **Python 3.9 ou supérieur** installé.
- Un terminal (Command Prompt sur Windows, Terminal sur macOS/Linux).
- **Git** (optionnel) pour cloner le dépôt.

## :gear: Installation

1. **Téléchargement du projet**

   - Via Git :
     ```bash
     git clone https://github.com/ZIADEA/SmartWebScraper-CV.git
     ```
   - Ou téléchargez le fichier ZIP via GitHub et extrayez-le.

2. **Accédez au dossier de l’application locale**
   ```bash
   cd SmartWebScraper-CV/LocalApp/SMARTWEBSCRAPPER-CV
   ```

3. **(Optionnel) Créez un environnement virtuel**
   ```bash
   python -m venv venv
   ```
   - Windows : `venv\Scripts\activate`
   - macOS/Linux : `source venv/bin/activate`

4. **Installez les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

5. **Installez les navigateurs Playwright** (nécessaire uniquement la première fois)
   ```bash
   playwright install
   ```

6. **Configurez le compte admin**  
   Vous pouvez définir les variables d’environnement ou modifier le fichier `admin_config.json` :
   - macOS/Linux :
     ```bash
     export ADMIN_EMAIL="admin@example.com"
     export ADMIN_PASSWORD="your_password"
     ```
   - Windows :
     ```cmd
     set ADMIN_EMAIL="admin@example.com"
     set ADMIN_PASSWORD="your_password"
     ```

## :rocket: Lancement de l'application

### Étape 0 — Clé API Gemini (obligatoire)
Créez un fichier `.env` et ajoutez votre clé API Gemini.  
Suivez ce guide : [How to obtain a Gemini API key](https://dev.to/explinks/how-to-obtain-a-gemini-api-key-step-by-step-guide-4m97)

### Étape 1 — Modèle local Mistral
Téléchargez et installez **Ollama** : [https://ollama.com/](https://ollama.com/)  
Puis lancez dans un terminal :
```bash
ollama run mistral
```
et laisse le tourner en backend 

### Étape 2 — Démarrer le serveur Flask
```bash
python run.py
```

### Étape 3 — Accéder à l'application
Ouvrez votre navigateur et allez sur : [http://localhost:5000](http://localhost:5000)

### Étape 4 — Arrêter l'application
Dans le terminal ou vous avez demarer le terminal , utilisez `Ctrl + C` pour interrompre l’exécution.

## :file_folder: Dossiers générés

L’application crée automatiquement un dossier `data/` contenant les sous-dossiers suivants :

```
data/
├── originals/            # Captures originales des pages
├── resized/              # Images redimensionnées (si activé)
├── annotated/            # Résultats d’annotation automatique
├── predictions_raw/      # Prédictions du modèle (coordonnées brutes)
├── predictions_scaled/   # Prédictions mises à l’échelle
├── human_data/           # Annotations manuelles utilisateur
├── fine_tune_data/       # Données validées pour le réentraînement
```

## :repeat: Workflow

Pour comprendre le fonctionnement global de l'application et l’enchaînement des pages/interfaces, veuillez consulter le fichier [`WORKFLOW.md`](WORKFLOW.md).
