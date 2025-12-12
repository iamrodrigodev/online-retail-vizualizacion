from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie
import json
import plotly.utils
from .visualizations.world_map.plot import create_world_map_plot
from .visualizations.customer_profiles.plot import create_customer_profiles_plot
from .visualizations.sales.plot import create_sales_trend_plot
from .visualizations.products.plot import create_top_products_plot
from .visualizations.shared.data_loader import load_online_retail_data
from .visualizations.client_similarity.data_processor import (
    compute_client_similarity_graph,
    get_all_customer_ids
)
from .visualizations.client_similarity.plot import create_client_similarity_plot
from .visualizations.products.data_processor import get_categories_and_subcategories
from .visualizations.sales.detail_analyzer import get_daily_sales_detail
import polars as pl

@ensure_csrf_cookie
def index(request):
    # 1. Crear el mapa mundial desde nuestra nueva función de visualización
    world_map_fig, dataset_countries = create_world_map_plot()

    # 2. Crear el gráfico de perfiles de cliente (global inicialmente)
    customer_profiles_fig = create_customer_profiles_plot()

    # 3. Crear el gráfico de tendencia de ventas (global inicialmente)
    sales_trend_fig = create_sales_trend_plot()

    # 4. Crear el gráfico de top productos (global inicialmente)
    top_products_fig = create_top_products_plot()

    # 5. Obtener el rango de fechas del dataset
    df = load_online_retail_data()
    date_range = {'min': None, 'max': None}
    
    if df is not None and df.height > 0:
        df = df.with_columns([
            pl.col('InvoiceDate').str.strptime(pl.Datetime, "%Y-%m-%d %H:%M:%S").alias('InvoiceDate')
        ])
        min_date = df['InvoiceDate'].min()
        max_date = df['InvoiceDate'].max()
        
        if min_date and max_date:
            date_range = {
                'min': min_date.strftime('%Y-%m'),
                'max': max_date.strftime('%Y-%m')
            }

    # 6. Convertir las figuras de Plotly a strings JSON para el frontend
    world_map_json = json.dumps(world_map_fig, cls=plotly.utils.PlotlyJSONEncoder)
    customer_profiles_json = json.dumps(customer_profiles_fig, cls=plotly.utils.PlotlyJSONEncoder)
    sales_trend_json = json.dumps(sales_trend_fig, cls=plotly.utils.PlotlyJSONEncoder)
    top_products_json = json.dumps(top_products_fig, cls=plotly.utils.PlotlyJSONEncoder)

    # 7. Pasar los JSONs al contexto de la plantilla
    context = {
        'worldMapJSON': world_map_json,
        'customerProfilesJSON': customer_profiles_json,
        'salesTrendJSON': sales_trend_json,
        'topProductsJSON': top_products_json,
        'dataset_countries': json.dumps(dataset_countries),
        'date_range': json.dumps(date_range)
    }

    return render(request, 'index.html', context)


def get_customer_profiles_by_country(request, country):
    """
    API endpoint para obtener perfiles de cliente por país
    """
    # Obtener filtros de fecha si existen
    start_date = request.GET.get('start_date', None)
    end_date = request.GET.get('end_date', None)
    
    # Crear el gráfico filtrado por país y fechas
    customer_profiles_fig = create_customer_profiles_plot(
        country=country, 
        start_date=start_date, 
        end_date=end_date
    )
    
    # Convertir a JSON
    customer_profiles_json = json.dumps(customer_profiles_fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    return JsonResponse({
        'graph': customer_profiles_json,
        'country': country
    })


def get_customer_profiles_global(request):
    """
    API endpoint para obtener perfiles de cliente globales con filtros de fecha
    """
    start_date = request.GET.get('start_date', None)
    end_date = request.GET.get('end_date', None)
    
    # Crear el gráfico con filtros de fecha
    customer_profiles_fig = create_customer_profiles_plot(
        country=None,
        start_date=start_date, 
        end_date=end_date
    )
    
    # Convertir a JSON
    customer_profiles_json = json.dumps(customer_profiles_fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    return JsonResponse({
        'graph': customer_profiles_json
    })


def get_sales_trend(request):
    """
    API endpoint para obtener tendencia de ventas con filtros opcionales
    """
    country = request.GET.get('country', None)
    customer_profile = request.GET.get('profile', None)
    start_date = request.GET.get('start_date', None)
    end_date = request.GET.get('end_date', None)
    
    print(f"DEBUG - get_sales_trend: country={country}, profile={customer_profile}, dates={start_date} to {end_date}")
    
    # Crear el gráfico con los filtros aplicados
    sales_trend_fig = create_sales_trend_plot(
        country=country, 
        customer_profile=customer_profile,
        start_date=start_date,
        end_date=end_date
    )
    
    # Convertir a JSON
    sales_trend_json = json.dumps(sales_trend_fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    return JsonResponse({
        'graph': sales_trend_json,
        'country': country,
        'profile': customer_profile
    })


def get_top_products(request):
    """
    API endpoint para obtener top 5 productos con filtros opcionales
    """
    country = request.GET.get('country', None)
    customer_profile = request.GET.get('profile', None)
    start_date = request.GET.get('start_date', None)
    end_date = request.GET.get('end_date', None)
    category = request.GET.get('category', None)
    subcategory = request.GET.get('subcategory', None)

    print(f"DEBUG - get_top_products: country={country}, profile={customer_profile}, dates={start_date} to {end_date}, category={category}, subcategory={subcategory}")

    # Crear el gráfico con los filtros aplicados
    top_products_fig = create_top_products_plot(
        country=country,
        customer_profile=customer_profile,
        start_date=start_date,
        end_date=end_date,
        category=category,
        subcategory=subcategory
    )
    
    # Convertir a JSON
    top_products_json = json.dumps(top_products_fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    return JsonResponse({
        'graph': top_products_json,
        'country': country,
        'profile': customer_profile
    })


@require_http_methods(["POST"])
def compute_client_similarity(request):
    """
    API endpoint para calcular el gráfico de similitud de clientes
    """
    import sys
    try:
        print("=== INICIO compute_client_similarity ===", file=sys.stderr)
        
        # Parsear datos JSON del body
        data = json.loads(request.body)
        print(f"Datos recibidos: {data}", file=sys.stderr)
        
        # Extraer parámetros
        customer_id = data.get('customer_id', None)
        k = int(data.get('k', 10))
        metric = data.get('metric', 'euclidean')
        normalization = data.get('normalization', 'zscore')
        dimred = data.get('dimred', 'pca')
        x_axis = data.get('x_axis', None)
        y_axis = data.get('y_axis', None)
        country = data.get('country', None)
        start_date = data.get('start_date', None)
        end_date = data.get('end_date', None)
        
        print(f"Filtros: country={country}, start_date={start_date}, end_date={end_date}", file=sys.stderr)
        
        # Convertir a enteros si están presentes
        if x_axis is not None:
            x_axis = int(x_axis)
        if y_axis is not None:
            y_axis = int(y_axis)
        
        # Validar parámetros
        if k < 1 or k > 500:
            return JsonResponse({'error': 'K debe estar entre 1 y 500'}, status=400)
        
        if metric not in ['euclidean', 'cosine', 'pearson']:
            return JsonResponse({'error': 'Métrica no válida'}, status=400)
        
        if normalization not in ['zscore', 'minmax_01']:
            return JsonResponse({'error': 'Normalización no válida'}, status=400)
        
        if dimred not in ['pca']:
            return JsonResponse({'error': 'Solo PCA está soportado'}, status=400)
        
        print("Iniciando cálculo...", file=sys.stderr)
        
        # Calcular el gráfico
        result = compute_client_similarity_graph(
            customer_id=customer_id,
            k=k,
            metric=metric,
            normalization=normalization,
            dimred=dimred,
            x_axis=x_axis,
            y_axis=y_axis,
            country=country,
            start_date=start_date,
            end_date=end_date
        )
        
        print(f"Cálculo completado. Total clientes: {result.get('total_customers', 0)}", file=sys.stderr)
        
        # Verificar si hay datos en el resultado
        if not result or not result.get('embedding'):
            return JsonResponse({
                'error': 'No hay datos disponibles para los filtros seleccionados',
                'details': {
                    'country': country,
                    'start_date': start_date,
                    'end_date': end_date,
                    'customer_id': customer_id
                }
            }, status=404)
        
        print("=== FIN compute_client_similarity (éxito) ===", file=sys.stderr)
        return JsonResponse(result)
    
    except json.JSONDecodeError as e:
        print(f"ERROR JSON: {e}", file=sys.stderr)
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    except Exception as e:
        print(f"ERROR en compute_client_similarity: {type(e).__name__}: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return JsonResponse({'error': f'Error interno: {str(e)}'}, status=500)


def get_customer_ids(request):
    """
    API endpoint para obtener todos los IDs de clientes disponibles
    """
    try:
        # Obtener filtros opcionales
        country = request.GET.get('country', None)
        start_date = request.GET.get('start_date', None)
        end_date = request.GET.get('end_date', None)

        customer_ids = get_all_customer_ids(
            country=country,
            start_date=start_date,
            end_date=end_date
        )
        return JsonResponse({
            'customer_ids': customer_ids,
            'total': len(customer_ids)
        })
    except Exception as e:
        print(f"Error en get_customer_ids: {e}")
        return JsonResponse({'error': str(e)}, status=500)


def get_categories(request):
    """
    API endpoint para obtener categorías y subcategorías disponibles
    """
    try:
        data = get_categories_and_subcategories()
        return JsonResponse(data)
    except Exception as e:
        print(f"Error en get_categories: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["POST"])
def get_products_by_customers(request):
    """
    API endpoint para obtener el Top 5 de productos comprados por una lista de clientes
    Retorna un gráfico completo de Plotly
    """
    import sys
    try:
        # Parsear datos JSON del body
        data = json.loads(request.body)
        customer_ids = data.get('customer_ids', [])
        category = data.get('category', None)
        subcategory = data.get('subcategory', None)

        print(f"CustomerIDs recibidos: {customer_ids[:5]}...", file=sys.stderr)
        print(f"Filtros: category={category}, subcategory={subcategory}", file=sys.stderr)

        if not customer_ids:
            return JsonResponse({'error': 'No se proporcionaron CustomerIDs'}, status=400)

        # Convertir customer_ids a strings en el mismo formato que el dataset
        customer_ids_str = []
        for cid in customer_ids:
            try:
                # Convertir a int primero (para limpiar), luego a string
                customer_ids_str.append(str(int(float(str(cid)))))
            except (ValueError, TypeError):
                print(f"Error convirtiendo CustomerID: {cid}", file=sys.stderr)
                continue

        print(f"CustomerIDs convertidos: {customer_ids_str[:5]}...", file=sys.stderr)

        # Cargar datos
        df = load_online_retail_data()

        if df.is_empty():
            return JsonResponse({'error': 'No hay datos disponibles'}, status=404)

        print(f"Dataset cargado, shape: {df.shape}", file=sys.stderr)
        print(f"CustomerID type en dataset: {df['CustomerID'].dtype}", file=sys.stderr)

        # Convertir CustomerID del dataset: String -> Float -> Int -> String (para remover .0)
        df = df.with_columns([
            pl.col('CustomerID').cast(pl.Float64).cast(pl.Int64).cast(pl.Utf8).alias('CustomerID')
        ])

        print(f"CustomerID convertido a string en dataset (sin .0)", file=sys.stderr)

        # Filtrar por CustomerIDs usando comparación de strings
        filters = [
            (pl.col('CustomerID').is_not_null()),
            (pl.col('CustomerID').is_in(customer_ids_str)),
            (pl.col('Description').is_not_null()),
            (pl.col('Description') != ''),
            (pl.col('Quantity') > 0)
        ]

        # Agregar filtros de categoría si existen
        if category:
            filters.append(pl.col('Category') == category)
            print(f"Filtro de categoría aplicado: {category}", file=sys.stderr)

        if subcategory:
            filters.append(pl.col('Subcategory') == subcategory)
            print(f"Filtro de subcategoría aplicado: {subcategory}", file=sys.stderr)

        # Aplicar todos los filtros
        df_filtered = df.filter(pl.all_horizontal(filters))

        print(f"Filas después de filtrar: {df_filtered.height}", file=sys.stderr)

        if df_filtered.is_empty():
            print(f"No hay productos. Verificando CustomerIDs en dataset...", file=sys.stderr)
            unique_customers = df.filter(pl.col('CustomerID').is_not_null())['CustomerID'].unique().to_list()
            print(f"CustomerIDs únicos en dataset (primeros 10): {unique_customers[:10]}", file=sys.stderr)
            return JsonResponse({'error': 'No hay productos para los clientes seleccionados'}, status=404)

        # Calcular Top 5 productos por cantidad total vendida
        top_products = df_filtered.group_by('Description').agg([
            pl.col('Quantity').sum().alias('TotalQuantity')
        ]).sort('TotalQuantity', descending=True).head(5)

        if top_products.is_empty():
            return JsonResponse({'error': 'No hay productos disponibles'}, status=404)

        # Extraer datos para el gráfico
        products = top_products['Description'].to_list()
        quantities = top_products['TotalQuantity'].to_list()

        # Crear gráfico de barras horizontales (como el original)
        import plotly.graph_objects as go

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=quantities,
            y=products,
            orientation='h',
            marker=dict(color='#FF5722'),  # Naranja para indicar que es filtrado
            text=[f'{q:,}' for q in quantities],
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>Cantidad: %{x:,}<extra></extra>'
        ))

        # Calcular total de cantidad vendida
        total_quantity = sum(quantities)

        # Construir título dinámico
        title_parts = []
        if category and subcategory:
            title_parts.append(f'{subcategory}')
        elif category:
            title_parts.append(f'{category}')

        if title_parts:
            title_text = f'{" - ".join(title_parts)}: Top Compras de {len(customer_ids)} Clientes'
        else:
            title_text = f'Productos Más Comprados por {len(customer_ids)} Clientes Seleccionados'

        # Layout del gráfico
        fig.update_layout(
            title={
                'text': title_text,
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18, 'color': '#FF5722', 'family': 'Arial, sans-serif'}
            },
            xaxis=dict(
                title='Cantidad Vendida',
                showgrid=True,
                gridcolor='rgba(200, 200, 200, 0.2)'
            ),
            yaxis=dict(
                title='',
                autorange='reversed'
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=200, r=50, t=100, b=50),  # Aumentado margen superior de 80 a 100
            height=400,
            annotations=[
                dict(
                    text=f'Total vendido: {total_quantity:,} unidades',
                    xref='paper',
                    yref='paper',
                    x=0.5,
                    y=1.05,  # Ajustado de 1.08 a 1.05 para evitar solapamiento
                    xanchor='center',
                    yanchor='bottom',
                    showarrow=False,
                    font=dict(
                        size=11,
                        color='#666666',
                        family='Arial, sans-serif'
                    )
                )
            ]
        )

        # Convertir a JSON
        graph_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

        return JsonResponse({
            'graph': graph_json,
            'total_products': len(products),
            'total_customers': len(customer_ids)
        })

    except json.JSONDecodeError as e:
        print(f"ERROR JSON en get_products_by_customers: {e}")
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    except Exception as e:
        print(f"Error en get_products_by_customers: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)


def get_sales_detail(request, date):
    """
    API endpoint para obtener análisis detallado de ventas de un día específico

    Args:
        date: Fecha en formato YYYY-MM-DD

    Query params:
        country: País para filtrar (opcional)
        profile: Perfil de cliente para filtrar (opcional)
        start_date: Fecha de inicio del rango general (opcional)
        end_date: Fecha de fin del rango general (opcional)
    """
    try:
        # Obtener filtros opcionales
        country = request.GET.get('country', None)
        customer_profile = request.GET.get('profile', None)
        start_date = request.GET.get('start_date', None)
        end_date = request.GET.get('end_date', None)

        print(f"DEBUG - get_sales_detail: date={date}, country={country}, profile={customer_profile}")

        # Obtener análisis detallado
        detail = get_daily_sales_detail(
            date_str=date,
            country=country,
            customer_profile=customer_profile,
            start_date=start_date,
            end_date=end_date
        )

        if detail is None:
            return JsonResponse({
                'error': f'No hay datos disponibles para la fecha {date}'
            }, status=404)

        return JsonResponse(detail)

    except ValueError as e:
        return JsonResponse({
            'error': f'Formato de fecha inválido: {str(e)}'
        }, status=400)
    except Exception as e:
        print(f"Error en get_sales_detail: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)

