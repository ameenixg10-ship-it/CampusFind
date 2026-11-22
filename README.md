# CampusFind – Python Campus Lost & Found Management System

A beginner-friendly web application built with Python, Flask, SQLite, HTML and CSS.

## Features
- Report lost items and found items
- Browse and search reports by item name, category or location
- View item details and submit claim requests
- Admin dashboard to approve/reject claims
- Mark reports as resolved
- SQLite database saves data between runs

## Requirements
- Python 3.9+
- VS Code
- Flask (installed from requirements.txt)

## Run in VS Code
1. Extract the ZIP and open the `CampusFind_Python` folder in VS Code.
2. Open Terminal → New Terminal.
3. (Recommended) Create a virtual environment:

   Windows:
   ```bash
   py -m venv .venv
   .venv\\Scripts\\activate
   ```

   macOS/Linux:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

4. Install Flask:
   ```bash
   python -m pip install -r requirements.txt
   ```
5. Start the app:
   ```bash
   python app.py
   ```
6. Open http://127.0.0.1:5000 in your browser.

The database file `campusfind.db` is created automatically on first run.

## Important security note
This is a learning/demo project. The admin page is not password-protected and the app uses Flask's development server. Do not expose it publicly or use real personal data. Before deployment, add admin authentication, CSRF protection, stronger validation, privacy controls, and production hosting.

## Resume description (after running and understanding it)
**CampusFind – Campus Lost & Found Management System**  
Built a campus lost-and-found web application using Python, Flask and SQLite. Implemented lost/found item reporting, keyword search, claim submission, and an admin dashboard for claim review and report resolution.
