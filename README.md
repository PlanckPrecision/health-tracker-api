# health-tracker-api
Building a web app that tracks weight. Calculates descriptive measures and trends, allowing the user to track weight in a simple manner. Yet, key measures are displayed. 

Also implements forecasting.

Project Overview
A Flask web application for tracking weight with features like user authentication, weight entry logging, and analytics including descriptive statistics and trend forecasting.

Root Level Files
File	Purpose
main.py	Entry point that creates and runs the Flask app with debug mode enabled

README.md	Project description explaining it's a weight tracking app with metrics and forecasting

requirements.txt	Lists all Python dependencies (Flask, SQLAlchemy, Flask-Login, etc.)

LICENSE	Project license file

App Folder Structure

app/init.py
Initializes the Flask application
Sets up SQLAlchemy database (uses in-memory SQLite)
Configures Flask-Login for user authentication
Registers blueprints (auth and entries routes)
Creates all database tables on startup

Sets up the Flask server, database, and authentication system and registers your routes so everything can run.

app/models.py
Two database models:

User: Stores username and hashed password; has relationship to entries
Entry: Stores weight, date, and user_id (can be null for anonymous entries)

Defines the database schema (the structure of what gets stored). It creates the User and Entry classes that represent tables in your database. User input is actually gathered in the routes files.

app/validate.py
Validation functions:

check_weight() - Validates weight input (0-500 range, max 2 decimals, accepts comma or period)
check_date() - Validates date format (DD.MM.YYYY), defaults to today
is_valid_password() - Ensures password is 6+ chars with letters and special characters

Contains your validation helper functions that check if user input (weight, date, password) meets your requirements before it's saved.

Routes (app/routes/)

auth.py - Authentication endpoints
/signup - User registration with password validation
/login - User login with credential verification
/logout - User logout
Includes load_user() function for Flask-Login

entries.py - Weight tracking endpoints
/ - Home page (index) showing today's date
/register (POST) - Records a new weight entry
/history - Shows weight history (filtered by logged-in user or anonymous entries)

Templates (app/templates/)
Template	Purpose
base.html	Base template extended by other pages
index.html	Main page to enter weight and view last entry
login.html	User login form
signup.html	User registration form
history.html	Displays weight entry history

Static Assets (app/static/)
File	Purpose
styles.css	Compiled CSS styling
styles.scss	Source SCSS styling (uncompiled version)
datepicker.js	JavaScript for date selection

Database
Uses SQLite (in-memory during development)
Two tables: users and entries
User entries are linked by user_id; anonymous entries supported