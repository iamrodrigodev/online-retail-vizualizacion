document.addEventListener('DOMContentLoaded', function () {
    const loader = document.getElementById('loader');
    const contentContainer = document.getElementById('content-container');
    const mapDiv = document.getElementById('worldMap');
    const profilesDiv = document.getElementById('customerProfiles');
    
    // Variable para almacenar el país seleccionado
    let selectedCountry = null;
    // Array de todos los países con datos (convertir Set a Array)
    const allCountries = Array.from(countriesWithData);

    if (mapDiv && profilesDiv && contentContainer && loader && 
        typeof Plotly !== 'undefined' && 
        typeof worldMapData !== 'undefined' && 
        typeof customerProfilesData !== 'undefined') {
        
        // Guardar la escala y centro inicial del mapa
        const initialScale = worldMapData.layout.geo?.projection?.scale || 1.0;
        const initialRotation = worldMapData.layout.geo?.projection?.rotation || {lon: 0, lat: 0, roll: 0};
        const initialCenter = worldMapData.layout.geo?.center || {lon: 0, lat: 0};
        
        // Límites de latitud (arriba/abajo)
        const maxLatOffset = 60; // Grados máximos de desplazamiento vertical
        
        // Renderizar el mapa mundial
        Plotly.newPlot(mapDiv, worldMapData.data, worldMapData.layout, {
            responsive: true,
            displayModeBar: false,
            scrollZoom: false,  // Deshabilitar zoom automático de Plotly
            doubleClick: 'reset'  // Doble click para resetear vista
        }).then(function() {
            // Renderizar el gráfico de perfiles de cliente
            return Plotly.newPlot(profilesDiv, customerProfilesData.data, customerProfilesData.layout, {
                responsive: true,
                displayModeBar: false
            });
        }).then(function() {
            // Una vez que ambos gráficos se han renderizado, oculta el loader y muestra el contenido
            loader.style.display = 'none';
            contentContainer.style.display = 'block';
            
            // Implementar zoom manual con límite para el mapa
            mapDiv.addEventListener('wheel', function(e) {
                e.preventDefault();
                
                const currentScale = mapDiv.layout.geo?.projection?.scale || initialScale;
                const zoomFactor = 0.1;
                let newScale;
                
                if (e.deltaY < 0) {
                    // Zoom in (acercar)
                    newScale = currentScale * (1 + zoomFactor);
                } else {
                    // Zoom out (alejar)
                    newScale = currentScale * (1 - zoomFactor);
                    // No permitir escala menor a la inicial
                    if (newScale < initialScale) {
                        newScale = initialScale;
                    }
                }
                
                // Aplicar el nuevo zoom
                Plotly.relayout(mapDiv, {'geo.projection.scale': newScale});
            }, { passive: false });
        });
        
        // Interceptar eventos de relayout para limitar el movimiento vertical del mapa
        mapDiv.on('plotly_relayout', function(eventData) {
            // Verificar si hay cambios en el centro del mapa (movimiento)
            if (eventData['geo.center.lat'] !== undefined) {
                const newLat = eventData['geo.center.lat'];
                const currentScale = mapDiv.layout.geo?.projection?.scale || initialScale;
                
                // Solo limitar cuando estamos en escala inicial (sin zoom)
                if (currentScale <= initialScale) {
                    // Limitar el desplazamiento vertical
                    if (Math.abs(newLat - initialCenter.lat) > maxLatOffset) {
                        const limitedLat = newLat > initialCenter.lat 
                            ? initialCenter.lat + maxLatOffset 
                            : initialCenter.lat - maxLatOffset;
                        
                        Plotly.relayout(mapDiv, {'geo.center.lat': limitedLat});
                    }
                }
            }
        });

        // Lógica para la interactividad del cursor
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

        // Lógica para manejar los clics en países
        mapDiv.on('plotly_click', function (data) {
            const point = data.points[0];
            const countryName = point.location;

            // Verificar que el país esté en el dataset
            if (!countriesWithData.has(countryName)) {
                return false;
            }
            
            // Si se hace click en el país ya seleccionado, deseleccionarlo
            if (selectedCountry === countryName) {
                selectedCountry = null;
                
                // Actualizar ambos traces: todos los países en gris, ninguno en azul
                Plotly.update(mapDiv, {
                    'locations': [allCountries, ['']],
                    'z': [[...Array(allCountries.length).fill(1)], [1]]
                }, {}, [0, 1]);
                
                // Volver a mostrar datos globales en el gráfico de perfiles
                Plotly.react(profilesDiv, customerProfilesData.data, customerProfilesData.layout);
            } else {
                // Seleccionar el nuevo país
                // Filtrar el país seleccionado de la lista de países con ventas
                const countriesWithoutSelected = allCountries.filter(c => c !== countryName);
                
                selectedCountry = countryName;
                
                // Actualizar ambos traces: países sin el seleccionado en gris, país seleccionado en azul
                Plotly.update(mapDiv, {
                    'locations': [countriesWithoutSelected, [countryName]],
                    'z': [[...Array(countriesWithoutSelected.length).fill(1)], [1]]
                }, {}, [0, 1]);
                
                // Actualizar el gráfico de perfiles de cliente con datos del país seleccionado
                fetch(`/api/customer-profiles/${encodeURIComponent(countryName)}/`)
                    .then(response => response.json())
                    .then(data => {
                        const newGraphData = JSON.parse(data.graph);
                        Plotly.react(profilesDiv, newGraphData.data, newGraphData.layout);
                    })
                    .catch(error => {
                        console.error('Error al cargar perfiles por país:', error);
                    });
            }
        });
    } else {
        // Si algo falla, muestra un mensaje de error al usuario
        if (loader) {
            loader.textContent = 'Error al cargar los datos del mapa.';
        }
        console.error('No se pudo renderizar el mapa. Faltan elementos (div, Plotly) o datos (worldMapData).');
    }
});
