"""
Módulo para generar visualizaciones Plotly del gráfico de similitud de clientes
"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def create_client_similarity_plot(embedding_data, neighbors_data=None, edges_data=None, 
                                  selected_customer_id=None, pca_variance=None, axis_info=None):
    """
    Crea el gráfico Plotly de similitud de clientes usando CLUSTERING RFM
    
    ESTRATEGIA DE VISUALIZACIÓN PROFESIONAL:
    ✓ Colorea por CLUSTER (grupos de comportamiento RFM similar)
    ✓ Muestra CustomerType en tooltip (validación de negocio)
    ✓ Usa normalización Z-Score para separación visual clara
    ✓ Evita Min-Max [0,1] que comprime los clusters
    
    Args:
        embedding_data: lista de diccionarios con datos de embedding
        neighbors_data: lista de vecinos (opcional)
        edges_data: lista de conexiones (opcional)
        selected_customer_id: ID del cliente seleccionado (opcional)
        pca_variance: dict con información de varianza explicada del PCA (opcional)
        axis_info: dict con información de ejes personalizados (opcional)
    
    Returns:
        figura Plotly
    """
    if not embedding_data:
        # Crear figura vacía si no hay datos
        fig = go.Figure()
        fig.add_annotation(
            text="No hay datos disponibles",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=20)
        )
        return fig
    
    # Separar datos por CLUSTER (grupos de comportamiento RFM)
    clusters = {}
    cluster_types = {}  # Para calcular tipo predominante y estadísticas
    
    for point in embedding_data:
        cluster_id = point['cluster']
        if cluster_id not in clusters:
            clusters[cluster_id] = {
                'x': [], 'y': [], 'ids': [], 'texts': [],
                'outliers': [], 'customer_types': []
            }
            cluster_types[cluster_id] = []
        
        clusters[cluster_id]['x'].append(point['x'])
        clusters[cluster_id]['y'].append(point['y'])
        clusters[cluster_id]['ids'].append(point['id'])
        clusters[cluster_id]['outliers'].append(point['outlier'])
        clusters[cluster_id]['customer_types'].append(point['customer_type'])
        cluster_types[cluster_id].append(point['customer_type'])
        
        # Tooltip muestra: cluster + tipo individual + métricas RFM
        text = (f"<b>Cluster RFM:</b> {cluster_id}<br>"
                f"<b>Tipo de Cliente:</b> {point['customer_type']}<br>"
                f"<b>ID:</b> {point['id']}<br>"
                f"<b>Total gastado:</b> ${point['total_spent']:,.2f}<br>"
                f"<b>Frecuencia:</b> {point['frequency']} compras<br>"
                f"<b>Productos únicos:</b> {point['unique_products']}<br>"
                f"<b>País:</b> {point['country']}")
        clusters[cluster_id]['texts'].append(text)
    
    # Calcular tipo predominante por cluster (para nombre descriptivo)
    cluster_names = {}
    for cluster_id, types in cluster_types.items():
        # Contar frecuencia de cada tipo
        type_counts = {}
        for t in types:
            type_counts[t] = type_counts.get(t, 0) + 1
        # Obtener el tipo más común y su porcentaje
        predominant_type = max(type_counts, key=type_counts.get)
        total = len(types)
        percentage = (type_counts[predominant_type] / total) * 100
        cluster_names[cluster_id] = f'Cluster {cluster_id}: {predominant_type} ({percentage:.0f}%)'
    
    # Crear figura
    fig = go.Figure()
    
    # Paleta de colores distintivos para CLUSTERS (no para tipos de cliente)
    # Usando colores que se distinguen bien visualmente entre sí
    cluster_color_palette = [
        '#e74c3c',  # Rojo vibrante - Cluster 0
        '#3498db',  # Azul brillante - Cluster 1
        '#2ecc71',  # Verde esmeralda - Cluster 2
        '#f39c12',  # Naranja dorado - Cluster 3
        '#9b59b6',  # Púrpura - Cluster 4 (por si se usa n_clusters=5)
        '#1abc9c',  # Turquesa - Cluster 5 (backup)
    ]
    
    # Dibujar líneas de conexión primero (para que estén debajo)
    if edges_data:
        # Crear diccionario de búsqueda rápida para coordenadas
        coords_dict = {point['id']: (point['x'], point['y']) 
                      for point in embedding_data}
        
        for edge in edges_data:
            source_id = str(edge['source'])
            target_id = str(edge['target'])
            
            if source_id in coords_dict and target_id in coords_dict:
                x0, y0 = coords_dict[source_id]
                x1, y1 = coords_dict[target_id]
                
                fig.add_trace(go.Scatter(
                    x=[x0, x1],
                    y=[y0, y1],
                    mode='lines',
                    line=dict(color='rgba(150, 150, 150, 0.3)', width=1),
                    hoverinfo='skip',
                    showlegend=False
                ))
    
    # Crear set de vecinos para resaltarlos
    neighbor_ids_set = set()
    if neighbors_data:
        neighbor_ids_set = {str(n['id']) for n in neighbors_data}
    
    # Agregar puntos por CLUSTER (grupos visuales claros)
    # con colores según tipo predominante (consistencia con Customer Profiles)
    for cluster_id, cluster_data in clusters.items():
        # Separar puntos normales, outliers, vecinos y seleccionado
        normal_x, normal_y, normal_text, normal_ids = [], [], [], []
        outlier_x, outlier_y, outlier_text, outlier_ids = [], [], [], []
        selected_x, selected_y, selected_text, selected_ids = [], [], [], []
        neighbor_x, neighbor_y, neighbor_text, neighbor_point_ids = [], [], [], []
        
        for i in range(len(cluster_data['x'])):
            x, y = cluster_data['x'][i], cluster_data['y'][i]
            text = cluster_data['texts'][i]
            point_id = str(cluster_data['ids'][i])
            
            # Cliente seleccionado
            if selected_customer_id and point_id == str(selected_customer_id):
                selected_x.append(x)
                selected_y.append(y)
                selected_text.append(text)
                selected_ids.append(point_id)
            # Vecinos del cliente seleccionado
            elif point_id in neighbor_ids_set:
                neighbor_x.append(x)
                neighbor_y.append(y)
                neighbor_text.append(text)
                neighbor_point_ids.append(point_id)
            # Outliers
            elif cluster_data['outliers'][i]:
                outlier_x.append(x)
                outlier_y.append(y)
                outlier_text.append(text)
                outlier_ids.append(point_id)
            # Puntos normales
            else:
                normal_x.append(x)
                normal_y.append(y)
                normal_text.append(text)
                normal_ids.append(point_id)
        
        # Nombre descriptivo y color según el ID del cluster
        cluster_name = cluster_names.get(cluster_id, f'Cluster {cluster_id}')
        color = cluster_color_palette[cluster_id % len(cluster_color_palette)]
        
        # Puntos normales
        if normal_x:
            fig.add_trace(go.Scatter(
                x=normal_x, y=normal_y,
                mode='markers',
                name=cluster_name,
                marker=dict(
                    size=8,
                    color=color,
                    symbol='circle',
                    line=dict(width=0.5, color='white')
                ),
                text=normal_text,
                hovertemplate='%{text}<extra></extra>',
                customdata=[[id] for id in normal_ids]
            ))
        
        # Outliers
        if outlier_x:
            fig.add_trace(go.Scatter(
                x=outlier_x, y=outlier_y,
                mode='markers',
                name=f'{cluster_name} (Atípicos)',
                marker=dict(
                    size=10,
                    color=color,
                    symbol='diamond',
                    line=dict(width=1, color='black')
                ),
                text=outlier_text,
                hovertemplate='%{text}<extra></extra>',
                customdata=[[id] for id in outlier_ids]
            ))
        
        # Vecinos resaltados
        if neighbor_x:
            fig.add_trace(go.Scatter(
                x=neighbor_x, y=neighbor_y,
                mode='markers',
                name=f'Vecinos - {cluster_name}',
                marker=dict(
                    size=12,
                    color=color,
                    symbol='circle',
                    line=dict(width=2, color='yellow')
                ),
                text=neighbor_text,
                hovertemplate='%{text}<extra></extra>',
                customdata=[[id] for id in neighbor_point_ids]
            ))
        
        # Cliente seleccionado
        if selected_x:
            fig.add_trace(go.Scatter(
                x=selected_x, y=selected_y,
                mode='markers',
                name='Cliente Seleccionado',
                marker=dict(
                    size=16,
                    color='red',
                    symbol='star',
                    line=dict(width=2, color='darkred')
                ),
                text=selected_text,
                hovertemplate='%{text}<extra></extra>',
                customdata=[[id] for id in selected_ids]
            ))
    
    # Configurar títulos de ejes
    # Verificar si se usan ejes personalizados
    if axis_info and axis_info.get('use_pca') == False:
        # Usar características directas
        x_name = axis_info.get('x_axis_name', 'Eje X')
        y_name = axis_info.get('y_axis_name', 'Eje Y')
        xaxis_title = x_name
        yaxis_title = y_name
        title_text = f'Gráfico de Similitud de Clientes (Análisis RFM: {x_name} vs {y_name})'
    elif pca_variance:
        # Usar PCA con información de varianza
        pc1_var = pca_variance.get('pc1_variance', 0)
        pc2_var = pca_variance.get('pc2_variance', 0)
        total_var = pca_variance.get('total_variance', 0)
        pc1_features = pca_variance.get('pc1_features', [])
        pc2_features = pca_variance.get('pc2_features', [])
        
        # Mostrar solo la característica MÁS IMPORTANTE de cada dimensión
        if pc1_features and len(pc1_features) > 0:
            xaxis_title = f'{pc1_features[0]} ({pc1_var:.1f}%)'
        else:
            xaxis_title = f'Dimensión 1 ({pc1_var:.1f}%)'
        
        if pc2_features and len(pc2_features) > 0:
            yaxis_title = f'{pc2_features[0]} ({pc2_var:.1f}%)'
        else:
            yaxis_title = f'Dimensión 2 ({pc2_var:.1f}%)'
        
        # Total de clientes para mostrar que es toda la data
        total_customers = len(embedding_data)
        title_text = f'Gráfico de Similitud de Clientes - Análisis RFM ({total_customers:,} clientes)'
    else:
        # Valores por defecto
        xaxis_title = 'Dimensión 1'
        yaxis_title = 'Dimensión 2'
        title_text = 'Gráfico de Similitud de Clientes - Análisis RFM'
    
    # Configurar layout con zoom habilitado (como el mapa mundial)
    fig.update_layout(
        title={
            'text': title_text,
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': '#0824a4', 'family': 'Arial, sans-serif'}
        },
        xaxis=dict(
            title=xaxis_title,
            showgrid=True,
            gridcolor='rgba(200, 200, 200, 0.2)',
            zeroline=False,
            fixedrange=False  # Habilitar zoom en eje X
        ),
        yaxis=dict(
            title=yaxis_title,
            showgrid=True,
            gridcolor='rgba(200, 200, 200, 0.2)',
            zeroline=False,
            fixedrange=False  # Habilitar zoom en eje Y
        ),
        hovermode='closest',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02,
            bgcolor='rgba(255, 255, 255, 0.9)',
            bordercolor='#e0e0e0',
            borderwidth=1,
            font=dict(size=11, color='#2c3e50')
        ),
        dragmode='pan',  # Habilitar movimiento/arrastre (como el mapa mundial)
        height=700,
        margin=dict(l=50, r=200, t=80, b=50)
    )
    
    return fig
