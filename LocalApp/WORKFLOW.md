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
