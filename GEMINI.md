# Project: online-retail-vizualizacion

## Project Overview

This is a Django project for a university course on "Business Intelligence and Data Mining". The project is in its initial state and appears to be a web application for data visualization related to online retail.

*   **Purpose:** University project for the "Inteligencia de Negocios y Minería de Datos" course.
*   **Main Technologies:** Python, Django 5.2.8
*   **Architecture:** The project follows a standard Django architecture.
    *   It has a single Django app named `dashboard`.
    *   It is configured to use a SQLite database (`db.sqlite3`).
    *   The project is in a very early stage of development, with no models, views, or URLs defined yet.

## Building and Running

Here are the basic commands to get the project running:

1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Apply Database Migrations:**
    ```bash
    python manage.py migrate
    ```

3.  **Run the Development Server:**
    ```bash
    python manage.py runserver
    ```
    The application will be available at `http://127.0.0.1:8000/`.

4.  **Run Tests:**
    ```bash
    python manage.py test
    ```

## Development Conventions

The project is in its early stages, and no specific development conventions have been established yet. Based on the initial files, it follows the standard Django project structure.
