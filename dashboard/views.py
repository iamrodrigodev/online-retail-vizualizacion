from django.shortcuts import render
import json
import plotly.utils
from .visualizations.world_map.plot import create_world_map_plot

def index(request):
    # 1. Crear el mapa mundial desde nuestra nueva función de visualización
    world_map_fig, dataset_countries = create_world_map_plot()

    # 2. Convertir la figura de Plotly a un string JSON para el frontend
    graphJSON = json.dumps(world_map_fig, cls=plotly.utils.PlotlyJSONEncoder)

    # 3. Pasar el JSON del gráfico y la lista de países al contexto de la plantilla
    context = {
        'graphJSON': graphJSON,
        'dataset_countries': json.dumps(dataset_countries)
    }

    return render(request, 'index.html', context)
