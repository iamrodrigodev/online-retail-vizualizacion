document.addEventListener('DOMContentLoaded', function () {
    const loader = document.getElementById('loader');
    const contentContainer = document.getElementById('content-container');
    const salesContainer = document.getElementById('sales-container');
    const timeFilterContainer = document.getElementById('time-filter-container');
    const mapDiv = document.getElementById('worldMap');
    const profilesDiv = document.getElementById('customerProfiles');
    const salesDiv = document.getElementById('salesTrend');
    const productsDiv = document.getElementById('topProducts');
    
    // Variable para almacenar el país seleccionado
    let selectedCountry = null;
    // Variable para almacenar el perfil seleccionado
    let selectedProfile = null;
    // Variables para el filtro temporal
    let selectedStartDate = null;
    let selectedEndDate = null;
    let allMonths = [];
    
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
        timeFilterContainer &&
        typeof Plotly !== 'undefined' && 
        typeof worldMapData !== 'undefined' && 
        typeof customerProfilesData !== 'undefined' &&
        typeof salesTrendData !== 'undefined' &&
        typeof topProductsData !== 'undefined' &&
        typeof dateRange !== 'undefined') {
        
        // Inicializar el filtro temporal
        function initializeTimeFilter() {
            if (!dateRange.min || !dateRange.max) {
                console.log('No hay rango de fechas disponible');
                return;
            }
            
            // Generar array de meses entre min y max
            const [minYear, minMonth] = dateRange.min.split('-').map(Number);
            const [maxYear, maxMonth] = dateRange.max.split('-').map(Number);
            
            allMonths = [];
            for (let year = minYear; year <= maxYear; year++) {
                const startMonth = (year === minYear) ? minMonth : 1;
                const endMonth = (year === maxYear) ? maxMonth : 12;
                
                for (let month = startMonth; month <= endMonth; month++) {
                    const monthStr = month.toString().padStart(2, '0');
                    allMonths.push(`${year}-${monthStr}`);
                }
            }
            
            // Configurar los sliders
            const startSlider = document.getElementById('timeSliderStart');
            const endSlider = document.getElementById('timeSliderEnd');
            const startLabel = document.getElementById('startDateLabel');
            const endLabel = document.getElementById('endDateLabel');
            const rangeDisplay = document.getElementById('timeRangeDisplay');
            const descriptionText = document.getElementById('timeFilterDescription');
            const sliderWrapper = document.querySelector('.time-slider-wrapper');
            const ticksContainer = document.getElementById('timeSliderTicks');
            
            // Referencias a los textos de rango de fechas de cada gráfico
            const customerProfilesDateRange = document.getElementById('customerProfilesDateRange');
            const salesTrendDateRange = document.getElementById('salesTrendDateRange');
            const topProductsDateRange = document.getElementById('topProductsDateRange');
            
            if (!startSlider || !endSlider) return;
            
            startSlider.max = allMonths.length - 1;
            endSlider.max = allMonths.length - 1;
            startSlider.value = 0;
            endSlider.value = allMonths.length - 1;
            
            // Inicializar fechas seleccionadas (rango completo)
            selectedStartDate = null;
            selectedEndDate = null;
            
            // Generar marcadores de meses
            function generateTicks() {
                ticksContainer.innerHTML = '';
                const totalMonths = allMonths.length;
                
                if (totalMonths <= 1) return;
                
                // Paso para las etiquetas (solo mostrar algunas)
                const labelStep = Math.ceil(totalMonths / 8);
                
                // Generar un tick para cada mes
                for (let i = 0; i < totalMonths; i++) {
                    const month = allMonths[i];
                    const [year, monthNum] = month.split('-');
                    
                    const tickContainer = document.createElement('div');
                    tickContainer.className = 'time-slider-tick-container';
                    
                    // Calcular posición exacta basada en el índice
                    const position = (i / (totalMonths - 1)) * 100;
                    tickContainer.style.left = `${position}%`;
                    
                    // No necesitamos ajustar el transform, el CSS ya los centra con translateX(-50%)
                    
                    const tick = document.createElement('div');
                    
                    // Determinar si debe mostrar etiqueta (cada labelStep meses o si es el último)
                    const shouldShowLabel = (i % labelStep === 0) || (i === totalMonths - 1);
                    
                    if (shouldShowLabel) {
                        tick.className = 'time-slider-tick major';
                        
                        const label = document.createElement('span');
                        label.className = 'time-slider-tick-label';
                        
                        const monthNames = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 
                                           'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];
                        label.textContent = `${monthNames[parseInt(monthNum) - 1]} ${year}`;
                        
                        tickContainer.appendChild(tick);
                        tickContainer.appendChild(label);
                    } else {
                        tick.className = 'time-slider-tick minor';
                        tickContainer.appendChild(tick);
                    }
                    
                    ticksContainer.appendChild(tickContainer);
                }
            }
            
            generateTicks();
            
            // Función para actualizar la barra de progreso visual
            function updateProgressBar() {
                const startIdx = parseInt(startSlider.value);
                const endIdx = parseInt(endSlider.value);
                const max = parseInt(startSlider.max);
                
                const startPercent = (startIdx / max) * 100;
                const endPercent = (endIdx / max) * 100;
                
                sliderWrapper.style.setProperty('--start-percent', startPercent + '%');
                sliderWrapper.style.setProperty('--end-percent', (100 - endPercent) + '%');
            }
            
            // Función para formatear fecha para mostrar
            function formatDateDisplay(dateStr) {
                const [year, month] = dateStr.split('-');
                const monthNames = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 
                                   'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
                return `${monthNames[parseInt(month) - 1]} ${year}`;
            }
            
            // Función para generar el texto de rango con contexto
            function generateRangeText(graphType) {
                const startIdx = parseInt(startSlider.value);
                const endIdx = parseInt(endSlider.value);
                const [startYear, startMonth] = allMonths[startIdx].split('-');
                const [endYear, endMonth] = allMonths[endIdx].split('-');
                const monthNames = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 
                                   'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
                
                const startMonthName = monthNames[parseInt(startMonth) - 1];
                const endMonthName = monthNames[parseInt(endMonth) - 1];
                
                let prefix = '';
                if (graphType === 'sales') {
                    prefix = 'Ventas';
                } else if (graphType === 'products') {
                    prefix = 'Productos';
                } else if (graphType === 'profiles') {
                    prefix = 'Perfiles de Cliente';
                }
                
                // Agregar información de país si está seleccionado
                if (selectedCountry) {
                    prefix += ` en ${selectedCountry}`;
                }
                
                // Agregar información de perfil si está seleccionado
                if (selectedProfile && (graphType === 'sales' || graphType === 'products')) {
                    prefix += ` con perfil ${selectedProfile}`;
                }
                
                return `${prefix} desde ${startMonthName} del ${startYear} <strong>hasta</strong> ${endMonthName} del ${endYear}`;
            }
            
            // Función para actualizar etiquetas
            function updateLabels() {
                const startIdx = parseInt(startSlider.value);
                const endIdx = parseInt(endSlider.value);
                
                startLabel.textContent = `Desde: ${formatDateDisplay(allMonths[startIdx])}`;
                endLabel.textContent = `Hasta: ${formatDateDisplay(allMonths[endIdx])}`;
                rangeDisplay.textContent = `${formatDateDisplay(allMonths[startIdx])} - ${formatDateDisplay(allMonths[endIdx])}`;
                
                // Actualizar el texto descriptivo con "hasta" en negritas
                if (descriptionText) {
                    const [startYear, startMonth] = allMonths[startIdx].split('-');
                    const [endYear, endMonth] = allMonths[endIdx].split('-');
                    const monthNames = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 
                                       'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
                    
                    const startMonthName = monthNames[parseInt(startMonth) - 1];
                    const endMonthName = monthNames[parseInt(endMonth) - 1];
                    
                    descriptionText.innerHTML = `Desde ${startMonthName} del ${startYear} <strong>hasta</strong> ${endMonthName} del ${endYear}`;
                }
                
                // Actualizar los textos de rango de fecha de cada gráfico
                if (customerProfilesDateRange) {
                    customerProfilesDateRange.innerHTML = generateRangeText('profiles');
                }
                if (salesTrendDateRange) {
                    salesTrendDateRange.innerHTML = generateRangeText('sales');
                }
                if (topProductsDateRange) {
                    topProductsDateRange.innerHTML = generateRangeText('products');
                }
                
                updateProgressBar();
            }
            
            // Función para actualizar gráficos con filtro temporal
            function updateChartsWithTimeFilter() {
                const startIdx = parseInt(startSlider.value);
                const endIdx = parseInt(endSlider.value);
                
                // Si el rango es completo, no aplicar filtro de fechas
                if (startIdx === 0 && endIdx === allMonths.length - 1) {
                    selectedStartDate = null;
                    selectedEndDate = null;
                } else {
                    selectedStartDate = allMonths[startIdx];
                    selectedEndDate = allMonths[endIdx];
                }
                
                updateLabels();
                
                // Actualizar los tres gráficos que deben responder al filtro temporal
                updateSalesTrend();
                updateTopProducts();
                updateCustomerProfiles();
            }
            
            // Event listeners para los sliders
            let updateTimeout;
            
            startSlider.addEventListener('input', function() {
                const startIdx = parseInt(startSlider.value);
                const endIdx = parseInt(endSlider.value);
                
                // Asegurar que start no supere a end
                if (startIdx > endIdx) {
                    startSlider.value = endIdx;
                }
                
                updateLabels();
                
                // Debounce para no hacer muchas peticiones
                clearTimeout(updateTimeout);
                updateTimeout = setTimeout(updateChartsWithTimeFilter, 300);
            });
            
            endSlider.addEventListener('input', function() {
                const startIdx = parseInt(startSlider.value);
                const endIdx = parseInt(endSlider.value);
                
                // Asegurar que end no sea menor que start
                if (endIdx < startIdx) {
                    endSlider.value = startIdx;
                }
                
                updateLabels();
                
                // Debounce para no hacer muchas peticiones
                clearTimeout(updateTimeout);
                updateTimeout = setTimeout(updateChartsWithTimeFilter, 300);
            });
            
            // Hacer el slider clickeable
            sliderWrapper.addEventListener('click', function(event) {
                // Obtener las dimensiones del wrapper
                const rect = sliderWrapper.getBoundingClientRect();
                const clickX = event.clientX - rect.left;
                
                // Calcular el porcentaje de la posición del click (considerando el padding de 10px)
                const padding = 10;
                const availableWidth = rect.width - (padding * 2);
                const adjustedClickX = clickX - padding;
                
                // Asegurar que el click esté dentro del área válida
                if (adjustedClickX < 0 || adjustedClickX > availableWidth) return;
                
                const percentage = adjustedClickX / availableWidth;
                const clickedIndex = Math.round(percentage * (allMonths.length - 1));
                
                // Determinar cuál slider mover (el más cercano al click)
                const startIdx = parseInt(startSlider.value);
                const endIdx = parseInt(endSlider.value);
                const startPos = (startIdx / (allMonths.length - 1)) * availableWidth + padding;
                const endPos = (endIdx / (allMonths.length - 1)) * availableWidth + padding;
                
                const distanceToStart = Math.abs(clickX - startPos);
                const distanceToEnd = Math.abs(clickX - endPos);
                
                if (distanceToStart < distanceToEnd) {
                    // Mover el slider de inicio
                    if (clickedIndex <= endIdx) {
                        startSlider.value = clickedIndex;
                    }
                } else {
                    // Mover el slider de fin
                    if (clickedIndex >= startIdx) {
                        endSlider.value = clickedIndex;
                    }
                }
                
                updateLabels();
                updateChartsWithTimeFilter();
            });
            
            // Inicializar etiquetas
            updateLabels();
            
            // Mostrar el contenedor del filtro
            timeFilterContainer.style.display = 'block';
        }
        
        // Función para actualizar el gráfico de perfiles de cliente
        function updateCustomerProfiles() {
            if (!selectedCountry) {
                // Si no hay país seleccionado, solo aplicar filtro de fechas si existe
                if (!selectedStartDate && !selectedEndDate) {
                    // Rango completo, usar datos iniciales
                    Plotly.react(profilesDiv, customerProfilesData.data, customerProfilesData.layout).then(function() {
                        Plotly.relayout(profilesDiv, { 'dragmode': false });
                        setupProfileClickEvents();
                        
                        if (selectedProfile) {
                            const currentData = profilesDiv.data[0];
                            if (currentData.x.includes(selectedProfile)) {
                                const colors = currentData.x.map(name => 
                                    name === selectedProfile ? selectedColor : profileColors[name] || '#6c757d'
                                );
                                Plotly.restyle(profilesDiv, { 'marker.color': [colors] }, [0]);
                            } else {
                                selectedProfile = null;
                            }
                        }
                        
                        // Actualizar el texto de rango de fecha
                        if (customerProfilesDateRange) {
                            customerProfilesDateRange.innerHTML = generateRangeText('profiles');
                        }
                    });
                } else {
                    // Aplicar filtro de fechas
                    let url = '/api/customer-profiles-global/';
                    const params = new URLSearchParams();
                    
                    if (selectedStartDate) params.append('start_date', selectedStartDate);
                    if (selectedEndDate) params.append('end_date', selectedEndDate);
                    
                    if (params.toString()) url += '?' + params.toString();
                    
                    fetch(url)
                        .then(response => response.json())
                        .then(data => {
                            const newGraphData = JSON.parse(data.graph);
                            Plotly.react(profilesDiv, newGraphData.data, newGraphData.layout).then(function() {
                                Plotly.relayout(profilesDiv, { 'dragmode': false });
                                setupProfileClickEvents();
                                
                                if (selectedProfile) {
                                    const currentData = profilesDiv.data[0];
                                    if (currentData.x.includes(selectedProfile)) {
                                        const colors = currentData.x.map(name => 
                                            name === selectedProfile ? selectedColor : profileColors[name] || '#6c757d'
                                        );
                                        Plotly.restyle(profilesDiv, { 'marker.color': [colors] }, [0]);
                                    } else {
                                        selectedProfile = null;
                                    }
                                }
                                
                                // Actualizar el texto de rango de fecha
                                if (customerProfilesDateRange) {
                                    customerProfilesDateRange.innerHTML = generateRangeText('profiles');
                                }
                            });
                        })
                        .catch(error => console.error('Error:', error));
                }
            } else {
                // Ya hay lógica para país seleccionado, solo añadir filtro de fechas
                // Esta parte se manejará en la función existente de actualización por país
            }
        }
        
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
            if (selectedStartDate) {
                params.append('start_date', selectedStartDate);
            }
            if (selectedEndDate) {
                params.append('end_date', selectedEndDate);
            }
            
            if (params.toString()) {
                url += '?' + params.toString();
            }
            
            console.log('Actualizando ventas con:', { 
                country: selectedCountry, 
                profile: selectedProfile, 
                startDate: selectedStartDate,
                endDate: selectedEndDate,
                url: url 
            });
            
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
                        
                        // Actualizar el texto de rango de fecha
                        if (salesTrendDateRange) {
                            salesTrendDateRange.innerHTML = generateRangeText('sales');
                        }
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
            if (selectedStartDate) {
                params.append('start_date', selectedStartDate);
            }
            if (selectedEndDate) {
                params.append('end_date', selectedEndDate);
            }
            
            if (params.toString()) {
                url += '?' + params.toString();
            }
            
            console.log('Actualizando productos con:', { 
                country: selectedCountry, 
                profile: selectedProfile,
                startDate: selectedStartDate,
                endDate: selectedEndDate,
                url: url 
            });
            
            // Hacer petición al servidor
            fetch(url)
                .then(response => response.json())
                .then(data => {
                    const graphData = JSON.parse(data.graph);
                    
                    Plotly.react(productsDiv, graphData.data, graphData.layout, {
                        responsive: true,
                        displayModeBar: false,
                        staticPlot: true
                    }).then(function() {
                        // Actualizar el texto de rango de fecha
                        if (topProductsDateRange) {
                            topProductsDateRange.innerHTML = generateRangeText('products');
                        }
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
            
            // Inicializar el filtro temporal
            initializeTimeFilter();
            
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
                    
                    // Si hay filtro temporal, actualizar con él
                    if (selectedStartDate || selectedEndDate) {
                        updateCustomerProfiles();
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
                let profileUrl = `/api/customer-profiles/${encodeURIComponent(countryName)}/`;
                const profileParams = new URLSearchParams();
                
                if (selectedStartDate) profileParams.append('start_date', selectedStartDate);
                if (selectedEndDate) profileParams.append('end_date', selectedEndDate);
                
                if (profileParams.toString()) profileUrl += '?' + profileParams.toString();
                
                fetch(profileUrl)
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
