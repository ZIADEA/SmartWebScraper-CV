# Application Workflow

The SmartWebScraper-CV local app guides the user through a series of pages to capture and annotate websites. Below is a simplified description of how it works.

1. **Home Page**
   - Choose to proceed as an ordinary user or log in as the administrator.

2. **User Path**
   - Enter the URL of a website. The app uses Playwright to take a screenshot.
   - The screenshot is passed through an object detection model which highlights common webpage elements (ads, headers, sidebars, etc.).
   - You can ask a question about the page using ChatGPT or the local NLP engine.
   - Validate or adjust the suggested bounding boxes. You may remove boxes or create new ones using the integrated annotation interface.
   - When finished, the image and its annotations are stored in `human_data/` for review and can be promoted to `fine_tune_data/`.

3. **Admin Path**
   - Log in with the admin credentials.
   - The dashboard lets you:
     - View the history of visited links.
     - Review predictions approved by users.
     - Inspect manual annotations submitted by users.
     - Monitor how many images are available for model fine-tuning.
     - Trigger a fine‑tuning run of the detection model (after which the images in `fine_tune_data/` are cleared).

4. **Data Folders**
   - `originals/` – raw screenshots captured from the web.
   - `annotated/` – screenshots with boxes drawn by the model.
   - `human_data/` – images validated by users or manually annotated.
   - `fine_tune_data/` – images selected for retraining the model.

This workflow allows non‑technical users to contribute data for improving the page element detection model while giving administrators tools to curate the dataset and manage training runs.


```mermaid
flowchart TD
    A[Page 1: Bienvenu dans votre scrapper intelligent] --> B[Se connecter]
    B --> C[Utilisateur --> Page 1.1]
    B --> D[Administrateur --> Page 1.2]
    
    D --> E[Page 1.2: Authentification]
    E -->|Incorrect| E
    E -->|Correct| F[Page 1.2.1: Tableau de bord]
    
    F --> G[Voir les liens des sites --> Page 1.2.1.1]
    F --> H[Voir images annotées par modèle --> Page 1.2.1.2]
    F --> I[Voir images annotées par utilisateur --> Page 1.2.1.3]
    F --> J[Voir nombre d'images fine-tune --> Page 1.2.1.4]
    
    H --> K[Page 1.2.1.2: Liste images]
    K -->|Click image| L[Page 1.2.1.2.1: Affiche image]
    L --> M[Valider --> Envoie fine-tune]
    L --> N[Supprimer]
    L --> O[Modifier --> Page AA]
    
    I --> P[Page 1.2.1.3: Liste images]
    P -->|Click image| Q[Page 1.2.1.3.1: Affiche image]
    Q --> R[Valider --> Envoie fine-tune]
    Q --> S[Supprimer]
    Q --> T[Modifier --> Page AA]
    
    J --> U[Page 1.2.1.4: Affiche nombre]
    U --> V[Lancer fine-tuning]
    
    AA[Page AA: Annotation admin] -->|Sauvegarde| U
    
    C --> W[Page 1.1: Entrer lien]
    W --> X[Page 1.1.2: Capture + options]
    X --> Y[Poser question --> Page 1.1.2.1]
    X --> Z[Sauvegarder --> Page 1.1.2.2]
    
    Y --> Y1[ChatGPT --> Page 1.1.2.1.1]
    Y --> Y2[NLP Classic --> Page 1.1.2.1.2]
    
    Z --> Z1[Modifier? Oui --> Page 1.1.2.2.1]
    Z --> Z2[Non --> Page Tn]
    
    Z1 --> Z11[Page 1.1.2.2.1: Image annotée]
    Z11 --> Z12[Feedback: Bonne détection?]
    Z12 -->|Oui| To
    Z12 -->|Non| FA
    
    FA -->|Oui| B[Page B: Annotation utilisateur]
    B --> B1[Valider --> Page B1]
    B1 --> B11[Supprimer box? Oui --> B1.1]
    B1 --> B12[Non --> Tou]
    
    B1.1 --> To
    To[Page To: Capture annotée]
    Tou[Page Tou: Capture utilisateur]
