"""
Módulo de clustering (KMeans)
"""
import numpy as np
from sklearn.cluster import KMeans


def apply_kmeans_clustering(X, n_clusters=5, random_state=42):
    """
    Aplica KMeans clustering a los datos (optimizado para grandes datasets)
    
    Args:
        X: matriz numpy de forma (n_samples, n_features)
        n_clusters: número de clusters a crear
        random_state: semilla aleatoria para reproducibilidad
    
    Returns:
        array de etiquetas de cluster (n_samples,)
    """
    # Ajustar número de clusters si hay pocos datos
    n_samples = X.shape[0]
    n_clusters = min(n_clusters, n_samples)
    
    if n_clusters < 2:
        # Si hay muy pocos datos, asignar todos al mismo cluster
        return np.zeros(n_samples, dtype=int)
    
    # Usar algoritmo optimizado para grandes datasets
    if n_samples > 1000:
        # Usar algoritmo 'elkan' que es más rápido para muchas muestras
        kmeans = KMeans(n_clusters=n_clusters, random_state=random_state, 
                       n_init=10, algorithm='elkan', max_iter=100)
    else:
        kmeans = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    
    return kmeans.fit_predict(X)


def detect_outliers_isolation_forest(X, contamination=0.1, random_state=42):
    """
    Detecta outliers usando Isolation Forest
    
    Args:
        X: matriz numpy de forma (n_samples, n_features)
        contamination: proporción de outliers esperada
        random_state: semilla aleatoria para reproducibilidad
    
    Returns:
        array booleano indicando outliers (True = outlier)
    """
    from sklearn.ensemble import IsolationForest
    
    iso_forest = IsolationForest(contamination=contamination, random_state=random_state)
    predictions = iso_forest.fit_predict(X)
    
    # -1 indica outlier, 1 indica inlier
    return predictions == -1


def detect_outliers_statistical(X, threshold=3):
    """
    Detecta outliers usando el método estadístico de Z-score (optimizado)
    
    Args:
        X: matriz numpy de forma (n_samples, n_features)
        threshold: umbral de desviación estándar (default 3)
    
    Returns:
        array booleano indicando outliers (True = outlier)
    """
    # Calcular z-scores de forma vectorizada
    mean = np.mean(X, axis=0)
    std = np.std(X, axis=0)
    std[std == 0] = 1  # Evitar división por cero
    
    z_scores = np.abs((X - mean) / std)
    
    # Un punto es outlier si alguna característica excede el umbral
    # Usar operaciones numpy optimizadas
    return np.any(z_scores > threshold, axis=1)
