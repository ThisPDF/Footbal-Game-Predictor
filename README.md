# Project Name: Football Outcome Predictor

## Overview
This project is a Flask web application designed to interact with datasets and machine learning models. It includes functionality for data visualization, model training, and predictions in the domains of robotics and football.

## Features
- **Web Interface**: Built using Flask.
- **Data Management**: Handles CSV files for robotics and football data.
- **Machine Learning**: Utilizes a pre-trained TensorFlow/Keras model.
- **Custom Utilities**: Additional Python modules enhance functionality.
- **Docker Support**: A pre-built Docker image is available for easy deployment.

## Prerequisites
Ensure you have the following installed:
- Python 3.8 or higher
- pip (Python package installer)
- Docker (optional, if using the Docker image)

## Installation and Setup
Follow these steps to run the project:

### 1. Clone the Repository:
```bash
git clone https://github.com/ThisPDF/Football-Game-Predictor.git
cd Football-Game-Predictor
```

### 2. Install Dependencies:
Install the necessary packages:
```bash
pip install -r requirements.txt
```

### 3. Set Up Directories:
Ensure the following directories exist (if not, create them):
- `./model/`
- `./app/data/`
- `./scraper_data/`

### 4. Run the Application:
Start the Flask server:
```bash
python app.py
```

### 5. Access the Application:
If the browser window does not open automatically, open your web browser and navigate to:
```plaintext
http://127.0.0.1:80/
```

## Running with Docker
Alternatively, you can use the pre-built Docker image to run the application without setting up dependencies manually.

### 1. Pull the Docker Image:
```bash
docker pull eusuntpdf23/data_prediction_app:latest
```

### 2. Run the Docker Container:
```bash
docker run -d -p 8080:80 eusuntpdf23/data_prediction_app:latest
```

### 3. Access the Application:
Once the container is running, open your browser and go to:
```plaintext
http://localhost:8080/
```

## Project Structure
```
app/
├── app.py                 # Main application file
├── scraper.py            # Web scraping script
├── scraper_robotica.py   # Robotics-specific scraper
├── rn_utils.py           # Utility functions
├── templates/            # HTML templates
scraper_data/             # Additional scraped data
model/                    # Contains the trained models
```

## Contributing
Feel free to contribute by submitting issues or pull requests. Make sure to follow the contribution guidelines.

## License
This project is licensed under the MIT License. See `LICENSE` for details.

---

### Notes
- Ensure all necessary CSV files and models are properly placed before running the application.
- If any additional dependencies are required, update `requirements.txt` accordingly.
- If using Docker, ensure you have Docker installed and running before pulling the image.
