"""
Generador de gráfico de Top 5 productos más vendidos.
"""
import plotly.graph_objects as go
from dashboard.visualizations.products.data_processor import get_top_products_data


def create_top_products_plot(country=None, customer_profile=None, start_date=None, end_date=None, category=None, subcategory=None):
    """
    Crea una figura de Plotly con el Top 5 de productos más vendidos.

    Args:
        country: País para filtrar (opcional)
        customer_profile: Perfil de cliente para filtrar (opcional)
        start_date: Fecha de inicio en formato YYYY-MM (opcional)
        end_date: Fecha de fin en formato YYYY-MM (opcional)
        category: Categoría para filtrar (opcional)
        subcategory: Subcategoría para filtrar (opcional)

    Returns:
        Figura de Plotly
    """
    print(f"DEBUG - create_top_products_plot: country={country}, profile={customer_profile}, dates={start_date} to {end_date}, category={category}, subcategory={subcategory}")

    data = get_top_products_data(country, customer_profile, start_date, end_date, category, subcategory)
    
    print(f"DEBUG - data received: {data}")
    
    if not data or data['total_products'] == 0:
        print("DEBUG - No hay datos, retornando figura vacía")
        # Retornar una figura con mensaje en lugar de figura vacía
        fig = go.Figure()
        fig.update_layout(
            title={
                'text': 'Top 5 Productos Más Vendidos',
                'x': 0.5,
                'xanchor': 'center',
                'font': {
                    'size': 20,
                    'color': '#0824a4',
                    'family': 'Arial, sans-serif'
                }
            },
            xaxis={'visible': False},
            yaxis={'visible': False},
            annotations=[{
                'text': 'No hay datos disponibles',
                'xref': 'paper',
                'yref': 'paper',
                'x': 0.5,
                'y': 0.5,
                'xanchor': 'center',
                'yanchor': 'middle',
                'showarrow': False,
                'font': {'size': 14, 'color': '#666'}
            }],
            margin={"r": 20, "t": 60, "l": 20, "b": 20}
        )
        return fig
    
    products = data['products']
    sales = data['sales']
    quantities = data['quantities']
    
    # Crear el gráfico de barras horizontales
    fig = go.Figure(data=[
        go.Bar(
            y=products,
            x=sales,
            orientation='h',
            marker=dict(
                color='#0824a4',
                line=dict(color='white', width=1.5)
            ),
            text=[f'£{s:,.0f}' for s in sales],
            textposition='outside',
            textfont=dict(size=11, color='#2c3e50'),
            hovertemplate='<b>%{y}</b><br>' +
                         'Ventas: £%{x:,.2f}<br>' +
                         'Cantidad: %{customdata:,}<br>' +
                         '<extra></extra>',
            customdata=quantities
        )
    ])
    
    # Determinar el título según los filtros aplicados
    if country and customer_profile:
        title_text = f"Top 5 Productos en {country} - {customer_profile}"
    elif country:
        title_text = f"Top 5 Productos en {country}"
    elif customer_profile:
        title_text = f"Top 5 Productos - {customer_profile}"
    else:
        title_text = "Top 5 Productos Más Vendidos"
    
    # Calcular el total de ventas para el subtítulo
    total_sales = sum(sales)
    
    # Configurar el layout
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
                'text': 'Ventas (£)',
                'font': {'size': 12, 'color': '#2c3e50'}
            },
            'showgrid': True,
            'gridcolor': 'lightgray',
            'tickfont': {'size': 11, 'color': '#2c3e50'},
            'fixedrange': True
        },
        yaxis={
            'title': {
                'text': '',
                'font': {'size': 12, 'color': '#2c3e50'}
            },
            'showgrid': False,
            'tickfont': {'size': 10, 'color': '#2c3e50'},
            'fixedrange': True
        },
        plot_bgcolor='white',
        paper_bgcolor='rgba(0,0,0,0)',
        margin={"r": 80, "t": 100, "l": 180, "b": 60},  # Aumentado margen superior de 60 a 100
        hovermode='closest',
        dragmode=False,
        annotations=[
            dict(
                text=f'Total de ventas (Top 5): £{total_sales:,.2f}',
                xref='paper',
                yref='paper',
                x=0.5,
                y=1.05,  # Ajustado de 1.08 a 1.05 para evitar solapamiento
                xanchor='center',
                yanchor='bottom',
                showarrow=False,
                font=dict(
                    size=11,
                    color='#666666',  # Color más suave
                    family='Arial, sans-serif'
                )
            )
        ]
    )
    
    return fig
