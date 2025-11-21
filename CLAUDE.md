# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Django web application for business intelligence and data mining visualization of online retail data. The application fetches data from an external CSV source and provides interactive visualizations including world maps, customer profiles, sales trends, product analytics, and client similarity analysis.

**Course**: INTELIGENCIA DE NEGOCIOS Y MINERÍA DE DATOS
**Institution**: Universidad La Salle de Arequipa

## Architecture

### Django Structure
- **core/**: Django project configuration
  - `settings.py`: Configured for both local (SQLite) and production (Railway with PostgreSQL)
  - `urls.py`: Routes API endpoints and main index view
- **dashboard/**: Main application containing all visualization logic
  - `views.py`: Handles HTTP requests, orchestrates visualization generation, returns JSON responses
  - `visualizations/`: Modular visualization packages (see below)
  - `templates/index.html`: Single-page application with interactive Plotly charts
  - `static/visualizaciones/`: Frontend JavaScript and CSS

### Data Flow
1. `shared/data_loader.py` fetches CSV from GitHub URL (cached with `@functools.lru_cache`)
2. Each visualization module has a `data_processor.py` and `plot.py`
3. Data processor transforms raw data using Polars DataFrames
4. Plot modules generate Plotly figures as JSON
5. Views serialize with `plotly.utils.PlotlyJSONEncoder` and pass to frontend
6. Frontend uses Plotly.js to render interactive charts

### Visualization Modules

Each visualization module under `dashboard/visualizations/` follows the same pattern:

- **shared/**: `data_loader.py` - Centralized data loading with caching
- **world_map/**: Choropleth map of sales by country
- **customer_profiles/**: RFM-based customer segmentation (Minorista/Mayorista × Estándar/Lujo)
- **sales/**: Time-series sales trends with filters
- **products/**: Top products analysis with filters
- **client_similarity/**: Advanced KNN-based customer similarity analysis
  - `data_processor.py`: RFM feature engineering, orchestrates the pipeline
  - `preprocessing.py`: Z-score and min-max normalization
  - `distances.py`: Euclidean, cosine, and Pearson distance matrices
  - `knn.py`: K-nearest neighbors graph construction
  - `dimensionality.py`: PCA dimensionality reduction
  - `clustering.py`: K-means clustering and outlier detection
  - `plot.py`: Interactive 2D scatter plots with edges

### Frontend Architecture
- Single-page application in `dashboard/templates/index.html`
- `dashboard/static/visualizaciones/js/index.js` handles:
  - Country selection from world map clicks
  - Customer profile filtering via bar chart clicks
  - Date range filtering with dual sliders
  - Dynamic chart updates via fetch API
  - Client similarity visualization with configurable parameters

### API Endpoints

All visualization data is served through JSON APIs in `core/urls.py`:

- `GET /api/customer-profiles/<country>/` - Customer profiles by country
- `GET /api/customer-profiles-global/` - Global customer profiles
- `GET /api/sales-trend/` - Sales trends (filterable by country, profile, dates)
- `GET /api/top-products/` - Top products (filterable by country, profile, dates)
- `POST /api/client-similarity/compute/` - Compute similarity graph
- `GET /api/client-similarity/customer-ids/` - Get available customer IDs

Query parameters: `country`, `profile`, `start_date`, `end_date` (format: `YYYY-MM`)

## Development Commands

### Local Development
```bash
python manage.py runserver
```

### Database
```bash
python manage.py migrate              # Apply migrations
python manage.py makemigrations       # Create new migrations
python manage.py createsuperuser      # Create admin user
```

### Static Files
```bash
python manage.py collectstatic        # Collect static files for production
python manage.py collectstatic --noinput  # Non-interactive (used in Procfile)
```

### Testing
No formal test suite is configured. The repository contains exploratory scripts:
- `test_clustering.py` - K-means clustering experiments
- `test_pca_variance.py` - PCA variance analysis

## Deployment

Configured for Railway deployment (see `Procfile` and `core/settings.py`):
- Uses Gunicorn WSGI server
- WhiteNoise for static file serving
- PostgreSQL via `DATABASE_URL` environment variable
- CSRF and session cookies secured when `RAILWAY_PUBLIC_DOMAIN` is set

**Procfile command**:
```
web: python manage.py collectstatic --noinput && gunicorn core.wsgi --log-file -
```

## Dependencies

- **Django 5.2.8**: Web framework
- **Polars**: High-performance DataFrame library (used instead of Pandas)
- **Plotly**: Interactive visualization library
- **NumPy, SciPy, scikit-learn**: Scientific computing and ML algorithms
- **gunicorn, whitenoise**: Production WSGI server and static files
- **dj-database-url, psycopg2-binary**: PostgreSQL support

## Data Source

Dataset URL: `https://raw.githubusercontent.com/iamrodrigodev/online-retail/main/dataset/retail_with_categories.csv`

Loaded via `load_online_retail_data()` in `dashboard/visualizations/shared/data_loader.py`

## Key Implementation Details

### Customer Profile Classification
Uses IQR-based outlier detection on `Total` and `UnitPrice` columns to classify customers into four profiles:
- Minorista Estándar (standard retail)
- Mayorista Estándar (standard wholesale)
- Minorista Lujo (luxury retail)
- Mayorista Lujo (luxury wholesale)

Logic in `dashboard/visualizations/customer_profiles/data_processor.py:detectar_outliers_iqr()`

### Client Similarity Pipeline
1. Prepare RFM features from transaction data
2. Apply normalization (z-score or min-max)
3. Compute distance matrix (Euclidean, cosine, or Pearson)
4. Find K-nearest neighbors
5. Apply PCA for 2D visualization
6. Optional K-means clustering
7. Generate interactive scatter plot with edges

All orchestrated in `dashboard/visualizations/client_similarity/data_processor.py:compute_client_similarity_graph()`

### Date Filtering
All visualizations support `start_date` and `end_date` parameters in `YYYY-MM` format. The application converts these to datetime ranges including the full last day of `end_date` month.

## Language and Locale

- `LANGUAGE_CODE = 'es-pe'` (Spanish - Peru)
- UI text, labels, and customer profile names are in Spanish
