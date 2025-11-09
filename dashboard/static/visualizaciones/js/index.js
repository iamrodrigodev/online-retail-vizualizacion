document.addEventListener('DOMContentLoaded', function () {
    const loader = document.getElementById('loader');
    const contentContainer = document.getElementById('content-container');
    const salesContainer = document.getElementById('sales-container');
    const mapDiv = document.getElementById('worldMap');
    const profilesDiv = document.getElementById('customerProfiles');
    const salesDiv = document.getElementById('salesTrend');
    const productsDiv = document.getElementById('topProducts');
    
    // Variable para almacenar el país seleccionado
    let selectedCountry = null;
    // Variable para almacenar el perfil seleccionado
    let selectedProfile = null;
    // Array de todos los países con datos (convertir Set a Array)
    const allCountries = Array.from(countriesWithData);
    
    // Mapa de colores originales de los perfiles
    const profileColors = {
        'Minorista Estándar': '#9b59b6',
        'Mayorista Estándar': '#28a745',
        'Minorista Lujo': '#ffc107',
        'Mayorista Lujo': '#00bcd4'
    };
    const selectedColor = '#0824a4'; // Color La Salle para selección

    if (mapDiv && profilesDiv && salesDiv && productsDiv && contentContainer && salesContainer && loader && 
        typeof Plotly !== 'undefined' && 
        typeof worldMapData !== 'undefined' && 
        typeof customerProfilesData !== 'undefined' &&
        typeof salesTrendData !== 'undefined' &&
        typeof topProductsData !== 'undefined') {
        
        // Función para actualizar el gráfico de tendencia de ventas
        function updateSalesTrend() {
            // Construir URL con parámetros
            let url = '/api/sales-trend/';
            const params = new URLSearchParams();
            
            if (selectedCountry) {
                params.append('country', selectedCountry);
            }
            if (selectedProfile) {
                params.append('profile', selectedProfile);
            }
            
            if (params.toString()) {
                url += '?' + params.toString();
            }
            
            console.log('Actualizando ventas con:', { country: selectedCountry, profile: selectedProfile, url: url });
            
            // Hacer petición al servidor
            fetch(url)
                .then(response => response.json())
                .then(data => {
                    const graphData = JSON.parse(data.graph);
                    
                    Plotly.react(salesDiv, graphData.data, graphData.layout).then(function() {
                        // Mantener dragmode en zoom (no deshabilitarlo)
                        Plotly.relayout(salesDiv, {
                            'dragmode': 'zoom'
                        });
                    });
                })
                .catch(error => {
                    console.error('Error al cargar tendencia de ventas:', error);
                });
        }
        
        // Función para actualizar el gráfico de top productos
        function updateTopProducts() {
            // Construir URL con parámetros
            let url = '/api/top-products/';
            const params = new URLSearchParams();
            
            if (selectedCountry) {
                params.append('country', selectedCountry);
            }
            if (selectedProfile) {
                params.append('profile', selectedProfile);
            }
            
            if (params.toString()) {
                url += '?' + params.toString();
            }
            
            console.log('Actualizando productos con:', { country: selectedCountry, profile: selectedProfile, url: url });
            
            // Hacer petición al servidor
            fetch(url)
                .then(response => response.json())
                .then(data => {
                    const graphData = JSON.parse(data.graph);
                    
                    Plotly.react(productsDiv, graphData.data, graphData.layout, {
                        responsive: true,
                        displayModeBar: false,
                        staticPlot: true
                    });
                })
                .catch(error => {
                    console.error('Error al cargar top productos:', error);
                });
        }
        
        // Función para configurar eventos de clic en el gráfico de perfiles
        function setupProfileClickEvents() {
            // Remover eventos anteriores para evitar duplicados
            profilesDiv.removeAllListeners('plotly_click');
            profilesDiv.removeAllListeners('plotly_hover');
            profilesDiv.removeAllListeners('plotly_unhover');
            
            // Agregar listener general al contenedor del gráfico para capturar todos los clicks
            const graphDiv = profilesDiv.querySelector('.svg-container');
            if (graphDiv) {
                // Remover listener previo si existe
                const oldListener = graphDiv._clickListener;
                if (oldListener) {
                    graphDiv.removeEventListener('click', oldListener);
                }
                
                // Crear nuevo listener
                const clickListener = function(event) {
                    // Obtener datos actuales
                    const currentData = profilesDiv.data[0];
                    if (!currentData || !currentData.x) return;
                    
                    const profiles = currentData.x;
                    
                    // Obtener el área del gráfico
                    const plotArea = profilesDiv.querySelector('.cartesianlayer .plot');
                    if (!plotArea) return;
                    
                    const rect = plotArea.getBoundingClientRect();
                    const clickX = event.clientX - rect.left;
                    
                    // Calcular el ancho de cada barra (dividir el área total entre el número de perfiles)
                    const totalWidth = rect.width;
                    const barWidth = totalWidth / profiles.length;
                    
                    // Determinar en qué barra se hizo click
                    const clickIndex = Math.floor(clickX / barWidth);
                    
                    // Verificar que el índice sea válido
                    if (clickIndex >= 0 && clickIndex < profiles.length) {
                        const clickedProfile = profiles[clickIndex];
                        
                        // Toggle selection
                        if (selectedProfile === clickedProfile) {
                            selectedProfile = null;
                            const originalColors = profiles.map(name => profileColors[name] || '#6c757d');
                            Plotly.restyle(profilesDiv, {'marker.color': [originalColors]}, [0]);
                            
                            // Actualizar gráficos de ventas y productos
                            updateSalesTrend();
                            updateTopProducts();
                        } else {
                            selectedProfile = clickedProfile;
                            const colors = profiles.map(name => 
                                name === selectedProfile ? selectedColor : profileColors[name] || '#6c757d'
                            );
                            Plotly.restyle(profilesDiv, {'marker.color': [colors]}, [0]);
                            
                            // Actualizar gráficos de ventas y productos
                            updateSalesTrend();
                            updateTopProducts();
                        }
                    }
                };
                
                // Guardar referencia y agregar listener
                graphDiv._clickListener = clickListener;
                graphDiv.addEventListener('click', clickListener);
            }
            
            // Cambiar cursor a pointer en todo el área del gráfico
            const plotArea = profilesDiv.querySelector('.cartesianlayer .plot');
            if (plotArea) {
                plotArea.style.cursor = 'pointer';
            }
            
            // También cambiar cursor en el contenedor SVG
            const svgContainer = profilesDiv.querySelector('.svg-container');
            if (svgContainer) {
                svgContainer.style.cursor = 'pointer';
            }
        }
        
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
                displayModeBar: false,
                staticPlot: false
            }).then(function() {
                // Deshabilitar dragmode para evitar cursor de cruz
                Plotly.relayout(profilesDiv, {
                    'dragmode': false
                });
            });
        }).then(function() {
            // Renderizar el gráfico de tendencia de ventas
            return Plotly.newPlot(salesDiv, salesTrendData.data, salesTrendData.layout, {
                responsive: true,
                displayModeBar: true,  // Mostrar barra de herramientas
                modeBarButtonsToRemove: ['lasso2d', 'select2d'],  // Quitar herramientas innecesarias
                staticPlot: false
            }).then(function() {
                // Mantener dragmode en zoom
                Plotly.relayout(salesDiv, {
                    'dragmode': 'zoom'
                });
            });
        }).then(function() {
            // Renderizar el gráfico de top productos
            return Plotly.newPlot(productsDiv, topProductsData.data, topProductsData.layout, {
                responsive: true,
                displayModeBar: false,
                staticPlot: true
            });
        }).then(function() {
            // Una vez que todos los gráficos se han renderizado, oculta el loader y muestra el contenido
            loader.style.display = 'none';
            contentContainer.style.display = 'grid';
            salesContainer.style.display = 'block';
            
            // Configurar eventos de clic en el gráfico de perfiles
            setupProfileClickEvents();
            
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
                Plotly.react(profilesDiv, customerProfilesData.data, customerProfilesData.layout).then(function() {
                    // Deshabilitar dragmode
                    Plotly.relayout(profilesDiv, {
                        'dragmode': false
                    });
                    // Re-configurar eventos
                    setupProfileClickEvents();
                    
                    // Si había un perfil seleccionado, mantenerlo seleccionado
                    if (selectedProfile) {
                        const currentData = profilesDiv.data[0];
                        if (currentData.x.includes(selectedProfile)) {
                            const colors = currentData.x.map(name => 
                                name === selectedProfile ? selectedColor : profileColors[name] || '#6c757d'
                            );
                            
                            Plotly.restyle(profilesDiv, {
                                'marker.color': [colors]
                            }, [0]);
                        } else {
                            selectedProfile = null;
                        }
                    }
                    
                    // Actualizar gráfico de ventas
                    updateSalesTrend();
                    // Actualizar gráfico de productos
                    updateTopProducts();
                });
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
                        Plotly.react(profilesDiv, newGraphData.data, newGraphData.layout).then(function() {
                            // Deshabilitar dragmode para evitar cursor de cruz
                            Plotly.relayout(profilesDiv, {
                                'dragmode': false
                            });
                            // Re-configurar eventos después de actualizar el gráfico
                            setupProfileClickEvents();
                            
                            // Si había un perfil seleccionado, mantenerlo seleccionado
                            if (selectedProfile) {
                                // Verificar si el perfil existe en los nuevos datos
                                const currentData = profilesDiv.data[0];
                                if (currentData.x.includes(selectedProfile)) {
                                    // Aplicar el color de selección al perfil
                                    const colors = currentData.x.map(name => 
                                        name === selectedProfile ? selectedColor : profileColors[name] || '#6c757d'
                                    );
                                    
                                    Plotly.restyle(profilesDiv, {
                                        'marker.color': [colors]
                                    }, [0]);
                                } else {
                                    // Si el perfil no existe en los nuevos datos, deseleccionarlo
                                    selectedProfile = null;
                                }
                            }
                            
                            // Actualizar gráfico de ventas
                            updateSalesTrend();
                            // Actualizar gráfico de productos
                            updateTopProducts();
                        });
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
