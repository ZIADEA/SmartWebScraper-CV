# SmartWebScraper-CV Local App

This directory contains the Flask web interface for SmartWebScraper-CV. The application lets you capture web pages, annotate them and manage the data used to train detection models.

## Prerequisites to run it locally

- **Python 3.9 or higher** installed on your computer.
- A command prompt/terminal window (Command Prompt on Windows or Terminal on macOS/Linux).
- Optionally **Git** if you want to clone the repository.

## Installation

1. **Download the project**
   - If you use Git:
     ```bash
     git clone https://github.com/ZIADEA/SmartWebScraper-CV.git
     ```
   - Or download the ZIP archive from GitHub and unzip it.

2. **Open a terminal** and go to the local app folder:
   ```bash
   cd SmartWebScraper-CV/LocalApp/SMARTWEBSCRAPPER-CV
   ```

3. **(Optional) Create a virtual environment** to keep the dependencies isolated:
   ```bash
   python -m venv venv
   ```
   - On Windows run: `venv\Scripts\activate`
   - On macOS/Linux run: `source venv/bin/activate`

4. **Install the required packages** (this can take a few minutes):
   ```bash
   pip install -r requirements.txt
   ```

5. **Install Playwright browsers** (only needed the first time):
   ```bash
   playwright install
   ```

6. **Configure the admin account**. You can either set environment variables or edit the `admin_config.json` file provided in this directory:
   ```bash
   export ADMIN_EMAIL="admin@example.com"
   export ADMIN_PASSWORD="your_password"
   ```
   *(On Windows use `set` instead of `export`.)*

## Running the Application

0. you need to create your own gemini API key and put il on en .env file .
   refere to this link for guid https://dev.to/explinks/how-to-obtain-a-gemini-api-key-step-by-step-guide-4m97
   
1.for the local LLM `MISTRAL` you need to install Ollama  from https://ollama.com/ , ollama is an open-source tool that runs large language models (LLMs) directly on a local machine.
Download and install Ollama.

Then, in a terminal run : 
   ```bash
   ollama run mistral
   ```
2. Still inside `LocalApp/SMARTWEBSCRAPPER-CV`, start the server:
   ```bash
   python run.py
   ```

3. Open your web browser and visit [http://localhost:5000](http://localhost:5000). You should see the SmartWebScraper interface.

4. To stop the application press `Ctrl+C` in the terminal window.

## Generated Folders

When the app runs it automatically creates a `data/` folder with several subdirectories to store images and annotations:

```
originals/
resized/
annotated/
predictions_raw/
predictions_scaled/
human_data/
fine_tune_data/
```

These directories keep the screenshots and labeled data used for model training.

For a description of how the different pages of the application interact, see [WORKFLOW.md](WORKFLOW.md).
