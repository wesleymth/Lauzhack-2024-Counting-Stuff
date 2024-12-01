# Lauzhack-2024

## Overview
Welcome to the Lauzhack-2024 project repository! This project focuses on monitoring oil storage facilities using satellite imagery and geospatial analysis with Google Earth. 
Beyond oil storage, the platform's versatile AI-powered tools enable you to count and analyze a wide range of objects, such as ships, people, books, and more, making it adaptable for various use cases.
With a combination of advanced detection models and an intuitive interface, this project offers powerful insights for monitoring and decision-making.

## Features
- Satellite Imagery Analysis: Seamlessly integrates with Google Earth to access and analyze high-resolution satellite images of oil storage facilities.
- Advanced Detection with YOLOv11: Utilizes the state-of-the-art YOLOv11 model for precise detection and analysis of oil storage infrastructure.
- Intelligent Chatbot: Incorporates LLama 3.2 8B with function-calling capabilities to assist in plot creation and navigation.
- Interactive Web Interface: A user-friendly Flask-powered platform that combines visualizations of Google Earth imagery with chatbot functionality for an enhanced user experience.

## Installation Steps
```sh
# Navigate to directory
cd .../Lauzhack-2024

# Create a new conda environment with Python 3.12
conda create -n lauz24 python=3.12

# Activate the environment
conda activate lauz24

# Install the required dependencies
pip install -r requirements.cv.txt
pip install -r requirements.flask.txt
pip install -r requirements.llms.txt

# # Install local src package
pip install -e .
```

Monitor Oil Storage Using Google Earth
