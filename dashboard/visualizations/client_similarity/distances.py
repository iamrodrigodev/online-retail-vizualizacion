"""
Módulo de cálculo de distancias entre clientes (optimizado)
"""
import numpy as np


def compute_euclidean_distance(X):
    """
    Calcula la matriz de distancias euclidianas (optimizada)
    
    Args:
        X: matriz numpy de forma (n_samples, n_features)
    
    Returns:
        matriz de distancias de forma (n_samples, n_samples)
    """
    # Usar broadcasting para calcular distancias euclidianas eficientemente
    # ||a - b||² = ||a||² + ||b||² - 2*a·b
    sum_squares = np.sum(X**2, axis=1, keepdims=True)
    dot_product = np.dot(X, X.T)
    
    distances_squared = sum_squares + sum_squares.T - 2 * dot_product
    
    # Evitar valores negativos por errores numéricos
    distances_squared = np.maximum(distances_squared, 0)
    
    # Tomar raíz cuadrada
    distance_matrix = np.sqrt(distances_squared)
    
    # Asegurar que la diagonal sea exactamente 0
    np.fill_diagonal(distance_matrix, 0)
    
    return distance_matrix


def compute_cosine_distance(X):
    """
    Calcula la matriz de distancias coseno (optimizada)
    
    Args:
        X: matriz numpy de forma (n_samples, n_features)
    
    Returns:
        matriz de distancias de forma (n_samples, n_samples)
    """
    # Normalizar cada vector (fila) a norma unitaria
    norms = np.linalg.norm(X, axis=1, keepdims=True)
    norms[norms == 0] = 1  # Evitar división por cero
    X_normalized = X / norms
    
    # Calcular similitud coseno: cos(θ) = X_normalized @ X_normalized.T
    cosine_similarity = np.dot(X_normalized, X_normalized.T)
    
    # Asegurar que esté en el rango [-1, 1]
    cosine_similarity = np.clip(cosine_similarity, -1, 1)
    
    # Convertir a distancia: dist = 1 - similarity
    distance_matrix = 1 - cosine_similarity
    
    # Asegurar que la diagonal sea 0
    np.fill_diagonal(distance_matrix, 0)
    
    return distance_matrix


def compute_pearson_distance(X):
    """
    Calcula la matriz de distancias basada en correlación de Pearson
    Distancia = 1 - correlación
    
    Args:
        X: matriz numpy de forma (n_samples, n_features)
    
    Returns:
        matriz de distancias de forma (n_samples, n_samples)
    """
    # Normalizar cada fila (centrar y escalar)
    X_centered = X - np.mean(X, axis=1, keepdims=True)
    X_std = np.std(X, axis=1, keepdims=True)
    
    # Evitar división por cero
    X_std[X_std == 0] = 1
    
    # Normalizar
    X_normalized = X_centered / X_std
    
    # Calcular matriz de correlación usando producto matricial
    # corr[i,j] = (X_normalized[i] @ X_normalized[j].T) / n_features
    n_features = X.shape[1]
    correlation_matrix = np.dot(X_normalized, X_normalized.T) / n_features
    
    # Asegurar que esté en el rango [-1, 1]
    correlation_matrix = np.clip(correlation_matrix, -1, 1)
    
    # Convertir a distancia: dist = 1 - corr
    # Esto da valores en [0, 2]
    distance_matrix = 1 - correlation_matrix
    
    # Asegurar que la diagonal sea 0
    np.fill_diagonal(distance_matrix, 0)
    
    return distance_matrix


def compute_distance_matrix(X, metric='euclidean'):
    """
    Calcula la matriz de distancias usando la métrica especificada
    
    Args:
        X: matriz numpy de forma (n_samples, n_features)
        metric: 'euclidean', 'cosine', o 'pearson'
    
    Returns:
        matriz de distancias de forma (n_samples, n_samples)
    """
    if metric == 'euclidean':
        return compute_euclidean_distance(X)
    elif metric == 'cosine':
        return compute_cosine_distance(X)
    elif metric == 'pearson':
        return compute_pearson_distance(X)
    else:
        raise ValueError(f"Métrica de distancia desconocida: {metric}")
