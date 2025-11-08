"""
Generador de gráfico de tendencia de ventas diarias.
"""
import plotly.graph_objects as go
from dashboard.visualizations.sales.data_processor import get_sales_trend_data


def create_sales_trend_plot(country=None, customer_profile=None):
    """
    Crea una figura de Plotly con la tendencia de ventas diarias.
    
    Args:
        country: País para filtrar (opcional)
        customer_profile: Perfil de cliente para filtrar (opcional)
    
    Returns:
        Figura de Plotly
    """
    data = get_sales_trend_data(country, customer_profile)
    
    if not data:
        return go.Figure()
    
    years = data['years']
    data_by_year = data['data_by_year']
    
    # Colores para cada año
    colores_anuales = ['#FF7F0E', '#2CA02C', '#E377C2']
    
    fig = go.Figure()
    
    # Agregar una traza por cada año
    for i, year in enumerate(years):
        year_data = data_by_year[year]
        
        fig.add_trace(go.Scatter(
            x=year_data['dates'],
            y=year_data['sales'],
            mode='lines',
            line=dict(
                color=colores_anuales[i % len(colores_anuales)],
                width=2.5
            ),
            name=f"{year}",
            hovertemplate='<b>Año:</b> ' + str(year) + 
                         '<br><b>Fecha:</b> %{x}' +
                         '<br><b>Ventas:</b> £%{y:,.2f}' +
                         '<extra></extra>',
            visible=True
        ))
    
    # Determinar el título según los filtros aplicados
    if country and customer_profile:
        title_text = f"Tendencia de Ventas en {country} - {customer_profile}"
    elif country:
        title_text = f"Tendencia de Ventas en {country}"
    elif customer_profile:
        title_text = f"Tendencia de Ventas - {customer_profile}"
    else:
        title_text = "Tendencia de Ventas"
    
    # Configurar el layout
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
                'text': 'Fecha',
                'font': {'size': 14, 'color': '#2c3e50'}
            },
            'showgrid': True,
            'gridcolor': 'lightgray',
            'tickfont': {'size': 12, 'color': '#2c3e50'}
        },
        yaxis={
            'title': {
                'text': 'Ventas (£)',
                'font': {'size': 14, 'color': '#2c3e50'}
            },
            'showgrid': True,
            'gridcolor': 'lightgray',
            'tickfont': {'size': 12, 'color': '#2c3e50'}
        },
        plot_bgcolor='white',
        paper_bgcolor='rgba(0,0,0,0)',
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor='white',
            font_size=12,
            font_family='Arial',
            bordercolor='#cccccc'
        ),
        showlegend=False,  # Ocultar la leyenda de años
        margin={"r": 20, "t": 100, "l": 60, "b": 80},
        dragmode=False,
        xaxis_fixedrange=True,
        yaxis_fixedrange=True
    )
    
    return fig
