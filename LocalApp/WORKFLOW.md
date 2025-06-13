# Application Workflow

L’application locale **SmartWebScraper-CV**
guide l’utilisateur à travers une série d’étapes pour capturer et annoter des sites web. Ci-dessous, une description simplifiée de son fonctionnement.

1. **Home Page**
   - Choisissez de continuer en tant qu’utilisateur standard ou connectez-vous en tant qu’administrateur.

2. **User Path**
   - Entrez l’URL d’un site web. L’application utilise **Playwright** pour capturer une capture d’écran.
   - Cette image est ensuite traitée par un modèle de détection d’objets qui met en évidence les éléments courants d’une page web (publicités, en-têtes, barres latérales, etc.).
   - Vous pouvez poser une question sur la page en utilisant **ChatGPT** ou le moteur NLP local.
   - Validez ou modifiez les zones de détection proposées. Il est possible de supprimer des boîtes ou d’en créer de nouvelles via l’interface d’annotation intégrée.
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
   - `annotated/` – captures annotées automatiquement par le modèle.
   - `human_data/` – images validées ou annotées manuellement par les utilisateurs.
   - `fine_tune_data/` – données sélectionnées pour le réentraînement du modèle.

Ce flux permet à des utilisateurs non techniques de contribuer à l’amélioration du modèle de détection des éléments de page, tout en offrant aux administrateurs les outils nécessaires pour gérer les jeux de données et les cycles d’apprentissage.


```mermaid
flowchart TD
    %% ========== ADMIN FLOW ==========
    A[Page 1: Bienvenu<br>dans votre scrapper intelligent]:::main
    B[Se connecter]:::neutral
    C[Utilisateur]:::user
    D[Administrateur]:::admin
    
    A --> B
    B --> C --> W
    B --> D --> E
    
    E[Page 1.2:<br>Authentification<br>Mail: djeryala@gmail.com<br>MDP: DJERI]:::auth
    E -->|Incorrect| E
    E -->|Correct| F
    
    F[Page 1.2.1:<br>Tableau de bord]:::dashboard
    F --> G[Voir les liens<br>des sites]:::link
    F --> H[Voir images<br>annotées modèle]:::model
    F --> I[Voir images<br>annotées user]:::userimg
    F --> J[Voir nb images<br>fine-tune]:::counter
    
    G --> 1.2.1.1[Page 1.2.1.1:<br>Liens des sites]:::linkpage
    H --> K[Page 1.2.1.2:<br>Liste images modèle] --> L[Page 1.2.1.2.1:<br>Image annotée modèle]:::modelview
    I --> P[Page 1.2.1.3:<br>Liste images user] --> Q[Page 1.2.1.3.1:<br>Image annotée user]:::userview
    J --> U[Page 1.2.1.4:<br>Nb images fine-tune]:::counterpage
    
    L --> M[Valider<br>→ fine-tune data]:::validate
    L --> N[Supprimer<br>image+json]:::delete
    L --> O[Modifier<br>annotation] --> AA[Page AA:<br>Annotation admin]:::annotation
    
    Q --> R[Valider<br>→ fine-tune data]:::validate
    Q --> S[Supprimer<br>image+json]:::delete
    Q --> T[Modifier<br>annotation] --> AA
    
    U --> V[Lancer<br>fine-tuning]:::action
    
    %% ========== USER FLOW ==========
    W[Page 1.1:<br>Entrer lien]:::input
    W --> X[Page 1.1.2:<br>Capture + options]:::capture
    X --> Y[Poser question] --> Y1[Page 1.1.2.1.1:<br>ChatGPT]:::chatgpt
    Y --> Y2[Page 1.1.2.1.2:<br>NLP Classic]:::nlp
    X --> Z[Sauvegarder] --> Z1[Modifier?]:::modify
    Z1 -->|Oui| Z11[Page 1.1.2.2.1:<br>Image annotée modèle] --> Z12[Feedback] -->|Oui| To[Page To:<br>Capture annotée]
    Z12 -->|Non| FA[Page FA:<br>Annoter vous-même?]:::feedback
    FA -->|Oui| B[Page B:<br>Interface annotation]:::annotation
    B --> B1[Valider] --> B11[Supprimer box?]
    B11 -->|Oui| B1.1[Modifier annotations] --> To
    B11 -->|Non| Tou[Page Tou:<br>Capture user]
    Z1 -->|Non| Tn[Page Tn:<br>Télécharger image]

    %% ========== STYLE DEFINITIONS ==========
    classDef main fill:#2E0249,color:white,stroke:#000
    classDef neutral fill:#937DC2,color:black
    classDef user fill:#1A5F7A,color:white
    classDef admin fill:#C70039,color:white
    classDef auth fill:#F99417,color:black
    classDef dashboard fill:#3E001F,color:white
    classDef link fill:#293462,color:white
    classDef model fill:#1C6758,color:white
    classDef userimg fill:#7D1E6A,color:white
    classDef counter fill:#3E6D9C,color:white
    classDef linkpage fill:#408E91,color:black
    classDef modelview fill:#245953,color:white
    classDef userview fill:#A13333,color:white
    classDef counterpage fill:#1E5128,color:white
    classDef validate fill:#2D6E3C,color:white
    classDef delete fill:#D82148,color:white
    classDef annotation fill:#5B2A00,color:white
    classDef action fill:#EC9B3B,color:black
    classDef input fill:#1D5D9B,color:white
    classDef capture fill:#39AEA9,color:black
    classDef chatgpt fill:#3A1078,color:white
    classDef nlp fill:#4E31AA,color:white
    classDef modify fill:#7F5283,color:white
    classDef feedback fill:#F24C4C,color:black
