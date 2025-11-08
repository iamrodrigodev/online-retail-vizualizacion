import polars as pl
import functools

# URL del dataset
DATASET_URL = "https://raw.githubusercontent.com/iamrodrigodev/online-retail/main/dataset/retail_with_categories.csv"

@functools.lru_cache(maxsize=None)
def load_online_retail_data():
    """
    Carga el dataset de online retail desde la URL de GitHub.
    Utiliza un caché para evitar descargas repetidas.
    """
    try:
        # Especificar el tipo de dato para la columna 'CustomerID' para evitar errores de inferencia
        df = pl.read_csv(DATASET_URL, dtypes={'CustomerID': pl.Utf8})
        return df
    except Exception as e:
        print(f"Error al cargar el dataset: {e}")
        return pl.DataFrame() # Retorna un DataFrame vacío en caso de error
