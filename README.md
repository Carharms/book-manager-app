# **MY DIGITAL LIBRARY APP**

# Description

A small-scale simple web app with the following features.

- Dashboard: For reading statistics and recently read books
- Adding Books: Record books with a subset of information
- Updating Books: Alter the information tied to a priorly read book
- Deleting Books: Removing books from your digital library
- Reading Goal Progress: Read more - track towards a yearly goal of 24 books

# Requirements

- Python 3.7+
- Flask 2.3.3
- SQLite (included with Python)

# Install Instructions

- Clone or download the project files
- Create a virtual environment:
> bashpython -m venv venv'
> source venv/bin/activate
> On Windows: venv\Scripts\activate

- Install dependencies:
> bashpip install -r requirements.txt

- Create the templates directory and add HTML files:
> bashmkdir templates

- Run the application:
> bashpython app.py

- Access the application:
> Open your browser and go to http://localhost:5000

# Usage Instructions for API's

> GET / - Dashboard homepage
> GET /add - Add new book form
> POST /add - Submit new book
> GET /update/<id> - Edit book form
> POST /update/<id> - Submit book updates
> POST /delete/<id> - Delete book


# Jenkins Instructions

Plugins
- Git
- Pipeline
- OWASP MArkup Formatter Plugin
- Coverage
- Warnings
- FIND OTHERS?


# Development Notes

- SQLite is used as a simple DB tool
- Database is created automatically on initialization
- Flash messages provide responses to actions
- Standard HTML/CSS styling for rudimentary UI
- HTML5 handles form validatation