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
   git clone https://github.com/ZIADEA/SmartWebScraper-CV.git   https://github.com/elm19/goldspot-predictor.git
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


## License

This project is licensed under the [MIT License](LICENSE).
