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

    # Crear una figura Choropleth
    fig = go.Figure(data=go.Choropleth(
        locations=dataset_countries,
        locationmode='country names',
        z=[1] * len(dataset_countries),  # Valor ficticio para asignar color
        colorscale=[[0, '#6c757d'], [1, '#6c757d']], # Escala de un solo color (gris)
        showscale=False, # Ocultar la barra de colores
        marker_line_color='white', # Color de las fronteras
        marker_line_width=0.5,
        hoverinfo='location' # Mostrar solo el nombre del país al pasar el cursor
    ))

    # Actualizar el layout del mapa
    fig.update_layout(
        title_text=None, # Quitamos el título para que no ocupe espacio
        geo=dict(
            showframe=False,
            showcoastlines=False,
            projection_type='natural earth',
            landcolor='#f8f9fa', # Color para países no presentes en el dataset
            bgcolor='rgba(0,0,0,0)', # Fondo transparente
        ),
        margin={"r":0,"t":0,"l":0,"b":0}, # Eliminar márgenes
        paper_bgcolor='rgba(0,0,0,0)', # Fondo del papel transparente
        plot_bgcolor='rgba(0,0,0,0)' # Fondo del gráfico transparente
    )

    return fig, dataset_countries
