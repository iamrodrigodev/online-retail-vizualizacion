"""
Procesador principal que integra todos los módulos de similitud de clientes
"""
import polars as pl
import numpy as np
from dashboard.visualizations.shared.data_loader import load_online_retail_data
from dashboard.visualizations.customer_profiles.data_processor import detectar_outliers_iqr
from .preprocessing import apply_normalization
from .distances import compute_distance_matrix
from .knn import find_k_nearest_neighbors, create_edges_list
from .dimensionality import apply_dimensionality_reduction
from .clustering import apply_kmeans_clustering, detect_outliers_statistical


def prepare_customer_features(country=None, start_date=None, end_date=None):
    """
    Prepara las características de clientes desde el dataset
    Calcula métricas RFM (Recency, Frequency, Monetary) y otras características
    
    Args:
        country: País para filtrar (opcional)
        start_date: Fecha de inicio del período (formato 'YYYY-MM', opcional)
        end_date: Fecha de fin del período (formato 'YYYY-MM', opcional)
    
    Returns:
        tuple: (customer_ids, feature_matrix, customer_info)
            - customer_ids: lista de CustomerIDs
            - feature_matrix: matriz numpy (n_customers, n_features)
            - customer_info: diccionario con información adicional de cada cliente
    """
    df = load_online_retail_data()
    
    if df.is_empty():
        return [], np.array([]), {}
    
    # Convertir InvoiceDate a datetime
    df = df.with_columns([
        pl.col('InvoiceDate').str.strptime(pl.Datetime, "%Y-%m-%d %H:%M:%S").alias('InvoiceDate')
    ])
    
    # Aplicar filtro de país si se especifica
    if country:
        df = df.filter(pl.col('Country') == country)
    
    # Aplicar filtro de fechas si se especifica
    if start_date:
        start_datetime = pl.datetime(int(start_date[:4]), int(start_date[5:7]), 1)
        df = df.filter(pl.col('InvoiceDate') >= start_datetime)
    
    if end_date:
        # Último día del mes especificado
        year = int(end_date[:4])
        month = int(end_date[5:7])
        if month == 12:
            end_datetime = pl.datetime(year + 1, 1, 1)
        else:
            end_datetime = pl.datetime(year, month + 1, 1)
        df = df.filter(pl.col('InvoiceDate') < end_datetime)
    
    # Crear columna Total
    df = df.with_columns(
        (pl.col('Quantity') * pl.col('UnitPrice')).alias('Total')
    )
    
    # Filtrar transacciones válidas
    df = df.filter(
        (pl.col('CustomerID').is_not_null()) &
        (pl.col('Total') > 0) &
        (pl.col('Quantity') > 0)
    )
    
    # Clasificar transacciones usando la MISMA lógica que customer_profiles
    total_lower, total_upper = detectar_outliers_iqr(df, 'Total')
    price_lower, price_upper = detectar_outliers_iqr(df, 'UnitPrice')
    
    # Agregar columna Perfil a nivel de transacción (igual que customer_profiles)
    df = df.with_columns(
        pl.when((pl.col('Total') > total_upper) & (pl.col('UnitPrice') <= price_upper))
        .then(pl.lit('Mayorista Estándar'))
        .when((pl.col('Total') <= total_upper) & (pl.col('UnitPrice') > price_upper))
        .then(pl.lit('Minorista Lujo'))
        .when((pl.col('Total') > total_upper) & (pl.col('UnitPrice') > price_upper))
        .then(pl.lit('Mayorista Lujo'))
        .otherwise(pl.lit('Minorista Estándar'))
        .alias('Perfil')
    )
    
    # Calcular fecha de referencia (última fecha + 1 día)
    max_date = df['InvoiceDate'].max()
    reference_date = max_date + pl.duration(days=1)
    
    # Calcular métricas RFM por cliente
    customer_metrics = df.group_by('CustomerID').agg([
        # Recency: días desde la última compra
        ((reference_date - pl.col('InvoiceDate').max()).dt.total_days()).alias('Recency'),
        # Frequency: número de transacciones únicas
        pl.col('InvoiceNo').n_unique().alias('Frequency'),
        # Monetary: total gastado
        pl.col('Total').sum().alias('Monetary'),
        # Métricas adicionales
        pl.col('Quantity').sum().alias('TotalQuantity'),
        pl.col('UnitPrice').mean().alias('AvgUnitPrice'),
        pl.col('Total').mean().alias('AvgOrderValue'),
        pl.col('StockCode').n_unique().alias('UniqueProducts'),
        pl.col('Country').first().alias('Country'),
        # Usar el perfil más frecuente del cliente
        pl.col('Perfil').mode().first().alias('CustomerType')
    ])
    
    # Filtrar clientes con datos válidos
    customer_metrics = customer_metrics.filter(
        (pl.col('Recency').is_not_null()) &
        (pl.col('Frequency') > 0) &
        (pl.col('Monetary') > 0)
    )
    
    if customer_metrics.is_empty():
        return [], np.array([]), {}
    
    # La clasificación CustomerType ya viene del aggregation (perfil más frecuente)
    # No necesitamos recalcularla aquí
    
    # Extraer IDs de clientes (convertir a float primero, luego a int y finalmente a string)
    customer_ids = [str(int(float(cid))) for cid in customer_metrics['CustomerID'].to_list()]
    
    # Crear matriz de características usando to_numpy() de Polars (más eficiente)
    features = customer_metrics.select([
        'Recency', 'Frequency', 'Monetary', 
        'TotalQuantity', 'AvgUnitPrice', 'AvgOrderValue', 'UniqueProducts'
    ]).to_numpy()
    
    # Crear diccionario de información adicional usando iter_rows (más eficiente)
    customer_info = {}
    info_data = customer_metrics.select([
        'CustomerID', 'CustomerType', 'Monetary', 'Frequency', 
        'Recency', 'AvgOrderValue', 'UniqueProducts', 'Country'
    ]).to_dicts()
    
    for row in info_data:
        cid = str(int(float(row['CustomerID'])))
        customer_info[cid] = {
            'customer_type': row['CustomerType'],
            'total_spent': round(row['Monetary'], 2),
            'frequency': row['Frequency'],
            'recency': round(row['Recency'], 0),
            'avg_order_value': round(row['AvgOrderValue'], 2),
            'unique_products': row['UniqueProducts'],
            'country': row['Country']
        }
    
    return customer_ids, features, customer_info


def compute_client_similarity_graph(customer_id=None, k=10, metric='euclidean', 
                                    normalization='zscore', dimred='pca',
                                    x_axis=None, y_axis=None,
                                    country=None, start_date=None, end_date=None):
    """
    Calcula el gráfico de similitud de clientes con todos los componentes
    
    Args:
        customer_id: ID del cliente a resaltar (opcional)
        k: número de vecinos más cercanos
        metric: métrica de distancia ('euclidean', 'cosine', 'pearson')
        normalization: método de normalización ('zscore', 'minmax_01')
        dimred: método de reducción dimensional ('pca', 'tsne', 'umap')
        x_axis: índice de característica para eje X (0-6, opcional)
        y_axis: índice de característica para eje Y (0-6, opcional)
        country: País para filtrar (opcional)
        start_date: Fecha de inicio del período (formato 'YYYY-MM', opcional)
        end_date: Fecha de fin del período (formato 'YYYY-MM', opcional)
    
    Returns:
        dict con toda la información para visualización
    """
    import gc
    
    # 1. Preparar características de clientes con filtros
    customer_ids, features, customer_info = prepare_customer_features(
        country=country,
        start_date=start_date,
        end_date=end_date
    )
    
    if len(customer_ids) == 0:
        return {
            'embedding': [],
            'neighbors': [],
            'edges': [],
            'error': 'No hay datos de clientes disponibles'
        }
    
    # 2. Normalizar características
    features_normalized = apply_normalization(features, method=normalization)
    
    # Convertir a float32 para ahorrar memoria (50% menos que float64)
    features_normalized = features_normalized.astype(np.float32)
    
    # Verificar que no haya NaN o Inf después de la normalización
    if np.any(np.isnan(features_normalized)) or np.any(np.isinf(features_normalized)):
        # Reemplazar NaN/Inf con valores seguros
        features_normalized = np.nan_to_num(features_normalized, nan=0.0, posinf=1.0, neginf=-1.0)
    
    # 3. Calcular matriz de distancias
    try:
        distance_matrix = compute_distance_matrix(features_normalized, metric=metric)
    except Exception as e:
        print(f"Error al calcular distancias con métrica {metric}: {e}")
        # Fallback a euclidiana si falla
        distance_matrix = compute_distance_matrix(features_normalized, metric='euclidean')
    
    # 4. Aplicar reducción dimensional O usar características directas
    feature_names = ['Recency', 'Frequency', 'Monetary', 'TotalQuantity', 
                     'AvgUnitPrice', 'AvgOrderValue', 'UniqueProducts']
    
    # Inicializar variables
    explained_variance = None
    total_variance_explained = None
    pc1_top_features = None
    pc2_top_features = None
    
    # Si se especifican ejes personalizados, usar características directas
    if x_axis is not None and y_axis is not None:
        # Validar índices
        if not (0 <= x_axis < 7 and 0 <= y_axis < 7):
            # Fallback a PCA si los índices son inválidos
            embedding_2d, explained_variance, pca_object, _ = apply_dimensionality_reduction(features_normalized, method=dimred)
            total_variance_explained = sum(explained_variance) * 100
            components = pca_object.components_
            pc1_importance = np.abs(components[0])
            pc1_top_indices = np.argsort(pc1_importance)[::-1][:3]
            pc1_top_features = [feature_names[i] for i in pc1_top_indices]
            if len(components) > 1:
                pc2_importance = np.abs(components[1])
                pc2_top_indices = np.argsort(pc2_importance)[::-1][:3]
                pc2_top_features = [feature_names[i] for i in pc2_top_indices]
            else:
                pc2_top_features = None
            use_pca = True
        else:
            # Usar características seleccionadas directamente
            embedding_2d = features_normalized[:, [x_axis, y_axis]]
            use_pca = False
    else:
        # Usar PCA (comportamiento por defecto)
        embedding_2d, explained_variance, pca_object, _ = apply_dimensionality_reduction(features_normalized, method=dimred)
        total_variance_explained = sum(explained_variance) * 100
        
        # Obtener los componentes principales y determinar las características más importantes
        components = pca_object.components_
        
        # Para PC1 (primera fila): encontrar las 3 características más influyentes
        pc1_importance = np.abs(components[0])
        pc1_top_indices = np.argsort(pc1_importance)[::-1][:3]
        pc1_top_features = [feature_names[i] for i in pc1_top_indices]
        
        # Para PC2 (segunda fila): encontrar las 3 características más influyentes (si existe)
        if len(components) > 1:
            pc2_importance = np.abs(components[1])
            pc2_top_indices = np.argsort(pc2_importance)[::-1][:3]
            pc2_top_features = [feature_names[i] for i in pc2_top_indices]
        else:
            pc2_top_features = None
        use_pca = True
    
    # 5. Clustering (usar 4 clusters para coincidir con los 4 tipos de cliente)
    cluster_labels = apply_kmeans_clustering(features_normalized, n_clusters=4)
    
    # 6. Detectar outliers
    outlier_mask = detect_outliers_statistical(features_normalized, threshold=3)
    
    # Copiar vecinos antes de liberar distance_matrix si se necesita
    neighbors_indices = None
    neighbors_distances = None
    if customer_id is not None:
        customer_id_str = str(customer_id)
        try:
            customer_idx = customer_ids.index(customer_id_str)
        except ValueError:
            try:
                customer_idx = customer_ids.index(customer_id)
            except ValueError:
                customer_idx = None
        
        if customer_idx is not None:
            neighbors_result = find_k_nearest_neighbors(distance_matrix, k=k, customer_idx=customer_idx)
            neighbors_indices = neighbors_result['neighbor_indices']
            neighbors_distances = neighbors_result['neighbor_distances']
    
    # Liberar matriz de distancias AHORA (puede ser muy grande)
    del distance_matrix
    gc.collect()
    
    # 7. Preparar datos de embedding
    embedding_data = []
    for i, cust_id in enumerate(customer_ids):
        embedding_data.append({
            'id': str(cust_id),
            'x': float(embedding_2d[i, 0]),
            'y': float(embedding_2d[i, 1]),
            'cluster': int(cluster_labels[i]),
            'outlier': bool(outlier_mask[i]),
            'customer_type': customer_info[cust_id]['customer_type'],
            'total_spent': customer_info[cust_id]['total_spent'],
            'frequency': customer_info[cust_id]['frequency'],
            'recency': customer_info[cust_id]['recency'],
            'avg_order_value': customer_info[cust_id]['avg_order_value'],
            'unique_products': customer_info[cust_id]['unique_products'],
            'country': customer_info[cust_id]['country']
        })
    
    # 8. Preparar vecinos si se calcularon anteriormente
    neighbors_data = []
    edges_data = []
    
    if neighbors_indices is not None and neighbors_distances is not None:
        # Preparar datos de vecinos usando los índices precalculados
        for i, (neighbor_idx, distance) in enumerate(zip(neighbors_indices, neighbors_distances)):
            neighbor_id = customer_ids[neighbor_idx]
            neighbors_data.append({
                'id': str(neighbor_id),
                'distance': float(distance),
                'rank': i + 1
            })
        
        # Crear edges (conexiones)
        customer_id_str = str(customer_id)
        try:
            customer_idx = customer_ids.index(customer_id_str)
        except ValueError:
            try:
                customer_idx = customer_ids.index(customer_id)
            except ValueError:
                customer_idx = None
        
        if customer_idx is not None:
            edges_data = create_edges_list(customer_idx, neighbors_indices, customer_ids)
    
    # Liberar memoria de matrices grandes
    del features_normalized
    gc.collect()
    
    return {
        'embedding': embedding_data,
        'neighbors': neighbors_data,
        'edges': edges_data,
        'customer_ids': customer_ids,
        'total_customers': len(customer_ids),
        'axis_info': {
            'use_pca': use_pca,
            'x_axis_index': x_axis if x_axis is not None else None,
            'y_axis_index': y_axis if y_axis is not None else None,
            'x_axis_name': feature_names[x_axis] if x_axis is not None else None,
            'y_axis_name': feature_names[y_axis] if y_axis is not None else None
        },
        'pca_variance': {
            'pc1_variance': float(explained_variance[0] * 100) if use_pca else None,
            'pc2_variance': float(explained_variance[1] * 100) if use_pca and len(explained_variance) > 1 else None,
            'total_variance': float(total_variance_explained) if use_pca else None,
            'pc1_features': pc1_top_features if use_pca else None,
            'pc2_features': pc2_top_features if use_pca else None
        }
    }


def get_all_customer_ids(country=None, start_date=None, end_date=None):
    """
    Obtiene todos los IDs de clientes disponibles
    
    Args:
        country: País para filtrar (opcional)
        start_date: Fecha de inicio del período (formato 'YYYY-MM', opcional)
        end_date: Fecha de fin del período (formato 'YYYY-MM', opcional)
    
    Returns:
        lista de CustomerIDs
    """
    customer_ids, _, _ = prepare_customer_features(
        country=country,
        start_date=start_date,
        end_date=end_date
    )
    return customer_ids
