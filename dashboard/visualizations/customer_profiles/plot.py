import plotly.graph_objects as go
from dashboard.visualizations.customer_profiles.data_processor import get_customer_profiles_data


def create_customer_profiles_plot(country=None):
    """
    Crea una figura de Plotly con un gráfico de barras de perfiles de cliente.
    Si se proporciona un país, muestra datos específicos de ese país.
    """
    data = get_customer_profiles_data(country)
    
    if not data:
        # Retorna una figura vacía si no hay datos
        return go.Figure()
    
    perfiles = data['perfiles']
    percentages = data['percentages']
    counts = data['counts']
    
    # Colores para cada perfil
    color_map = {
        'Minorista Estándar': '#9b59b6',  # Morado
        'Mayorista Estándar': '#28a745',  # Verde
        'Minorista Lujo': '#ffc107',      # Amarillo
        'Mayorista Lujo': '#0824a4'       # Azul La Salle
    }
    
    colors = [color_map.get(perfil, '#6c757d') for perfil in perfiles]
    
    # Crear el gráfico de barras
    fig = go.Figure(data=[
        go.Bar(
            x=perfiles,
            y=percentages,
            text=[f'{pct:.1f}%' for pct in percentages],
            textposition='outside',
            marker=dict(
                color=colors,
                line=dict(color='white', width=2)
            ),
            hovertemplate='<b>%{x}</b><br>' +
                         'Porcentaje: %{y:.2f}%<br>' +
                         'Transacciones: %{customdata:,}<br>' +
                         '<extra></extra>',
            customdata=counts
        )
    ])
    
    # Determinar el título según si hay país seleccionado
    if country:
        title_text = f'Perfiles de Cliente - {country}'
    else:
        title_text = 'Perfiles de Cliente - Global'
    
    # Actualizar el layout
    fig.update_layout(
        title={
            'text': title_text,
            'x': 0.5,
            'xanchor': 'center',
            'font': {
                'size': 24,
                'color': '#0824a4',
                'family': 'Arial, sans-serif'
            }
        },
        xaxis={
            'title': {
                'text': 'Perfil de Cliente',
                'font': {'size': 14, 'color': '#2c3e50'}
            },
            'tickfont': {'size': 12, 'color': '#2c3e50'}
        },
        yaxis={
            'title': {
                'text': 'Porcentaje (%)',
                'font': {'size': 14, 'color': '#2c3e50'}
            },
            'tickfont': {'size': 12, 'color': '#2c3e50'},
            'range': [0, max(percentages) * 1.15]  # Espacio para los labels
        },
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin={"r": 20, "t": 80, "l": 60, "b": 80},
        showlegend=False,
        annotations=[
            dict(
                text=f'Total de transacciones: {data["total_transacciones"]:,}',
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
    
    return fig
