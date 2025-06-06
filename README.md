# SmartWebScraper-CV

## Features

- **Data Collection**: Automatically capture website screenshots using Playwright or Selenium.
- **Data Annotation**: Use pretrained models or manual tools to annotate web page regions (headers, footers, ads, media, etc.).
- **Model Training**: Fine-tune object detection models (e.g., Faster R-CNN) using COCO-formatted data.
- **Evaluation & Backtesting**: Assess model performance on annotated images.
- **Deployment**: Serve predictions and postprocessing via a Flask web interface.

## Repository Structure

```
📂 SmartWebScraper-CV
├── 📂 data                 # Images and COCO data (originals, annotated, fine-tune data)
├── 📂 notebooks            # Jupyter notebooks for training, evaluation, etc.
├── 📂 models               # Trained models and saved weights
├── 📂 scripts              # Scripts for data collection, annotation, preprocessing
├── 📂 api                  # Deployment API (Flask/FastAPI) — to be implemented
├── 📂 reports              # Project summaries, metrics, diagrams
├── .gitignore              # Git ignore rules
├── README.md               # Project documentation
```

## Requirements

- Python 3.x
- Flask
- OpenCV
- Detectron2
- PaddleOCR
- Playwright or Selenium
- COCO API
- (Full list in `requirements.txt`)

## Getting Started

1. **Clone the repository**:
   ```bash
   git clone https://github.com/ZIADEA/SmartWebScraper-CV.git
   cd SmartWebScraper-CV
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install local app dependencies**:
   ```bash
   cd LocalApp/SMARTWEBSCRAPPER-CV
   pip install -r requirements.txt
   ```

## Admin Credentials

The admin dashboard requires credentials that can be supplied either as **environment variables** or through a **JSON config file** at the project root.

### Option 1 — Environment variables

```bash
export ADMIN_EMAIL="admin@example.com"
export ADMIN_PASSWORD="your_password"
```

### Option 2 — Configuration file

Create a file named `admin_config.json` at the root, based on `admin_config.json.example`:

```json
{
  "email": "admin@example.com",
  "password": "your_password"
}
```

## Launching the Flask App

From `LocalApp/SMARTWEBSCRAPPER-CV`:

```bash
python run.py
```

The application will be available at: [http://localhost:5000](http://localhost:5000)

The app will automatically create the following folders:
- `originals/`
- `resized/`
- `annotated/`
- `predictions_raw/`
- `predictions_scaled/`
- `human_data/`
- `fine_tune_data/`
- `visited_links.json` (for web scraping tracking)

## Documentation

Detailed documentation is available in the [`docs/`](docs) folder.

To build the HTML documentation:

```bash
cd docs
make html
```

Then open:

```bash
docs/build/html/index.html
```

## License

This project is licensed under the [MIT License](LICENSE).
