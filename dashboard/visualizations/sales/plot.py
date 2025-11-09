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
    
    # Variables para calcular el rango del eje Y
    all_sales = []
    total_points = 0
    total_sales_amount = 0  # Total acumulado de ventas
    
    # Agregar una traza por cada año
    for i, year in enumerate(years):
        year_data = data_by_year[year]
        all_sales.extend(year_data['sales'])
        total_sales_amount += sum(year_data['sales'])  # Sumar ventas de este año
        total_points += len(year_data['sales'])
        
        # Si hay pocos datos, mostrar puntos además de líneas
        mode = 'lines+markers' if total_points < 50 else 'lines'
        
        fig.add_trace(go.Scatter(
            x=year_data['dates'],
            y=year_data['sales'],
            mode=mode,
            line=dict(
                color=colores_anuales[i % len(colores_anuales)],
                width=2.5
            ),
            marker=dict(
                size=8,
                color=colores_anuales[i % len(colores_anuales)]
            ) if 'markers' in mode else None,
            name=f"{year}",
            hovertemplate='<b>Año:</b> ' + str(year) + 
                         '<br><b>Fecha:</b> %{x}' +
                         '<br><b>Ventas:</b> £%{y:,.2f}' +
                         '<extra></extra>',
            visible=True
        ))
    
    # Calcular rango apropiado para el eje Y
    if all_sales:
        min_sales = min(all_sales)
        max_sales = max(all_sales)
        
        print(f"DEBUG - Ventas: min={min_sales}, max={max_sales}, total_points={len(all_sales)}")
        
        # Agregar margen del 10% arriba y abajo
        margin = (max_sales - min_sales) * 0.1
        y_min = max(0, min_sales - margin)  # No permitir valores negativos
        y_max = max_sales + margin
        
        # Si el rango es muy pequeño, establecer un mínimo
        if (y_max - y_min) < 1:
            y_max = y_min + 10
            
        print(f"DEBUG - Rango Y: y_min={y_min}, y_max={y_max}")
    else:
        y_min = 0
        y_max = 100
        print("DEBUG - No hay datos de ventas, usando rango por defecto")
    
    # Determinar el título según los filtros aplicados
    if country and customer_profile:
        title_text = f"Ventas en {country} con Perfil {customer_profile}"
    elif country:
        title_text = f"Ventas en {country}"
    elif customer_profile:
        title_text = f"Ventas con Perfil {customer_profile}"
    else:
        title_text = "Ventas"
    
    print(f"DEBUG - plot.py: country={country}, profile={customer_profile}, title={title_text}")
    
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
            'tickfont': {'size': 12, 'color': '#2c3e50'},
            'range': [y_min, y_max],  # Rango dinámico basado en los datos
            'autorange': False
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
        margin={"r": 20, "t": 110, "l": 60, "b": 80},
        dragmode='zoom',  # Permitir zoom con selección
        xaxis_fixedrange=False,  # Permitir zoom en X
        yaxis_fixedrange=False,   # Permitir zoom en Y
        annotations=[
            dict(
                text=f'Total de ventas: £{total_sales_amount:,.2f}',
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
    
    return fig
