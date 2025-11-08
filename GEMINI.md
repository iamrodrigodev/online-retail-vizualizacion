# Project Overview

This is a Django-based web application designed for visualizing the "Online Retail Dataset". The project is intended to be a dashboard for data analysis and visualization, likely for a university project in a "Business Intelligence and Data Mining" course.

The application is built with Python and the Django framework. The frontend uses HTML, CSS, and JavaScript, with the Plotly.js library for creating interactive charts. The project is configured for deployment using Gunicorn and Whitenoise.

## Building and Running

### Prerequisites

*   Python 3
*   pip

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd online-retail-vizualizacion
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### Running the application

1.  **Apply the database migrations:**
    ```bash
    python manage.py migrate
    ```

2.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```

The application will be available at `http://127.0.0.1:8000/`.

## Development Conventions

*   The project follows the standard Django project structure.
*   The main application logic is contained within the `dashboard` app.
*   Static files (CSS, JavaScript, images) are located in the `dashboard/static/visualizaciones` directory.
*   Templates are located in the `dashboard/templates` directory.
*   The project is configured to use a SQLite database by default, but can be configured to use PostgreSQL for production.
*   The `index.js` file is currently empty, so the visualizations are not yet implemented.
