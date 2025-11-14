"""
Módulo de búsqueda de K vecinos más cercanos
"""
import numpy as np


def find_k_nearest_neighbors(distance_matrix, k=10, customer_idx=None):
    """
    Encuentra los K vecinos más cercanos para un cliente específico
    o para todos los clientes
    
    Args:
        distance_matrix: matriz de distancias (n_samples, n_samples)
        k: número de vecinos más cercanos a encontrar
        customer_idx: índice del cliente (opcional). Si es None, devuelve para todos
    
    Returns:
        Si customer_idx es None:
            dict con todos los clientes y sus vecinos
        Si customer_idx está especificado:
            dict con vecinos y distancias del cliente especificado
    """
    n_samples = distance_matrix.shape[0]
    
    # Ajustar k si es mayor que el número de muestras
    k = min(k, n_samples - 1)
    
    if customer_idx is not None:
        # Encontrar vecinos para un cliente específico
        distances = distance_matrix[customer_idx].copy()
        # Establecer la distancia a sí mismo como infinita para excluirlo
        distances[customer_idx] = np.inf
        
        # Obtener los índices de los k vecinos más cercanos
        neighbor_indices = np.argsort(distances)[:k]
        neighbor_distances = distances[neighbor_indices]
        
        return {
            'neighbor_indices': neighbor_indices.tolist(),
            'neighbor_distances': neighbor_distances.tolist()
        }
    else:
        # Encontrar vecinos para todos los clientes
        all_neighbors = {}
        for i in range(n_samples):
            distances = distance_matrix[i].copy()
            distances[i] = np.inf
            neighbor_indices = np.argsort(distances)[:k]
            neighbor_distances = distances[neighbor_indices]
            
            all_neighbors[i] = {
                'neighbor_indices': neighbor_indices.tolist(),
                'neighbor_distances': neighbor_distances.tolist()
            }
        
        return all_neighbors


def create_edges_list(customer_idx, neighbor_indices, customer_ids):
    """
    Crea una lista de conexiones (edges) entre el cliente y sus vecinos
    
    Args:
        customer_idx: índice del cliente seleccionado
        neighbor_indices: lista de índices de vecinos
        customer_ids: lista de IDs de clientes
    
    Returns:
        lista de diccionarios con formato {'source': id, 'target': id}
    """
    edges = []
    source_id = customer_ids[customer_idx]
    
    for neighbor_idx in neighbor_indices:
        target_id = customer_ids[neighbor_idx]
        edges.append({
            'source': source_id,
            'target': target_id
        })
    
    return edges
