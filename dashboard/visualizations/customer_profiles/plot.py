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
    
    # Ajustar valores muy pequeños para que sean visibles
    # Si el porcentaje es menor a 1%, se muestra como 1% en la barra
    # pero se mantiene el valor real para el hover y texto
    percentages_display = [max(pct, 1.0) for pct in percentages]
    
    # Colores para cada perfil
    color_map = {
        'Minorista Estándar': '#9b59b6',  # Morado
        'Mayorista Estándar': '#28a745',  # Verde
        'Minorista Lujo': '#ffc107',      # Amarillo
        'Mayorista Lujo': '#00bcd4'       # Celeste
    }
    
    colors = [color_map.get(perfil, '#6c757d') for perfil in perfiles]
    
    # Crear el gráfico de barras
    fig = go.Figure(data=[
        go.Bar(
            x=perfiles,
            y=percentages_display,  # Usar valores ajustados para visualización
            text=[f'{pct:.1f}%' for pct in percentages],  # Texto con valor real
            textposition='auto',
            marker=dict(
                color=colors,
                line=dict(color='white', width=2)
            ),
            hovertemplate='<b>%{x}</b><br>' +
                         'Porcentaje: %{customdata[0]:.2f}%<br>' +
                         'Transacciones: %{customdata[1]:,}<br>' +
                         '<extra></extra>',
            customdata=list(zip(percentages, counts)),  # Pasar valor real para hover
            showlegend=False  # No mostrar las barras en la leyenda
        )
    ])
    
    # Determinar el título según si hay país seleccionado
    if country:
        title_text = f'Perfiles de Cliente en {country}'
    else:
        title_text = 'Perfiles de Cliente'
    
    # Actualizar el layout
    fig.update_layout(
        title={
            'text': title_text,
            'x': 0.5,
            'xanchor': 'center',
            'font': {
                'size': 20,
                'color': '#0824a4',
                'family': 'Arial, sans-serif'
            }
        },
        xaxis={
            'title': {
                'text': 'Perfil de Cliente',
                'font': {'size': 14, 'color': '#2c3e50'},
                'standoff': 0
            },
            'tickfont': {'size': 12, 'color': '#2c3e50'},
            'fixedrange': True
        },
        yaxis={
            'title': {
                'text': 'Porcentaje (%)',
                'font': {'size': 12, 'color': '#2c3e50'}
            },
            'tickfont': {'size': 11, 'color': '#2c3e50'},
            'range': [0, max(percentages_display) * 1.15],  # Espacio para los labels
            'fixedrange': True
        },
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    # Ajustar márgenes: espacio inferior para colocar la leyenda centrada debajo
    margin={"r": 20, "t": 110, "l": 50, "b": 110},
        autosize=True,
        showlegend=True,
        dragmode=False,
        hovermode='closest',
        # Colocar la leyenda fuera del área de trazado, abajo
        # Colocar la leyenda horizontal y centrada debajo del gráfico
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.25,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(255,255,255,0.95)",
            bordercolor="#cccccc",
            borderwidth=1,
            font=dict(size=9, color='#2c3e50'),
            itemclick=False,
            itemdoubleclick=False,
            itemsizing='constant'
        ),
        annotations=[
            dict(
                text=f'Total de transacciones: {data["total_transacciones"]:,}',
                xref='paper',
                yref='paper',
                x=0.5,
                y=1.08,
                xanchor='center',
                yanchor='bottom',
                showarrow=False,
                font=dict(
                    size=11,
                    color='#000000',
                    family='Arial, sans-serif'
                )
            )
        ]
    )
    
    # Agregar trazas invisibles para la leyenda
    # Leyenda de colores de perfiles
    for perfil, color in color_map.items():
        fig.add_trace(go.Scatter(
            x=[None],
            y=[None],
            mode='markers',
            marker=dict(size=10, color=color, symbol='square'),
            showlegend=True,
            name=perfil,
            hoverinfo='skip'
        ))
    
    # Leyenda para perfil seleccionado
    fig.add_trace(go.Scatter(
        x=[None],
        y=[None],
        mode='markers',
        marker=dict(size=10, color='#0824a4', symbol='square'),
        showlegend=True,
        name='Perfil seleccionado',
        hoverinfo='skip'
    ))
    
    return fig
