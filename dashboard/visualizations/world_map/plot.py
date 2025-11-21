import plotly.graph_objects as go
from dashboard.visualizations.shared.data_loader import load_online_retail_data

def create_world_map_plot():
    """
    Crea una figura de Plotly con un mapa mundial, destacando los países
    presentes en el dataset de online retail.
    """
    df = load_online_retail_data()

    if df.is_empty():
        # Retorna una figura vacía y una lista vacía si no hay datos
        return go.Figure(), []

    # Obtener la lista de países únicos del dataset
    dataset_countries = df['Country'].unique().to_list()
    total_countries = len(dataset_countries)

    # Crear dos traces: uno para países con ventas (gris) y otro para país seleccionado (azul)
    fig = go.Figure()
    
    # Trace 1: Países con ventas (gris)
    fig.add_trace(go.Choropleth(
        locations=dataset_countries,
        locationmode='country names',
        z=[1] * len(dataset_countries),
        colorscale=[[0, '#6c757d'], [1, '#6c757d']],
        showscale=False,
        marker_line_color='white',
        marker_line_width=0.5,
        hoverinfo='location',
        name='Países con ventas',
        showlegend=True,
        visible=True
    ))
    
    # Trace 2: País seleccionado (azul La Salle) - inicialmente con un país invisible
    fig.add_trace(go.Choropleth(
        locations=[''],  # Inicialmente vacío pero con un elemento
        locationmode='country names',
        z=[1],
        colorscale=[[0, '#0824a4'], [1, '#0824a4']],
        showscale=False,
        marker_line_color='white',
        marker_line_width=0.5,
        hoverinfo='location',
        name='',  # Sin nombre en la leyenda
        showlegend=False,  # Ocultar de la leyenda
        visible=True
    ))

    # Actualizar el layout del mapa
    fig.update_layout(
        title={
            'text': 'Países con Ventas',
            'x': 0.5,
            'xanchor': 'center',
            'font': {
                'size': 24,
                'color': '#0824a4',
                'family': 'Arial, sans-serif'
            }
        },
        geo=dict(
            showframe=False,
            showcoastlines=False,
            projection_type='natural earth',
            landcolor='#f8f9fa', # Color para países no presentes en el dataset
            bgcolor='rgba(0,0,0,0)', # Fondo transparente
            projection_scale=1.0,  # Escala base del mapa
        ),
        dragmode='pan',  # Permitir arrastre/movimiento del mapa (izquierda/derecha, arriba/abajo)
        margin={"r":0,"t":60,"l":0,"b":0}, # Ajustar margen superior
        paper_bgcolor='rgba(0,0,0,0)', # Fondo del papel transparente
        plot_bgcolor='rgba(0,0,0,0)', # Fondo del gráfico transparente
        
        # Configuración de la leyenda
        showlegend=True,
        legend=dict(
            x=-0.02,  # Posición fuera del gráfico, a la izquierda
            y=1,  # Alineada arriba
            xanchor='right',
            yanchor='top',
            bgcolor='rgba(255, 255, 255, 0.9)',  # Fondo blanco semi-transparente
            bordercolor='#e0e0e0',
            borderwidth=1,
            font=dict(
                size=12,
                color='#2c3e50'
            ),
            itemclick=False,  # Desactivar click en items de la leyenda
            itemdoubleclick=False  # Desactivar doble click en items de la leyenda
        ),
        
        # Anotación para mostrar la cantidad de países
        annotations=[
            dict(
                text=f'Países donde se han realizado ventas: {total_countries}',
                xref='paper',
                yref='paper',
                x=0.5,
                y=0.92,
                xanchor='center',
                yanchor='top',
                showarrow=False,
                font=dict(
                    size=14,
                    color='#000000',
                    family='Arial, sans-serif'
                )
            )
        ]
    )

    return fig, dataset_countries
