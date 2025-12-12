# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Django web application for business intelligence and data mining visualization of online retail data. Implements RFM-based customer segmentation, K-nearest neighbors similarity analysis, PCA dimensionality reduction, and K-means clustering.

**Course**: INTELIGENCIA DE NEGOCIOS Y MINERÍA DE DATOS
**Institution**: Universidad La Salle de Arequipa

## Development Commands

### Local Development
```bash
# Run development server
python manage.py runserver

# Create and apply migrations
python manage.py makemigrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Collect static files (production)
python manage.py collectstatic
```

### Database Configuration
- **Local**: SQLite (`db.sqlite3`)
- **Production**: PostgreSQL via `DATABASE_URL` environment variable (Railway)
- Auto-detects environment based on `DATABASE_URL` presence

### Testing
No formal test suite configured. Exploratory scripts available:
- `test_clustering.py` - K-means clustering experiments
- `test_pca_variance.py` - PCA variance analysis

## Architecture Overview

### Django Structure
```
core/
├── settings.py    # Dual-mode config (SQLite/PostgreSQL), WhiteNoise
├── urls.py        # API routes
└── wsgi.py        # Gunicorn entry point

dashboard/
├── views.py                       # HTTP handlers, JSON serialization
├── templates/index.html           # Single-page application
├── static/visualizaciones/        # Frontend JS/CSS
└── visualizations/
    ├── shared/data_loader.py      # CSV loading with @lru_cache
    ├── world_map/                 # Choropleth sales by country
    ├── customer_profiles/         # RFM-based segmentation
    ├── sales/                     # Time-series trends
    ├── products/                  # Top products analysis
    └── client_similarity/         # Advanced ML pipeline
        ├── data_processor.py      # Orchestrates pipeline
        ├── preprocessing.py       # Z-score/Min-Max normalization
        ├── distances.py           # Distance matrix computation
        ├── knn.py                 # K-nearest neighbors
        ├── dimensionality.py      # PCA reduction
        ├── clustering.py          # K-means (k=4), outlier detection
        └── plot.py                # Plotly visualization
```

### Data Pipeline
1. **Extract**: `data_loader.py` fetches CSV from GitHub (cached)
2. **Transform**: Visualization modules process data using Polars DataFrames
3. **Load**: Views serialize to JSON with `plotly.utils.PlotlyJSONEncoder`
4. **Render**: Frontend renders with Plotly.js

### Visualization Modules Pattern
Each module follows consistent structure:
- `data_processor.py`: Business logic, data transformations (Polars)
- `plot.py`: Plotly figure generation

## API Endpoints

All JSON-based, defined in `core/urls.py`:

```
GET  /api/customer-profiles/<country>/     # Profiles by country
GET  /api/customer-profiles-global/        # Global profiles
GET  /api/sales-trend/                     # Sales trends
GET  /api/top-products/                    # Top products
POST /api/client-similarity/compute/       # Compute similarity graph
GET  /api/client-similarity/customer-ids/  # Available customer IDs
GET  /api/products-by-customers/           # Products by customer list
```

**Query Parameters** (where applicable):
- `country`: Country code (e.g., "United Kingdom")
- `profile`: Customer profile (e.g., "Minorista Estándar")
- `start_date`, `end_date`: Format `YYYY-MM`

**Note**: Date filters include full last day of `end_date` month.

## Key Algorithms

### 1. Customer Profile Classification (RFM + IQR)
**Location**: `dashboard/visualizations/customer_profiles/data_processor.py:detectar_outliers_iqr()`

Classifies customers into 4 profiles using IQR-based outlier detection:

| Profile | Total Condition | UnitPrice Condition |
|---------|----------------|---------------------|
| Minorista Estándar | ≤ Q3 | ≤ Q3 |
| Mayorista Estándar | > Q3 | ≤ Q3 |
| Minorista Lujo | ≤ Q3 | > Q3 |
| Mayorista Lujo | > Q3 | > Q3 |

**IQR Method**:
```
Q1 = 25th percentile
Q3 = 75th percentile
IQR = Q3 - Q1
Outlier if x > Q3 + 1.5×IQR
```

### 2. Client Similarity Pipeline (ML)
**Location**: `dashboard/visualizations/client_similarity/data_processor.py:compute_client_similarity_graph()`

**Pipeline Steps**:
1. **Feature Engineering**: Calculate 7 RFM metrics per customer
   - Recency (days since last purchase)
   - Frequency (transaction count)
   - Monetary (total spend)
   - TotalQuantity, AvgUnitPrice, AvgOrderValue, UniqueProducts
2. **Normalization**: Z-score (recommended) or Min-Max
3. **Distance Matrix**: Euclidean (default), Cosine, or Pearson
4. **KNN Graph**: Find k-nearest neighbors (configurable k=1-500)
5. **Dimensionality Reduction**: PCA to 2D (preserves ~60-70% variance)
6. **Clustering**: K-means with k=4 (aligns with RFM profiles)
7. **Outlier Detection**: Z-score threshold = 3
8. **Visualization**: Interactive Plotly scatter plot with edges

**Performance Optimizations**:
- `float32` dtype (50% memory reduction)
- Randomized SVD for PCA
- Elkan algorithm for K-means
- Aggressive garbage collection (`gc.collect()`)
- Designed for Railway resource limits

### 3. RFM Metrics
**Recency**: `max(InvoiceDate) + 1 day - last purchase date` (in days)
**Frequency**: Count of distinct `InvoiceNo`
**Monetary**: Sum of `Quantity × UnitPrice`

## Tech Stack

**Backend**:
- Django 5.2.8
- Polars (DataFrame processing, faster than Pandas)
- NumPy, SciPy, scikit-learn (ML algorithms)
- Plotly (chart generation)

**Frontend**:
- Vanilla JavaScript (ES6+)
- Plotly.js (interactive charts)

**Production**:
- Gunicorn (WSGI server)
- WhiteNoise (static file serving with compression)
- Railway (PaaS, PostgreSQL)

## Data Source

**CSV URL**: `https://raw.githubusercontent.com/iamrodrigodev/online-retail/main/dataset/retail_with_categories.csv`

**Loaded via**: `dashboard/visualizations/shared/data_loader.py:load_online_retail_data()`
**Caching**: `@functools.lru_cache` (persists in memory during server uptime)

**Dataset Info**:
- ~541,909 transactions
- ~4,372 unique customers
- 38 countries
- Period: 01/12/2010 - 09/12/2011

## Deployment (Railway)

**Procfile**:
```
web: python manage.py collectstatic --noinput && gunicorn core.wsgi --log-file -
```

**Environment Detection**:
- `DATABASE_URL`: Switches to PostgreSQL
- `RAILWAY_PUBLIC_DOMAIN`: Sets ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS, secure cookies

**Security**:
- CSRF protection enabled
- Secure cookies in production (`CSRF_COOKIE_SECURE`, `SESSION_COOKIE_SECURE`)
- WhiteNoise compressed static files

## Language and Locale

- `LANGUAGE_CODE = 'es-pe'` (Spanish - Peru)
- UI labels, customer profiles, and error messages in Spanish
- Date format: `YYYY-MM` for filters, `YYYY-MM-DD HH:MM:SS` internally

## Important Implementation Notes

### When Working with Visualizations
1. **Always use Polars**: Preferred over Pandas for performance
2. **Date Handling**: Convert `InvoiceDate` to `pl.Datetime` early in pipeline
3. **Filter Order**: Apply country/date filters before aggregations
4. **Memory**: Use `float32` for large matrices, call `gc.collect()` after heavy ops

### When Adding New Visualizations
1. Create module under `dashboard/visualizations/`
2. Implement `data_processor.py` (returns processed data) and `plot.py` (returns Plotly figure)
3. Add view in `dashboard/views.py`
4. Register endpoint in `core/urls.py`
5. Update frontend in `dashboard/static/visualizaciones/js/index.js`

### Client Similarity Specific
- **Default Parameters**: k=10, metric=euclidean, normalization=z-score, reduction=PCA
- **4 Clusters**: Intentionally matches 4 RFM profiles (not a coincidence)
- **Clusters ≠ Profiles**: K-means clusters use 7D features, profiles use 2D IQR rules
- **PCA Loadings**: PC1 typically dominated by Monetary/AvgOrderValue, PC2 by Frequency/Recency
- **Outliers Visualization**: Diamond markers (vs. circles), larger size, black border

### Performance Considerations
- **CSV Caching**: First load ~2-5s, subsequent <100ms (in-memory cache)
- **Similarity Computation**: n=1000 → 2-3s, n=5000 → 8-12s (includes PCA, K-means)
- **Railway Limits**: Optimizations target 512MB-1GB memory, <30s response times
