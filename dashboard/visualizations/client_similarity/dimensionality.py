"""
Módulo de reducción dimensional (solo PCA)
"""
import numpy as np
from sklearn.decomposition import PCA


def apply_pca(X, n_components=2, random_state=42):
    """
    Aplica PCA para reducción dimensional (optimizado para grandes datasets)
    
    Args:
        X: matriz numpy de forma (n_samples, n_features)
        n_components: número de componentes (default 2 para visualización 2D)
        random_state: semilla aleatoria para reproducibilidad
    
    Returns:
        tuple: (transformed_data, explained_variance_ratio, pca_object, feature_names)
            - transformed_data: matriz reducida de forma (n_samples, n_components)
            - explained_variance_ratio: array con % de varianza explicada por cada PC
            - pca_object: objeto PCA ajustado (para análisis adicional)
            - feature_names: nombres de las características RFM
    """
    n_samples, n_features = X.shape
    n_components = min(n_components, n_samples, n_features)
    
    # Nombres de las características RFM en orden
    feature_names = ['Recency', 'Frequency', 'Monetary', 'TotalQuantity', 
                     'AvgUnitPrice', 'AvgOrderValue', 'UniqueProducts']
    
    # Para datasets grandes, usar randomized SVD que es más rápido
    if n_samples > 1000:
        pca = PCA(n_components=n_components, svd_solver='randomized', random_state=random_state)
    else:
        pca = PCA(n_components=n_components, random_state=random_state)
    
    transformed = pca.fit_transform(X)
    
    return transformed, pca.explained_variance_ratio_, pca, feature_names


def apply_dimensionality_reduction(X, method='pca', random_state=42):
    """
    Aplica reducción dimensional usando PCA
    
    Args:
        X: matriz numpy de forma (n_samples, n_features)
        method: solo 'pca' está soportado
        random_state: semilla aleatoria para reproducibilidad
    
    Returns:
        tuple: (transformed_data, explained_variance_ratio, pca_object, feature_names)
            - transformed_data: matriz reducida de forma (n_samples, 2)
            - explained_variance_ratio: array con % de varianza explicada por cada PC
            - pca_object: objeto PCA ajustado
            - feature_names: nombres de las características RFM
    """
    # Solo PCA está implementado
    return apply_pca(X, random_state=random_state)

