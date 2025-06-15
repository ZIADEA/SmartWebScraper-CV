# Application Workflow

L’application locale **SmartWebScraper-CV**
guide l’utilisateur à travers une série d’étapes pour capturer et annoter des sites web. Ci-dessous, une description simplifiée de son fonctionnement.

1. **Home Page**
   - Choisissez de continuer en tant qu’utilisateur standard ou connectez-vous en tant qu’administrateur.

2. **User Path**
   - Entrez l’URL d’un site web. L’application utilise **Playwright** pour capturer une capture d’écran.
   - Cette image est ensuite traitée par un modèle de détection d’objets qui met en évidence les éléments courants d’une page web (publicités, en-têtes, barres latérales, etc.).
   - Vous pouvez poser une question sur la page en utilisant **Gemini** ou le moteur NLP local ou mistral LLM local.
   - Validez ou modifiez les zones de détection proposées. Il est possible de supprimer des boîtes detecter par le model  ou d’en créer de nouvelles boites via l’interface d’annotation intégrée.
   - Une fois terminé, l’image et ses annotations sont enregistrées dans le dossier `human_data/` pour relecture. Elles peuvent ensuite être promues dans `fine_tune_data/`.

3. **Admin Path**
   - Connectez-vous avec les identifiants administrateur.
   - pour se connecté en tant que administrateur le log in est djeryala@gmail.com et et mot de pass est DJERI
   - Le tableau de bord permet de :
     - Visualiser l’historique des liens visités.
     - Examiner les prédictions validées par les utilisateurs.
     - Inspecter les annotations manuelles soumises par les utilisateurs.
     - Suivre le nombre d’images disponibles pour l’affinage du modèle.
     - Lancer une phase de **fine‑tuning** du modèle de détection (après quoi les images dans `fine_tune_data/` sont réinitialisées).

4. **Data Folders**
   - `originals/` – captures d’écran brutes prises depuis le web.
   - `model/` – dossier image contenant (image + toute les class predictible possible).
   - `annotated/` – captures annotées avec les prediction du modèle.
   - `suppression/` – image editer avec les boxes (preditepar le model ) selectionner suprimer.
   - `pretictions_scaled/` – json des prediction du model. 
   - `human_data/` – contient 2 dossiers
   - `human_data/manual` – images + (2json pour chaque img) annoter par le user .
   - `human_data/model` – dossier image contenant (image + toute les class predictible possible).
   - `annotated_by_human/` – image avec les annotation du user.
   - `suppression_human/` – image editer avec les boxes (preditepar le model ) selectionner suprimer.
   - `fine_tune_data/` – données sélectionnées pour le réentraînement du modèle.
   - `fine_tune_backup/` – tous les fichiers du dossier fine_tune_data y son envoyer  pour une sauvegarde pour garder une trace (le model fintuner sera sauvegarder ./output/model_final.pth ).
   - `visited_link.json` – garde une trace des sites visite .



     
Ce flux permet à des utilisateurs non techniques de contribuer à l’amélioration du modèle de détection des 
éléments de page, tout en offrant aux administrateurs les outils nécessaires pour gérer les jeux de données et les cycles d’apprentissage.


```mermaid
flowchart TD
    %% Page d'accueil
    A[🏠 Scrapper Intelligent<br/>Page d'Accueil] --> B{🔐 Connexion}
    
    %% Parcours Utilisateur
    B -->|👤 Utilisateur| C[📝 Saisie URL]
    C --> E[📷 Capture d'écran<br/>avec Playwright]
    E --> F{⚡ Action}
    
    F -->|❓ Question| G{🤖 Assistant IA}
    F -->|💾 Sauvegarder| H{✏️ Modifications?}
    
    G -->|🌟 Gemini| J[🔍 Paddle OCR +<br/>📡 Gemini API]
    G -->|🧠 NLP Classic| K[🔍 Paddle OCR +<br/>⚙️ NLP Classique]
G -->|🧠  Mistral| K1[🔍 Paddle OCR +<br/>⚙️ local Mistral by Ollama ]

    J --> L[✅ Chat bot sur le contenu de l image screener]
    K --> M[✅ Chat bot sur le contenu de l image screener]
   K1 --> M1[✅ Chat bot sur le contenu de l image screener]

    H -->|✅ Oui| O[🎯 Détection Automatique par Modèle IA <br/> et selection des element asupprimer]
    H -->|❌ Non| P[📥 Téléchargement Direct]
    
    O --> Q{🔍 Validation Détection}
    Q -->|✅ Correct| R[🎨 Image editer avec supression des choix<br/>+ Téléchargement]
    Q -->|❌ Incorrect| S[👆 Annotation Manuelle]
    
    S --> T[🖊️ Interface Canvas<br/>Annotation Avancée]
    T --> U{🗑️ choix des  Boxes a Supprimer}
    U --> V[✂️ Sélection Suppression]
    V --> R
    
    %% Parcours Administrateur
    B -->|👨‍💼 Admin| D{🔒 Authentification}
    D -->|✅ Valide| Y[📊 Tableau de Bord<br/>Administrateur]
    D -->|❌ Invalide| D
    
    Y --> Z[🔗 Historique Liens<br/>Sites Visités]
    Y --> AA[🤖 Images Modèle IA<br/>+ Validation User]
    Y --> BB[👤 Images Annotées<br/>par Utilisateurs]
    Y --> CC[📈 Dataset Fine-Tuning<br/>+ Lancement]
    
    %% Gestion images modèle
    AA --> DD[🖼️ Visualisation Image<br/>Sélectionnée]
    DD --> EE[✅ Valider → Dataset]
    DD --> FF[🗑️ Supprimer Définitivement]
    DD --> GG[✏️ Modifier Annotation]
    
    %% Gestion images utilisateur
    BB --> HH[🖼️ Visualisation Image<br/>Sélectionnée]
    HH --> II[✅ Valider → Dataset]
    HH --> JJ[🗑️ Supprimer Définitivement]
    HH --> KK[✏️ Modifier Annotation]
    
    %% Fine-tuning
    CC --> LL[🚀 Lancement Fine-Tuning<br/>🔄 Auto-suppression post-training]
    
    %% Interface annotation admin
    GG --> MM[🎨 Interface Canvas<br/>Annotation Avancée]
    KK --> MM
    
    %% Styles visuels attractifs
    classDef startNode fill:#4CAF50,stroke:#2E7D32,stroke-width:3px,color:#fff
    classDef userPath fill:#2196F3,stroke:#1565C0,stroke-width:2px,color:#fff
    classDef adminPath fill:#9C27B0,stroke:#6A1B9A,stroke-width:2px,color:#fff
    classDef processNode fill:#FF9800,stroke:#E65100,stroke-width:2px,color:#fff
    classDef decisionNode fill:#FFC107,stroke:#F57F17,stroke-width:2px,color:#000
    classDef finalNode fill:#4CAF50,stroke:#2E7D32,stroke-width:3px,color:#fff
    classDef aiNode fill:#E91E63,stroke:#AD1457,stroke-width:2px,color:#fff
    classDef dataNode fill:#607D8B,stroke:#37474F,stroke-width:2px,color:#fff
    
    class A startNode
    class C,E,J,K,T userPath
    class Y,Z,AA,BB,CC,DD,HH,MM adminPath
    class O,S,V,EE,FF,II,JJ,LL processNode
    class B,F,G,H,Q,U,D decisionNode
    class P,R,W,L,M finalNode
    class J,K,O,MM aiNode
    class Z,AA,BB,CC,LL dataNode
