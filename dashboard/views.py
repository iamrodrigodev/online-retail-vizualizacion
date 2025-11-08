from django.shortcuts import render
from django.http import JsonResponse
import json
import plotly.utils
from .visualizations.world_map.plot import create_world_map_plot
from .visualizations.customer_profiles.plot import create_customer_profiles_plot
from .visualizations.sales.plot import create_sales_trend_plot

def index(request):
    # 1. Crear el mapa mundial desde nuestra nueva función de visualización
    world_map_fig, dataset_countries = create_world_map_plot()

    # 2. Crear el gráfico de perfiles de cliente (global inicialmente)
    customer_profiles_fig = create_customer_profiles_plot()

    # 3. Crear el gráfico de tendencia de ventas (global inicialmente)
    sales_trend_fig = create_sales_trend_plot()

    # 4. Convertir las figuras de Plotly a strings JSON para el frontend
    world_map_json = json.dumps(world_map_fig, cls=plotly.utils.PlotlyJSONEncoder)
    customer_profiles_json = json.dumps(customer_profiles_fig, cls=plotly.utils.PlotlyJSONEncoder)
    sales_trend_json = json.dumps(sales_trend_fig, cls=plotly.utils.PlotlyJSONEncoder)

    # 5. Pasar los JSONs al contexto de la plantilla
    context = {
        'worldMapJSON': world_map_json,
        'customerProfilesJSON': customer_profiles_json,
        'salesTrendJSON': sales_trend_json,
        'dataset_countries': json.dumps(dataset_countries)
    }

    return render(request, 'index.html', context)


def get_customer_profiles_by_country(request, country):
    """
    API endpoint para obtener perfiles de cliente por país
    """
    # Crear el gráfico filtrado por país
    customer_profiles_fig = create_customer_profiles_plot(country=country)
    
    # Convertir a JSON
    customer_profiles_json = json.dumps(customer_profiles_fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    return JsonResponse({
        'graph': customer_profiles_json,
        'country': country
    })


def get_sales_trend(request):
    """
    API endpoint para obtener tendencia de ventas con filtros opcionales
    """
    country = request.GET.get('country', None)
    customer_profile = request.GET.get('profile', None)
    
    # Crear el gráfico con los filtros aplicados
    sales_trend_fig = create_sales_trend_plot(country=country, customer_profile=customer_profile)
    
    # Convertir a JSON
    sales_trend_json = json.dumps(sales_trend_fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    return JsonResponse({
        'graph': sales_trend_json,
        'country': country,
        'profile': customer_profile
    })

