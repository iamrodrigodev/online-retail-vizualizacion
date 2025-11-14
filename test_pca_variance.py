"""
Script de prueba para verificar que PCA está calculando correctamente la varianza explicada
Y mostrando las características más importantes
"""
from dashboard.visualizations.client_similarity.data_processor import prepare_customer_features
from dashboard.visualizations.client_similarity.preprocessing import apply_normalization
from dashboard.visualizations.client_similarity.dimensionality import apply_pca
import numpy as np

print("="*60)
print("PRUEBA DE PCA - CARACTERÍSTICAS PRINCIPALES")
print("="*60)

# 1. Preparar datos
print("\n1. Preparando características de clientes...")
customer_ids, features, customer_info = prepare_customer_features()
print(f"   ✓ {len(customer_ids)} clientes")
print(f"   ✓ {features.shape[1]} características (features)")

# 2. Normalizar con Z-Score
print("\n2. Normalizando con Z-Score...")
features_normalized = apply_normalization(features, method='zscore')

# 3. Aplicar PCA
print("\n3. Aplicando PCA...")
embedding_2d, explained_variance, pca_object, feature_names = apply_pca(features_normalized, n_components=2)

print(f"\n   📊 CARACTERÍSTICAS RFM ANALIZADAS:")
print(f"   {'─'*50}")
for i, name in enumerate(feature_names, 1):
    print(f"   {i}. {name}")
print(f"   {'─'*50}")

# 4. Analizar componentes principales
components = pca_object.components_

print(f"\n   🎯 DIMENSIÓN 1 (Eje X) - {explained_variance[0]*100:.1f}%:")
print(f"   {'─'*50}")
pc1_importance = np.abs(components[0])
pc1_sorted = np.argsort(pc1_importance)[::-1]
for i in range(3):  # Top 3
    idx = pc1_sorted[i]
    weight = components[0][idx]
    print(f"   {i+1}. {feature_names[idx]:15} → {abs(weight):.3f} ({'positivo' if weight > 0 else 'negativo'})")

print(f"\n   🎯 DIMENSIÓN 2 (Eje Y) - {explained_variance[1]*100:.1f}%:")
print(f"   {'─'*50}")
pc2_importance = np.abs(components[1])
pc2_sorted = np.argsort(pc2_importance)[::-1]
for i in range(3):  # Top 3
    idx = pc2_sorted[i]
    weight = components[1][idx]
    print(f"   {i+1}. {feature_names[idx]:15} → {abs(weight):.3f} ({'positivo' if weight > 0 else 'negativo'})")

print(f"\n   📈 RESUMEN:")
print(f"   {'─'*50}")
print(f"   Total información preservada: {sum(explained_variance)*100:.1f}%")

# Nombres para los ejes
pc1_top_features = [feature_names[i] for i in pc1_sorted[:2]]
pc2_top_features = [feature_names[i] for i in pc2_sorted[:2]]

print(f"\n   📊 NOMBRE DE EJES EN EL GRÁFICO:")
print(f"   {'─'*50}")
print(f"   Eje X: Dimensión 1: {', '.join(pc1_top_features)} ({explained_variance[0]*100:.1f}%)")
print(f"   Eje Y: Dimensión 2: {', '.join(pc2_top_features)} ({explained_variance[1]*100:.1f}%)")

print(f"\n{'='*60}")
print("PRUEBA COMPLETADA")
print("="*60)
