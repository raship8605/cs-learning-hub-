# CS Learning Hub

Online Learning Platform for Computer Science students built with Django and MySQL.

## Features

- User Authentication (Login/Register)
- YouTube Video Library with Subject Filter
- Study Notes Download System
- Timed Online Quizzes with Instant Results
- Previous Year Papers Repository
- YouTube Video Library with Subject Filter
- Student Dashboard with Progress Tracking
- Admin Panel for Content Management

## Tech Stack

- Backend: Python, Django
- Database: MySQL
- Frontend: HTML, CSS, Bootstrap, JavaScript

## Installation

```bash
# Clone repository
git clone https://github.com/raship8605/cs-learning-hub.git

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run server
python manage.py runserver
