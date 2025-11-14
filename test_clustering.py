"""
Verificar el clustering con minmax_01
"""
from dashboard.visualizations.client_similarity.data_processor import prepare_customer_features
from dashboard.visualizations.client_similarity.preprocessing import apply_normalization
from dashboard.visualizations.client_similarity.clustering import apply_kmeans_clustering
from dashboard.visualizations.client_similarity.dimensionality import apply_dimensionality_reduction
import numpy as np
from collections import Counter

print("Probando con normalización minmax_01...")
customer_ids, features, customer_info = prepare_customer_features()

# Normalizar con minmax_01
features_normalized = apply_normalization(features, method='minmax_01')

# Aplicar PCA
X_2d = apply_dimensionality_reduction(features_normalized, method='pca')

# Clustering
clusters = apply_kmeans_clustering(features_normalized, n_clusters=5)

print(f"\nTotal clientes: {len(customer_ids)}")
print(f"\nDistribución de CLUSTERS:")
cluster_counts = Counter(clusters)
for cluster_id in sorted(cluster_counts.keys()):
    count = cluster_counts[cluster_id]
    pct = (count / len(clusters)) * 100
    print(f"  Cluster {cluster_id}: {count} clientes ({pct:.1f}%)")

print(f"\nDistribución de TIPOS DE CLIENTE:")
types = [customer_info[cid]['customer_type'] for cid in customer_ids]
type_counts = Counter(types)
for tipo, count in type_counts.most_common():
    pct = (count / len(types)) * 100
    print(f"  {tipo}: {count} ({pct:.1f}%)")

# Mostrar cómo se distribuyen los tipos en cada cluster
print(f"\nCOMPOSICIÓN DE CADA CLUSTER:")
for cluster_id in sorted(cluster_counts.keys()):
    print(f"\n  Cluster {cluster_id} ({cluster_counts[cluster_id]} clientes):")
    cluster_types = [customer_info[customer_ids[i]]['customer_type'] 
                     for i in range(len(customer_ids)) if clusters[i] == cluster_id]
    cluster_type_counts = Counter(cluster_types)
    for tipo, count in cluster_type_counts.most_common():
        pct = (count / len(cluster_types)) * 100
        print(f"    {tipo}: {count} ({pct:.1f}%)")

# Verificar separación espacial de clusters en 2D
print(f"\nSEPARACIÓN ESPACIAL EN 2D:")
for cluster_id in sorted(cluster_counts.keys()):
    cluster_points = X_2d[clusters == cluster_id]
    center_x = np.mean(cluster_points[:, 0])
    center_y = np.mean(cluster_points[:, 1])
    std_x = np.std(cluster_points[:, 0])
    std_y = np.std(cluster_points[:, 1])
    print(f"  Cluster {cluster_id}: Centro=({center_x:.2f}, {center_y:.2f}), STD=({std_x:.2f}, {std_y:.2f})")
