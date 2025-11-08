document.addEventListener('DOMContentLoaded', function () {
    const loader = document.getElementById('loader');
    const contentContainer = document.getElementById('content-container');
    const mapDiv = document.getElementById('worldMap');
    
    // Variable para almacenar el país seleccionado
    let selectedCountry = null;
    // Array de todos los países con datos (convertir Set a Array)
    const allCountries = Array.from(countriesWithData);

    if (mapDiv && contentContainer && loader && typeof Plotly !== 'undefined' && typeof graphData !== 'undefined') {
        // Guardar la escala y centro inicial
        const initialScale = graphData.layout.geo?.projection?.scale || 1.0;
        const initialRotation = graphData.layout.geo?.projection?.rotation || {lon: 0, lat: 0, roll: 0};
        const initialCenter = graphData.layout.geo?.center || {lon: 0, lat: 0};
        
        // Límites de latitud (arriba/abajo)
        const maxLatOffset = 60; // Grados máximos de desplazamiento vertical
        
        Plotly.newPlot(mapDiv, graphData.data, graphData.layout, {
            responsive: true,
            displayModeBar: false,
            scrollZoom: false,  // Deshabilitar zoom automático de Plotly
            doubleClick: 'reset'  // Doble click para resetear vista
        }).then(function() {
            // Una vez que el gráfico se ha renderizado, oculta el loader y muestra el contenido
            loader.style.display = 'none';
            contentContainer.style.display = 'block';
            
            // Implementar zoom manual con límite
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
        
        // Interceptar eventos de relayout para limitar el movimiento vertical
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
            
            console.log('Click detectado en:', countryName);

            // Verificar que el país esté en el dataset
            if (!countriesWithData.has(countryName)) {
                console.log('País no tiene datos, ignorando click');
                return false;
            }

            console.log('País válido, procesando selección');
            
            // Si se hace click en el país ya seleccionado, deseleccionarlo
            if (selectedCountry === countryName) {
                console.log('Deseleccionando país:', countryName);
                selectedCountry = null;
                
                // Actualizar ambos traces: todos los países en gris, ninguno en azul
                Plotly.update(mapDiv, {
                    'locations': [allCountries, ['']],
                    'z': [[...Array(allCountries.length).fill(1)], [1]]
                }, {}, [0, 1]).then(() => {
                    console.log('País deseleccionado exitosamente');
                }).catch(err => {
                    console.error('Error al deseleccionar:', err);
                });
            } else {
                // Seleccionar el nuevo país
                console.log('Seleccionando país:', countryName);
                
                // Filtrar el país seleccionado de la lista de países con ventas
                const countriesWithoutSelected = allCountries.filter(c => c !== countryName);
                
                selectedCountry = countryName;
                
                // Actualizar ambos traces: países sin el seleccionado en gris, país seleccionado en azul
                Plotly.update(mapDiv, {
                    'locations': [countriesWithoutSelected, [countryName]],
                    'z': [[...Array(countriesWithoutSelected.length).fill(1)], [1]]
                }, {}, [0, 1]).then(() => {
                    console.log('País seleccionado exitosamente:', countryName);
                }).catch(err => {
                    console.error('Error al seleccionar:', err);
                });
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
