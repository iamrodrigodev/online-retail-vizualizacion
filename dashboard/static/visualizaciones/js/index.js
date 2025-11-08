document.addEventListener('DOMContentLoaded', function () {
    const loader = document.getElementById('loader');
    const contentContainer = document.getElementById('content-container');
    const mapDiv = document.getElementById('worldMap');

    if (mapDiv && contentContainer && loader && typeof Plotly !== 'undefined' && typeof graphData !== 'undefined') {
        Plotly.newPlot(mapDiv, graphData.data, graphData.layout, {
            responsive: true,
            displayModeBar: false
        }).then(function() {
            // Una vez que el gráfico se ha renderizado, oculta el loader y muestra el contenido
            loader.style.display = 'none';
            contentContainer.style.display = 'block';
        });

        // Lógica para la interactividad del cursor y clics
        mapDiv.on('plotly_hover', function (data) {
            const point = data.points[0];
            const countryName = point.location;

            if (!countriesWithData.has(countryName)) {
                mapDiv.style.cursor = 'not-allowed';
            } else {
                mapDiv.style.cursor = 'pointer';
            }
        });

        mapDiv.on('plotly_unhover', function () {
            mapDiv.style.cursor = 'default';
        });

        mapDiv.on('plotly_click', function (data) {
            const point = data.points[0];
            const countryName = point.location;

            if (!countriesWithData.has(countryName)) {
                return false;
            }
        });
    } else {
        // Si algo falla, muestra un mensaje de error al usuario
        if (loader) {
            loader.textContent = 'Error al cargar los datos del mapa.';
        }
        console.error('No se pudo renderizar el mapa. Faltan elementos (div, Plotly) o datos (graphData).');
    }
});
