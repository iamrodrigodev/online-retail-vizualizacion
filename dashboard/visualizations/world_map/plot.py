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

    # Crear una figura Choropleth
    fig = go.Figure(data=go.Choropleth(
        locations=dataset_countries,
        locationmode='country names',
        z=[1] * len(dataset_countries),  # Valor ficticio para asignar color
        colorscale=[[0, '#6c757d'], [1, '#6c757d']], # Escala de un solo color (gris)
        showscale=False, # Ocultar la barra de colores
        marker_line_color='white', # Color de las fronteras
        marker_line_width=0.5,
        hoverinfo='location', # Mostrar solo el nombre del país al pasar el cursor
        name='Países con ventas',  # Nombre para la leyenda
        showlegend=True  # Mostrar en la leyenda
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
        ),
        margin={"r":0,"t":60,"l":0,"b":0}, # Ajustar margen superior para el título
        paper_bgcolor='rgba(0,0,0,0)', # Fondo del papel transparente
        plot_bgcolor='rgba(0,0,0,0)', # Fondo del gráfico transparente
        
        # Configuración de la leyenda
        showlegend=True,
        legend=dict(
            x=0.02,  # Posición horizontal (0-1, de izquierda a derecha)
            y=0.92,  # Posición vertical ajustada para evitar solapar el título
            xanchor='left',
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
                text=f'Total de países: {total_countries}',
                xref='paper',
                yref='paper',
                x=0.5,
                y=-0.05,
                xanchor='center',
                yanchor='top',
                showarrow=False,
                font=dict(
                    size=16,
                    color='#2c3e50',
                    family='Arial, sans-serif'
                ),
                bgcolor='rgba(255, 255, 255, 0.8)',
                bordercolor='#e0e0e0',
                borderwidth=1,
                borderpad=8
            )
        ]
    )

    return fig, dataset_countries
