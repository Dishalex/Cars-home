# [Cars-Home](https://cars-home-app-private-student-cf52bc9b.koyeb.app/docs) ![qrcode(1)](https://github.com/Dishalex/Cars-home/assets/131618968/b250accb-1a6b-4a9d-8825-4cf90647e77c)


# Automated Parking Management System

## Overview

This project is a web application designed to automate the management of parking spaces. It provides the following key features:
1. Automatic recognition of vehicle license plates from images.
2. Tracking the duration of parking for each unique vehicle.
3. Calculating accumulated parking charges.

### Additional Features
7. Real-time mobile notifications for each user's vehicle entry/exit events.
8. Graphs and reports on the number of available and occupied parking spots.

## Required Features

1. **User Account Management:**
   - Administrator and regular user roles.
   - Administrator functions: adding/removing registered license plates, setting parking rates, and creating a blacklist of vehicles.
   - User functions: viewing personal license plate information and parking history.

2. **Image Processing:**
   - Accepting images from users.
   - Detecting license plates in images.
   - Extracting and highlighting the license plate area from images.

3. **Optical Character Recognition (OCR):**
   - Identifying text on the license plate.
   - Searching for the license plate number in the registered vehicle database.

4. **Parking Duration Tracking:**
   - Recording entry/exit times whenever a license plate is recognized.
   - Calculating the total parking duration for each unique license plate.

5. **Data Storage:**
   - Storing duration data associated with license plates in a database.
   - Calculating parking costs.

6. **User Notifications:**
   - Notifying users if accumulated parking charges exceed set limits.

7. **Report Generation:**
   - Generating reports on calculations, exportable in CSV format.

## Technical Implementation

- **Backend Framework:** Developed using FastAPI.
- **Computer Vision:** Implemented with TensorFlow/Keras and OpenCV.
- **Database:** PostgreSQL for persistent storage of license plates and data.
- **Real-Time Notifications:** Implemented via a Telegram bot.

## Telegram Bot

You can interact with the application through the Telegram bot: [CarsHomeBot](https://t.me/CarsHomeBot)

## Running the Application

### Prerequisites

Ensure you have the following installed on your machine:
- Python 3.8+
- PostgreSQL
- Virtual environment tool (e.g., `venv` or `virtualenv`)

### Setup

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/yourusername/parking-management-system.git
   cd parking-management-system
   
2. **Create and Activate Virtual Environment:**
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

   
3. **Install Dependencies:**
   pip install -r requirements.txt

   
4. **Configure Database:**
   -   Create a PostgreSQL database.
   -   Update the database connection settings in backend/src/database/db.py.

  
5. **Run Database Migrations:**
   alembic upgrade head

   
6. **Start the Application:**
   uvicorn backend.main:app --reload
   
The application should now be running at http://127.0.0.1:8000.

# [Telegram bot](https://t.me/CarsHomeBot):
![frame](https://github.com/Dishalex/Cars-home/assets/131618968/932cc6c4-52f0-40f0-8094-76236ebb2dfd)

