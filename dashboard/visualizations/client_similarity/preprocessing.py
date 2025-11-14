"""
Módulo de preprocesamiento para normalización de datos
"""
import numpy as np


def normalize_zscore(X):
    """
    Normalización Z-Score (estandarización)
    
    Args:
        X: matriz numpy de forma (n_samples, n_features)
    
    Returns:
        matriz normalizada con media 0 y desviación estándar 1
    """
    mean = np.mean(X, axis=0)
    std = np.std(X, axis=0)
    # Evitar división por cero
    std[std == 0] = 1
    return (X - mean) / std


def normalize_minmax(X):
    """
    Normalización Min-Max (escalado a rango [0, 1])
    
    Args:
        X: matriz numpy de forma (n_samples, n_features)
    
    Returns:
        matriz normalizada en el rango [0, 1]
    """
    min_val = np.min(X, axis=0)
    max_val = np.max(X, axis=0)
    # Evitar división por cero
    range_val = max_val - min_val
    range_val[range_val == 0] = 1
    return (X - min_val) / range_val


def apply_normalization(X, method='zscore'):
    """
    Aplica el método de normalización especificado
    
    Args:
        X: matriz numpy de forma (n_samples, n_features)
        method: 'zscore' (RECOMENDADO) o 'minmax_01'
    
    Returns:
        matriz normalizada según el método especificado
    
    IMPORTANTE:
    - Z-Score (zscore): Mejor para clustering, separa bien los grupos visualmente
    - Min-Max (minmax_01): Escala a [0,1], comprime clusters y dificulta visualización
    
    Para visualización de clustering, SIEMPRE usar 'zscore'
    """
    if method == 'zscore':
        return normalize_zscore(X)
    elif method == 'minmax_01':
        return normalize_minmax(X)
    else:
        raise ValueError(f"Método de normalización desconocido: {method}")
