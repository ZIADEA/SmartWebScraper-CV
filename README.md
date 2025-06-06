# SmartWebScraper-CV


## Features

- **Data Collection**: 
- **Data Annotation**: 
- **Model Training**:
- **Evaluation & Backtesting**: Assess model performance on historical data.
- **Deployment**: Deploy the trained model via API or web interface.

## Repository Structure

```
📂 SmartWebScraper-CV
├── 📂 data                 # images and COCO data
├── 📂 notebooks            # Jupyter notebooks 
├── 📂 models               # Trained models and saved weights
├── 📂 scripts              # scripts used for data collection, data annotaition .
├── 📂 api                  # Deployment API (Flask/FastAPI)(LATER)
├── 📂 reports              # resume of project and results
├── .gitignore              # Git ignore file
├── README.md               # Project documentation


## Requirements

- Python 3.x
- 
- 
- Flask/FastAPI (for deployment)

## Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/ZIADEA/SmartWebScraper-CV.git
   cd SmartWebScraper-CV
   ```
   
  
  
challenges: 
1 - data collect

2 - images annotation

## Admin Credentials

The admin dashboard requires credentials that can be supplied either as environment variables or through a configuration file placed at the repository root.

### Using environment variables

Set `ADMIN_EMAIL` and `ADMIN_PASSWORD` before starting the application:

```bash
export ADMIN_EMAIL="admin@example.com"
export ADMIN_PASSWORD="secret"
```

### Using a config file

Create an `admin_config.json` file based on the provided `admin_config.json.example` and populate it with the desired credentials.

## Setup and Installation

Follow these steps to configure a local environment:

1. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # on Windows use venv\Scripts\activate
   ```
2. **Install the project dependencies**
   ```bash
   pip install -r requirement.txt
   ```
3. **Install the requirements for the local Flask interface**
   ```bash
   cd LocalApp/SMARTWEBSCRAPPER-CV
   pip install -r requirements.txt
   ```

## Launching the Local Flask App

1. Make sure your admin credentials are set (environment variables or `admin_config.json`).
2. From the `LocalApp/SMARTWEBSCRAPPER-CV` directory run:
   ```bash
   python run.py
   ```
   The application will be accessible at [http://localhost:5000](http://localhost:5000).

The app automatically creates an `app/data` directory within `LocalApp/SMARTWEBSCRAPPER-CV` on first launch. Subdirectories include `originals`, `resized`, `annotated`, `predictions_raw`, `predictions_scaled`, `human_data` and `fine_tune_data`. A `visited_links.json` file is also generated to store crawled URLs.

## Documentation

Detailed explanations of the project architecture and usage can be found in the [`docs/`](docs) directory. You can build the HTML version with:

```bash
cd docs
make html
```

Open `docs/build/html/index.html` in your browser to explore the full documentation.

