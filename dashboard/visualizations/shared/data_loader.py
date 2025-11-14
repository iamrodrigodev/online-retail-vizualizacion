import polars as pl
import functools
import sys

# URL del dataset
DATASET_URL = "https://raw.githubusercontent.com/iamrodrigodev/online-retail/main/dataset/retail_with_categories.csv"

@functools.lru_cache(maxsize=None)
def load_online_retail_data():
    """
    Carga el dataset de online retail desde la URL de GitHub.
    Utiliza un caché para evitar descargas repetidas.
    """
    try:
        print(f"Intentando cargar dataset desde: {DATASET_URL}", file=sys.stderr)
        # Especificar el tipo de dato para la columna 'CustomerID' para evitar errores de inferencia
        df = pl.read_csv(DATASET_URL, dtypes={'CustomerID': pl.Utf8})
        print(f"Dataset cargado exitosamente: {df.height} filas, {df.width} columnas", file=sys.stderr)
        return df
    except Exception as e:
        print(f"ERROR al cargar el dataset: {type(e).__name__}: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return pl.DataFrame() # Retorna un DataFrame vacío en caso de error
