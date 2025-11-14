from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
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
import polars as pl

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
    
    print(f"DEBUG - get_top_products: country={country}, profile={customer_profile}, dates={start_date} to {end_date}")
    
    # Crear el gráfico con los filtros aplicados
    top_products_fig = create_top_products_plot(
        country=country, 
        customer_profile=customer_profile,
        start_date=start_date,
        end_date=end_date
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
    try:
        # Parsear datos JSON del body
        data = json.loads(request.body)
        
        # Extraer parámetros
        customer_id = data.get('customer_id', None)
        k = int(data.get('k', 10))
        metric = data.get('metric', 'euclidean')
        normalization = data.get('normalization', 'zscore')
        dimred = data.get('dimred', 'pca')
        x_axis = data.get('x_axis', None)
        y_axis = data.get('y_axis', None)
        
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
        
        # Calcular el gráfico
        result = compute_client_similarity_graph(
            customer_id=customer_id,
            k=k,
            metric=metric,
            normalization=normalization,
            dimred=dimred,
            x_axis=x_axis,
            y_axis=y_axis
        )
        
        return JsonResponse(result)
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    except Exception as e:
        print(f"Error en compute_client_similarity: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)


def get_customer_ids(request):
    """
    API endpoint para obtener todos los IDs de clientes disponibles
    """
    try:
        customer_ids = get_all_customer_ids()
        return JsonResponse({
            'customer_ids': customer_ids,
            'total': len(customer_ids)
        })
    except Exception as e:
        print(f"Error en get_customer_ids: {e}")
        return JsonResponse({'error': str(e)}, status=500)

