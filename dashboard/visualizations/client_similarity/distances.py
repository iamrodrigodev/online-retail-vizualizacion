"""
Módulo de cálculo de distancias entre clientes (optimizado)
"""
import numpy as np


def compute_euclidean_distance(X):
    """
    Calcula la matriz de distancias euclidianas (optimizada para memoria)
    
    Args:
        X: matriz numpy de forma (n_samples, n_features)
    
    Returns:
        matriz de distancias de forma (n_samples, n_samples)
    """
    # Convertir a float32 si no lo es (ahorra 50% memoria)
    if X.dtype != np.float32:
        X = X.astype(np.float32)
    
    # Usar broadcasting para calcular distancias euclidianas eficientemente
    # ||a - b||² = ||a||² + ||b||² - 2*a·b
    sum_squares = np.sum(X**2, axis=1, keepdims=True).astype(np.float32)
    dot_product = np.dot(X, X.T).astype(np.float32)
    
    distances_squared = sum_squares + sum_squares.T - 2 * dot_product
    del sum_squares, dot_product  # Liberar memoria inmediatamente
    
    # Evitar valores negativos por errores numéricos (operación in-place)
    np.maximum(distances_squared, 0, out=distances_squared)
    
    # Tomar raíz cuadrada (operación in-place)
    np.sqrt(distances_squared, out=distances_squared)
    
    # Asegurar que la diagonal sea exactamente 0
    np.fill_diagonal(distances_squared, 0)
    
    return distances_squared


def compute_cosine_distance(X):
    """
    Calcula la matriz de distancias coseno (optimizada para memoria)
    
    Args:
        X: matriz numpy de forma (n_samples, n_features)
    
    Returns:
        matriz de distancias de forma (n_samples, n_samples)
    """
    # Convertir a float32 si no lo es
    if X.dtype != np.float32:
        X = X.astype(np.float32)
    
    # Normalizar cada vector (fila) a norma unitaria
    norms = np.linalg.norm(X, axis=1, keepdims=True).astype(np.float32)
    norms[norms == 0] = 1  # Evitar división por cero
    X_normalized = (X / norms).astype(np.float32)
    del norms  # Liberar memoria
    
    # Calcular similitud coseno: cos(θ) = X_normalized @ X_normalized.T
    cosine_similarity = np.dot(X_normalized, X_normalized.T).astype(np.float32)
    del X_normalized  # Liberar memoria
    
    # Asegurar que esté en el rango [-1, 1] (in-place)
    np.clip(cosine_similarity, -1, 1, out=cosine_similarity)
    
    # Convertir a distancia: dist = 1 - similarity (in-place)
    np.subtract(1, cosine_similarity, out=cosine_similarity)
    
    # Asegurar que la diagonal sea 0
    np.fill_diagonal(cosine_similarity, 0)
    
    return cosine_similarity


def compute_pearson_distance(X):
    """
    Calcula la matriz de distancias basada en correlación de Pearson
    Distancia = 1 - correlación (optimizada para memoria)
    
    Args:
        X: matriz numpy de forma (n_samples, n_features)
    
    Returns:
        matriz de distancias de forma (n_samples, n_samples)
    """
    # Convertir a float32 si no lo es
    if X.dtype != np.float32:
        X = X.astype(np.float32)
    
    # Normalizar cada fila (centrar y escalar)
    X_centered = (X - np.mean(X, axis=1, keepdims=True)).astype(np.float32)
    X_std = np.std(X, axis=1, keepdims=True).astype(np.float32)
    
    # Evitar división por cero
    X_std[X_std == 0] = 1
    
    # Normalizar
    X_normalized = (X_centered / X_std).astype(np.float32)
    del X_centered, X_std  # Liberar memoria
    
    # Calcular matriz de correlación usando producto matricial
    # corr[i,j] = (X_normalized[i] @ X_normalized[j].T) / n_features
    n_features = X.shape[1]
    correlation_matrix = (np.dot(X_normalized, X_normalized.T) / n_features).astype(np.float32)
    del X_normalized  # Liberar memoria
    
    # Asegurar que esté en el rango [-1, 1] (in-place)
    np.clip(correlation_matrix, -1, 1, out=correlation_matrix)
    
    # Convertir a distancia: dist = 1 - corr (in-place)
    np.subtract(1, correlation_matrix, out=correlation_matrix)
    
    # Asegurar que la diagonal sea 0
    np.fill_diagonal(correlation_matrix, 0)
    
    return correlation_matrix


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
