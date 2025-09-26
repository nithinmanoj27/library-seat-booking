# Library Seat Booking System

## Overview
This project is a Library Seat Booking System built with Flask for the backend and simple HTML, CSS, and JavaScript for the frontend.  
It allows students to check seat availability, hold seats, confirm bookings, and release them.  
An ETL pipeline is included to extract, transform, and load booking data for reporting purposes.

## Features
- User registration and login with ERP and password
- View seat availability in real time
- Hold a seat temporarily before confirming
- Confirm or release bookings
- Reset all seats for testing
- ETL pipeline to export data from the database into CSV

## Architecture
- Frontend: HTML, CSS, JavaScript (fetch API)
- Backend: Flask, Flask-JWT-Extended, Flask-SocketIO
- Database: SQLite or MySQL
- ETL: Python, Pandas

## Installation and Setup

1. Clone the repository
   ```bash
   git clone https://github.com/nithinmanoj27/library-seat-booking.git
   cd library-seat-booking/backend

## Create and activate a virtual environment
- python -m venv venv
- venv\Scripts\activate   # On Windows
- source venv/bin/activate  # On Linux/Mac

## Install dependencies
- pip install -r requirements.txt

## Start the backend server
- python app.py

## Open the frontend
- Navigate to frontend/login.html in a browser.
- Login with ERP credentials.

## ETL Pipeline
- Run the ETL pipeline to extract booking and seat data into a CSV file
- cd library-seat-booking
  python etl/etl_pipeline.py

## Project Structure
library-seat-booking/
│
├── backend/              # Flask backend
│   ├── app.py
│   ├── routes.py
│   ├── models.py
│   ├── auth.py
│   └── config.py
│
├── frontend/             # Frontend pages
│   ├── login.html
│   └── seats.html
│
├── etl/                  # ETL pipeline
│   └── etl_pipeline.py
│
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation
