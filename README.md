# Project Name: Football outcome predictor

## Overview
This project is a Flask web application designed to interact with datasets and machine learning models. It includes functionality for data visualization, model training, and predictions in the domains of robotics and football.

## Features
- **Web Interface**: Built using Flask.
- **Data Management**: Handles CSV files for robotics and football data.
- **Machine Learning**: Utilizes a pre-trained TensorFlow/Keras model.
- **Custom Utilities**: Additional Python modules enhance functionality.

## Prerequisites
Ensure you have the following installed:
- Python 3.8 or higher
- pip (Python package installer)

## Installation and Setup
Follow these steps to run the project:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/ThisPDF/Footbal-Game-Predictor.git
   cd Footbal-Game-Predictor.git
   ```

2. **Install Dependencies**:
   Install the necessary packages:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up Directories**:
   Ensure the following directories exist (if not, create them):
   - `./model/`
   - `./app/data/`
   - `./scraper_data/`

4**Run the Application**:
   Start the Flask server:
   ```bash
   python app.py
   ```

6. **Access the Application**:
   If the browser window dose not open automatically
   Open your web browser and navigate to `http://127.0.0.1:5001/`.

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
