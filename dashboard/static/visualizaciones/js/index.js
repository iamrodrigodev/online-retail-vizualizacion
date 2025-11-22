document.addEventListener('DOMContentLoaded', function () {
    const loader = document.getElementById('loader');
    const contentContainer = document.getElementById('content-container');
    const salesContainer = document.getElementById('sales-container');
    const productsContainer = document.getElementById('products-container');
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
    // Variables para filtros de productos
    let selectedCategory = null;
    let selectedSubcategory = null;
    
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

    if (mapDiv && profilesDiv && salesDiv && productsDiv && contentContainer && salesContainer &&
        productsContainer && loader && timeFilterContainer &&
        typeof Plotly !== 'undefined' &&
        typeof worldMapData !== 'undefined' &&
        typeof customerProfilesData !== 'undefined' &&
        typeof salesTrendData !== 'undefined' &&
        typeof topProductsData !== 'undefined' &&
        typeof dateRange !== 'undefined') {

        // Función para generar el texto de rango con contexto (debe estar accesible globalmente)
        function generateRangeText(graphType) {
            const startSlider = document.getElementById('timeSliderStart');
            const endSlider = document.getElementById('timeSliderEnd');

            if (!startSlider || !endSlider) return '';

            const startIdx = parseInt(startSlider.value);
            const endIdx = parseInt(endSlider.value);
            const max = parseInt(startSlider.max);

            // Si el rango está en el máximo (todos los datos), no mostrar texto
            if (startIdx === 0 && endIdx === max) {
                return '';
            }

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

        // Inicializar el filtro temporal
        function initializeTimeFilter() {
            if (!dateRange.min || !dateRange.max) {
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
                
                // Actualizar gráfico de similitud si está visible
                if (similarityContainer && similarityContainer.style.display !== 'none') {
                    loadCustomerIds();
                }
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
            // Si hay clientes seleccionados, actualizar con esos clientes
            if (selectedCustomerIds.length > 0) {
                console.log('Manteniendo selección de clientes con nuevos filtros');
                fetchProductsByCustomers(selectedCustomerIds);
                return;
            }

            // Si no hay clientes seleccionados, actualizar normalmente
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
            if (selectedCategory) {
                params.append('category', selectedCategory);
            }
            if (selectedSubcategory) {
                params.append('subcategory', selectedSubcategory);
            }

            if (params.toString()) {
                url += '?' + params.toString();
            }

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
                        // Guardar estado actualizado como el nuevo "original"
                        originalProductsGraph = {
                            data: JSON.parse(JSON.stringify(graphData.data)),
                            layout: JSON.parse(JSON.stringify(graphData.layout))
                        };

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
            }).then(function() {
                // Guardar estado original del gráfico de productos
                originalProductsGraph = {
                    data: JSON.parse(JSON.stringify(topProductsData.data)),
                    layout: JSON.parse(JSON.stringify(topProductsData.layout))
                };
            });
        }).then(function() {
            // Una vez que todos los gráficos se han renderizado, oculta el loader y muestra el contenido
            loader.style.display = 'none';
            contentContainer.style.display = 'grid';
            salesContainer.style.display = 'block';
            productsContainer.style.display = 'block';

            // Forzar resize de gráficos después de mostrarlos (arregla problema de tamaño)
            setTimeout(function() {
                Plotly.Plots.resize(mapDiv);
                Plotly.Plots.resize(profilesDiv);
                Plotly.Plots.resize(salesDiv);
                Plotly.Plots.resize(productsDiv);
                console.log('Gráficos redimensionados correctamente');
            }, 100);

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
                    
                    // Actualizar gráfico de similitud si está visible
                    if (similarityContainer && similarityContainer.style.display !== 'none') {
                        loadCustomerIds();
                    }
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
                            
                            // Actualizar gráfico de similitud si está visible
                            if (similarityContainer && similarityContainer.style.display !== 'none') {
                                loadCustomerIds();
                            }
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
    
    // =============================
    // SIMILITUD DE CLIENTES
    // =============================
    
    const similarityContainer = document.getElementById('client-similarity-container');
    const similarityGraph = document.getElementById('client_similarity_graph');
    const customerSelect = document.getElementById('customerSelect');
    const kNeighbors = document.getElementById('kNeighbors');
    const normalization = document.getElementById('normalization');
    const metric = document.getElementById('metric');
    const dimred = document.getElementById('dimred');
    const applyButton = document.getElementById('applyButton');
    const resetButton = document.getElementById('resetButton');
    const similarityInfo = document.getElementById('similarityInfo');
    const totalCustomersSpan = document.getElementById('totalCustomers');
    
    let currentSimilarityData = null;
    let customerIdsCache = null; // Cache para IDs de clientes
    let isLoadingCustomerIds = false; // Estado de carga
    let similarityGraphCache = {}; // Cache para diferentes configuraciones del gráfico
    let originalProductsGraph = null; // Guardar estado original del gráfico de productos
    let selectedCustomerIds = []; // CustomerIDs actualmente seleccionados
    
    // Valores iniciales por defecto
    const defaultSimilaritySettings = {
        customerId: null,
        k: 10,
        normalization: 'zscore',
        metric: 'euclidean',
        dimred: 'pca',
        xAxisFeature: '',
        yAxisFeature: ''
    };
    
    // Función para cargar los IDs de clientes con cache
    function loadCustomerIds() {
        // Crear clave de caché para IDs (incluir filtros)
        const cacheKey = `${selectedCountry || 'all'}_${selectedStartDate || 'start'}_${selectedEndDate || 'end'}`;
        
        // Si ya están en cache para estos filtros, usarlos directamente
        if (customerIdsCache && customerIdsCache.cacheKey === cacheKey) {
            populateCustomerSelect(customerIdsCache.ids);
            similarityContainer.style.display = 'block';
            updateSimilarityGraph();
            return;
        }
        
        // Si ya está cargando, no hacer otra petición
        if (isLoadingCustomerIds) {
            return;
        }
        
        isLoadingCustomerIds = true;
        
        // NO tocar el selector mientras carga para evitar que se ponga gris
        // Solo actualizarlo cuando tengamos los datos
        
        // Construir URL con parámetros de filtro
        let url = '/api/client-similarity/customer-ids/';
        const params = new URLSearchParams();
        
        if (selectedCountry) {
            params.append('country', selectedCountry);
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
        
        fetch(url)
            .then(response => response.json())
            .then(data => {
                if (data.customer_ids && data.customer_ids.length > 0) {
                    // Guardar en cache con la clave de filtros
                    customerIdsCache = {
                        cacheKey: cacheKey,
                        ids: data.customer_ids
                    };
                    
                    // Poblar el selector
                    populateCustomerSelect(data.customer_ids);
                    
                    // Mostrar el contenedor
                    similarityContainer.style.display = 'block';
                    
                    // Cargar el gráfico inicial
                    updateSimilarityGraph();
                }
            })
            .catch(error => {
                console.error('Error al cargar IDs de clientes:', error);
                customerSelect.innerHTML = '<option value="">Error al cargar clientes</option>';
            })
            .finally(() => {
                isLoadingCustomerIds = false;
            });
    }
    
    // Función auxiliar para poblar el selector con los IDs
    function populateCustomerSelect(customerIds, preserveSelection = true) {
        // Guardar el valor actual antes de limpiar
        const currentValue = preserveSelection ? customerSelect.value : '';
        
        // Limpiar y agregar opción por defecto
        customerSelect.innerHTML = '<option value="">Todos los clientes</option>';
        
        // Agregar opciones sin decimales
        customerIds.forEach(id => {
            const option = document.createElement('option');
            const cleanId = parseInt(id);
            option.value = cleanId;
            option.textContent = `Cliente ${cleanId}`;
            customerSelect.appendChild(option);
        });
        
        // Restaurar el valor anterior si existía y preserveSelection es true
        if (currentValue && preserveSelection) {
            customerSelect.value = currentValue;
        }
    }
    
    // Función para actualizar el rango de fechas del gráfico de similitud
    function updateClientSimilarityDateRange() {
        const clientSimilarityDateRange = document.getElementById('clientSimilarityDateRange');
        if (!clientSimilarityDateRange) return;
        
        // Si no hay filtros de fecha, no mostrar nada
        if (!selectedStartDate || !selectedEndDate) {
            clientSimilarityDateRange.innerHTML = '';
            return;
        }
        
        // Formatear las fechas
        const [startYear, startMonth] = selectedStartDate.split('-');
        const [endYear, endMonth] = selectedEndDate.split('-');
        const monthNames = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 
                           'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
        
        const startMonthName = monthNames[parseInt(startMonth) - 1];
        const endMonthName = monthNames[parseInt(endMonth) - 1];
        
        let rangeText = `Período: ${startMonthName} ${startYear} - ${endMonthName} ${endYear}`;
        
        clientSimilarityDateRange.innerHTML = rangeText;
    }
    
    // Función para actualizar el gráfico de similitud
    function updateSimilarityGraph() {
        const customerId = customerSelect.value || null;
        const k = parseInt(kNeighbors.value);
        const norm = normalization.value;
        const met = metric.value;
        const dim = dimred.value;
        const xAxisFeature = document.getElementById('xAxisFeature').value;
        const yAxisFeature = document.getElementById('yAxisFeature').value;
        
        // Validación
        if (k < 1 || k > 500) {
            alert('K debe estar entre 1 y 500');
            return;
        }
        
        // Crear clave de caché (incluir país y fechas)
        const cacheKey = `${selectedCountry || 'all'}_${selectedStartDate || 'start'}_${selectedEndDate || 'end'}_${customerId || 'all'}_${k}_${norm}_${met}_${dim}_${xAxisFeature}_${yAxisFeature}`;
        
        // Verificar si ya existe en caché
        if (similarityGraphCache[cacheKey]) {
            renderSimilarityGraph(similarityGraphCache[cacheKey], customerId, met, norm);
            updateClientSimilarityDateRange();
            return;
        }
        
        // Mostrar mensaje de carga
        applyButton.disabled = true;
        applyButton.textContent = 'Calculando...';
        
        // Preparar datos para enviar
        const requestData = {
            customer_id: customerId,
            k: k,
            metric: met,
            normalization: norm,
            dimred: dim,
            country: selectedCountry,
            start_date: selectedStartDate,
            end_date: selectedEndDate
        };
        
        // Añadir ejes si están seleccionados
        if (xAxisFeature !== '' && yAxisFeature !== '') {
            requestData.x_axis = parseInt(xAxisFeature);
            requestData.y_axis = parseInt(yAxisFeature);
        }
        
        // Hacer petición POST
        fetch('/api/client-similarity/compute/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(requestData)
        })
        .then(response => {
            if (!response.ok) {
                // Intentar parsear como JSON primero
                return response.text().then(text => {
                    try {
                        const err = JSON.parse(text);
                        throw new Error(err.error || 'Error en el servidor');
                    } catch {
                        // Si no es JSON, es probablemente HTML de error
                        throw new Error(`Error del servidor (${response.status}): El servidor está teniendo problemas. Intenta recargar la página.`);
                    }
                });
            }
            return response.text().then(text => {
                try {
                    return JSON.parse(text);
                } catch (e) {
                    throw new Error('Respuesta inválida del servidor. Recarga la página.');
                }
            });
        })
        .then(data => {
            if (data.error) {
                alert('Error: ' + data.error);
                applyButton.disabled = false;
                applyButton.textContent = 'APLICAR';
                return;
            }
            
            if (!data.embedding || data.embedding.length === 0) {
                alert('No hay datos disponibles para los filtros seleccionados');
                applyButton.disabled = false;
                applyButton.textContent = 'APLICAR';
                return;
            }
            
            currentSimilarityData = data;
            
            // Guardar en caché
            similarityGraphCache[cacheKey] = data;
            
            // Actualizar información
            if (data.total_customers) {
                totalCustomersSpan.textContent = data.total_customers;
                similarityInfo.style.display = 'block';
            }
            
            // Renderizar el gráfico
            renderSimilarityGraph(data, customerId, met, norm);
            
            // Restaurar botón
            applyButton.disabled = false;
            applyButton.textContent = 'APLICAR';
        })
        .catch(error => {
            alert('Error: ' + error.message);
            applyButton.disabled = false;
            applyButton.textContent = 'APLICAR';
        });
    }
    
    // Función para renderizar el gráfico
    function renderSimilarityGraph(data, selectedCustomerId, metricUsed, normalizationUsed) {
        if (!data.embedding || data.embedding.length === 0) {
            similarityGraph.innerHTML = '<p style="text-align: center; padding: 50px;">No hay datos disponibles</p>';
            return;
        }
        
        // Convertir selectedCustomerId a string para comparación consistente
        const selectedIdStr = selectedCustomerId ? String(selectedCustomerId) : null;
        
        // Separar datos por CLUSTER (grupos de comportamiento RFM)
        const clusterGroups = {};
        const clusterTypes = {};  // Para calcular tipo predominante
        
        // Paleta de colores distintivos para CLUSTERS
        const clusterColorPalette = [
            '#e74c3c',  // Rojo vibrante - Cluster 0
            '#3498db',  // Azul brillante - Cluster 1
            '#2ecc71',  // Verde esmeralda - Cluster 2
            '#f39c12',  // Naranja dorado - Cluster 3
            '#9b59b6',  // Púrpura - Cluster 4 (backup)
            '#1abc9c',  // Turquesa - Cluster 5 (backup)
        ];
        
        data.embedding.forEach(point => {
            const clusterId = point.cluster;
            const customerType = point.customer_type;
            
            if (!clusterGroups[clusterId]) {
                clusterGroups[clusterId] = {
                    normal: { x: [], y: [], text: [], ids: [] },
                    outlier: { x: [], y: [], text: [], ids: [] },
                    neighbor: { x: [], y: [], text: [], ids: [] },
                    selected: { x: [], y: [], text: [], ids: [] }
                };
                clusterTypes[clusterId] = [];
            }
            
            clusterTypes[clusterId].push(customerType);
            
            // Tooltip muestra: cluster + tipo individual + métricas RFM
            const text = `<b>Cluster RFM:</b> ${clusterId}<br>` +
                        `<b>Tipo de Cliente:</b> ${customerType}<br>` +
                        `<b>ID:</b> ${point.id}<br>` +
                        `<b>Total gastado:</b> $${point.total_spent.toLocaleString()}<br>` +
                        `<b>Frecuencia:</b> ${point.frequency} compras<br>` +
                        `<b>Productos únicos:</b> ${point.unique_products}<br>` +
                        `<b>País:</b> ${point.country}`;
            
            // Convertir point.id a string para comparación consistente
            const pointIdStr = String(point.id);
            const isSelected = selectedIdStr && pointIdStr === selectedIdStr;
            const isNeighbor = data.neighbors && data.neighbors.some(n => String(n.id) === pointIdStr);
            
            let category;
            if (isSelected) {
                category = 'selected';
            } else if (isNeighbor) {
                category = 'neighbor';
            } else if (point.outlier) {
                category = 'outlier';
            } else {
                category = 'normal';
            }
            
            clusterGroups[clusterId][category].x.push(point.x);
            clusterGroups[clusterId][category].y.push(point.y);
            clusterGroups[clusterId][category].text.push(text);
            clusterGroups[clusterId][category].ids.push(point.id);
        });
        
        // Calcular tipo predominante por cluster (para nombre descriptivo)
        const clusterNames = {};
        Object.keys(clusterTypes).forEach(clusterId => {
            const types = clusterTypes[clusterId];
            const typeCounts = {};
            types.forEach(t => {
                typeCounts[t] = (typeCounts[t] || 0) + 1;
            });
            const predominantType = Object.keys(typeCounts).reduce((a, b) => 
                typeCounts[a] > typeCounts[b] ? a : b
            );
            const total = types.length;
            const percentage = Math.round((typeCounts[predominantType] / total) * 100);
            clusterNames[clusterId] = `Cluster ${clusterId}: ${predominantType} (${percentage}%)`;
        });
        
        // Crear traces de Plotly
        const traces = [];
        
        // Líneas de conexión (dibujar primero)
        if (data.edges && data.edges.length > 0) {
            const coordsDict = {};
            data.embedding.forEach(p => {
                coordsDict[p.id] = { x: p.x, y: p.y };
            });
            
            data.edges.forEach(edge => {
                const source = coordsDict[edge.source];
                const target = coordsDict[edge.target];
                
                if (source && target) {
                    traces.push({
                        x: [source.x, target.x],
                        y: [source.y, target.y],
                        mode: 'lines',
                        line: { color: 'rgba(150, 150, 150, 0.3)', width: 1 },
                        hoverinfo: 'skip',
                        showlegend: false
                    });
                }
            });
        }
        
        // Agregar puntos por CLUSTER (con colores distintivos)
        Object.keys(clusterGroups).forEach(clusterId => {
            const clusterData = clusterGroups[clusterId];
            const color = clusterColorPalette[parseInt(clusterId) % clusterColorPalette.length];
            const clusterName = clusterNames[clusterId] || `Cluster ${clusterId}`;
            
            // Puntos normales
            if (clusterData.normal.x.length > 0) {
                traces.push({
                    x: clusterData.normal.x,
                    y: clusterData.normal.y,
                    mode: 'markers',
                    name: clusterName,
                    marker: {
                        size: 8,
                        color: color,
                        symbol: 'circle',
                        line: { width: 0.5, color: 'white' }
                    },
                    text: clusterData.normal.text,
                    hovertemplate: '%{text}<extra></extra>',
                    customdata: clusterData.normal.ids.map(id => [id]),
                    hoverlabel: { bgcolor: color },
                    hoverinfo: 'text'
                });
            }
            
            // Outliers
            if (clusterData.outlier.x.length > 0) {
                traces.push({
                    x: clusterData.outlier.x,
                    y: clusterData.outlier.y,
                    mode: 'markers',
                    name: `${clusterName} (Atípicos)`,
                    marker: {
                        size: 10,
                        color: color,
                        symbol: 'diamond',
                        line: { width: 1, color: 'black' }
                    },
                    text: clusterData.outlier.text,
                    hovertemplate: '%{text}<extra></extra>',
                    customdata: clusterData.outlier.ids.map(id => [id]),
                    hoverlabel: { bgcolor: color },
                    hoverinfo: 'text'
                });
            }
            
            // Vecinos
            if (clusterData.neighbor.x.length > 0) {
                traces.push({
                    x: clusterData.neighbor.x,
                    y: clusterData.neighbor.y,
                    mode: 'markers',
                    name: `Vecinos - ${clusterName}`,
                    marker: {
                        size: 12,
                        color: color,
                        symbol: 'circle',
                        line: { width: 2, color: 'yellow' }
                    },
                    text: clusterData.neighbor.text,
                    hovertemplate: '%{text}<extra></extra>',
                    customdata: clusterData.neighbor.ids.map(id => [id]),
                    hoverlabel: { bgcolor: color },
                    hoverinfo: 'text'
                });
            }
            
            // Cliente seleccionado
            if (clusterData.selected.x.length > 0) {
                traces.push({
                    x: clusterData.selected.x,
                    y: clusterData.selected.y,
                    mode: 'markers',
                    name: 'Cliente Seleccionado',
                    marker: {
                        size: 16,
                        color: 'red',
                        symbol: 'star',
                        line: { width: 2, color: 'darkred' }
                    },
                    text: clusterData.selected.text,
                    hovertemplate: '%{text}<extra></extra>',
                    customdata: clusterData.selected.ids.map(id => [id]),
                    hoverlabel: { bgcolor: 'red' },
                    hoverinfo: 'text'
                });
            }
        });
        
        // Configurar títulos de ejes
        let xaxisTitle = 'Dimensión 1';
        let yaxisTitle = 'Dimensión 2';
        let titleText = 'Gráfico de Similitud de Clientes - Análisis RFM';
        
        // Verificar si se usan ejes personalizados
        if (data.axis_info && data.axis_info.use_pca === false) {
            // Usar características directas
            const xName = data.axis_info.x_axis_name || 'Eje X';
            const yName = data.axis_info.y_axis_name || 'Eje Y';
            xaxisTitle = xName;
            yaxisTitle = yName;
        } else if (data.pca_variance) {
            // Usar PCA con información de varianza
            const pc1Var = data.pca_variance.pc1_variance.toFixed(1);
            const pc2Var = data.pca_variance.pc2_variance.toFixed(1);
            const pc1Features = data.pca_variance.pc1_features || [];
            const pc2Features = data.pca_variance.pc2_features || [];
            
            // Mostrar solo la característica MÁS IMPORTANTE de cada dimensión
            if (pc1Features.length > 0) {
                xaxisTitle = `${pc1Features[0]} (${pc1Var}%)`;
            } else {
                xaxisTitle = `Dimensión 1 (${pc1Var}%)`;
            }
            
            if (pc2Features.length > 0) {
                yaxisTitle = `${pc2Features[0]} (${pc2Var}%)`;
            } else {
                yaxisTitle = `Dimensión 2 (${pc2Var}%)`;
            }
        }
        
        // Título dinámico basado en filtros (país y fechas)
        const totalCustomers = data.total_customers || data.embedding.length;
        
        // Mapeo de nombres de métricas para mostrar en español
        const metricNames = {
            'euclidean': 'Euclidiana',
            'pearson': 'Pearson',
            'cosine': 'Coseno'
        };
        const metricDisplayName = metricNames[metricUsed] || metricUsed;
        
        // Mapeo de nombres de normalización
        const normalizationNames = {
            'zscore': 'Z-Score',
            'minmax_01': 'Min-Max [0,1]'
        };
        const normalizationDisplayName = normalizationNames[normalizationUsed] || normalizationUsed;
        
        if (selectedCountry) {
            titleText = `${selectedCountry} (${totalCustomers.toLocaleString('es-ES')} clientes)`;
        } else {
            titleText = `Todos los países (${totalCustomers.toLocaleString('es-ES')} clientes)`;
        }
        
        // Agregar métrica y normalización al título si no son las predeterminadas
        const infoItems = [];
        if (metricUsed && metricUsed !== 'euclidean') {
            infoItems.push(`Métrica: ${metricDisplayName}`);
        }
        if (normalizationUsed && normalizationUsed !== 'zscore') {
            infoItems.push(`Normalización: ${normalizationDisplayName}`);
        }
        
        if (infoItems.length > 0) {
            titleText += ` - ${infoItems.join(' | ')}`;
        }
        
        // Layout del gráfico (con zoom habilitado como el mapa mundial)
        const layout = {
            title: {
                text: titleText,
                x: 0.5,
                xanchor: 'center',
                font: { size: 20, color: '#0824a4', family: 'Arial, sans-serif' }
            },
            xaxis: {
                title: xaxisTitle,
                showgrid: true,
                gridcolor: 'rgba(200, 200, 200, 0.2)',
                zeroline: false,
                fixedrange: false  // Habilitar zoom en eje X
            },
            yaxis: {
                title: yaxisTitle,
                showgrid: true,
                gridcolor: 'rgba(200, 200, 200, 0.2)',
                zeroline: false,
                fixedrange: false  // Habilitar zoom en eje Y
            },
            hovermode: 'closest',
            plot_bgcolor: 'rgba(0,0,0,0)',
            paper_bgcolor: 'rgba(0,0,0,0)',
            showlegend: true,
            legend: {
                orientation: 'v',
                yanchor: 'top',
                y: 1,
                xanchor: 'left',
                x: 1.02,
                bgcolor: 'rgba(255, 255, 255, 0.9)',
                bordercolor: '#e0e0e0',
                borderwidth: 1,
                font: { size: 11, color: '#2c3e50' }
            },
            dragmode: 'pan',  // Pan por defecto para navegar. Usa los botones de la barra para lasso/box select
            height: 700,
            margin: { l: 50, r: 200, t: 80, b: 50 }
        };
        
        // Renderizar el gráfico con controles de zoom y selección habilitados
        Plotly.newPlot(similarityGraph, traces, layout, {
            responsive: true,
            displayModeBar: true,
            modeBarButtonsToRemove: [],  // Permitir lasso y select
            scrollZoom: true  // Habilitar zoom con scroll del mouse
        }).then(() => {
            // Forzar cursor pointer en todo el gráfico
            similarityGraph.style.cursor = 'pointer';

            // Agregar cursor pointer a todos los puntos después de renderizar
            const svgLayer = similarityGraph.querySelector('.svg-container');
            if (svgLayer) {
                svgLayer.style.cursor = 'pointer';
            }

            // Forzar cursor en la capa de scatter
            const scatterLayers = similarityGraph.querySelectorAll('.scatterlayer');
            scatterLayers.forEach(layer => {
                layer.style.cursor = 'pointer';
            });

            // Actualizar el subtítulo con el rango de fechas
            updateClientSimilarityDateRange();

            // Configurar eventos de selección de puntos
            setupSimilaritySelectionEvents();
        });
        
        // Agregar evento de clic en puntos para seleccionar cliente
        similarityGraph.on('plotly_click', function(eventData) {
            const point = eventData.points[0];
            
            if (point.customdata && point.customdata.length > 0) {
                const clickedId = point.customdata[0];
                
                // Si el cliente clickeado ya está seleccionado, deseleccionarlo
                if (customerSelect.value === String(clickedId)) {
                    customerSelect.value = '';
                    
                    // Deshabilitar K cuando se deselecciona
                    if (kNeighbors) {
                        kNeighbors.disabled = true;
                        kNeighbors.value = 10;
                        kNeighbors.style.backgroundColor = '#e0e0e0';
                        kNeighbors.style.cursor = 'not-allowed';
                    }
                } else {
                    // Seleccionar nuevo cliente
                    customerSelect.value = clickedId;
                    
                    // Habilitar K si estaba deshabilitado
                    if (kNeighbors && kNeighbors.disabled) {
                        kNeighbors.disabled = false;
                        kNeighbors.style.backgroundColor = '';
                        kNeighbors.style.cursor = '';
                    }
                }
                
                // Actualizar el gráfico
                updateSimilarityGraph();
            }
        });
        
        // Agregar evento hover para cambiar cursor a pointer
        similarityGraph.on('plotly_hover', function(eventData) {
            similarityGraph.style.cursor = 'pointer';
        });
        
        // Restaurar cursor cuando no hay hover
        similarityGraph.on('plotly_unhover', function(eventData) {
            similarityGraph.style.cursor = 'pointer';
        });
    }
    
    // =============================
    // SELECCIÓN DE PUNTOS Y ACTUALIZACIÓN DEL MAPA
    // =============================

    // Función para configurar eventos de selección en el gráfico de similitud
    function setupSimilaritySelectionEvents() {
        // Remover eventos previos para evitar duplicados
        similarityGraph.removeAllListeners('plotly_selected');
        similarityGraph.removeAllListeners('plotly_deselect');

        // Evento cuando el usuario SELECCIONA puntos (lasso o box)
        similarityGraph.on('plotly_selected', function(eventData) {
            if (!eventData || !eventData.points || eventData.points.length === 0) {
                // No hay selección, resetear mapa
                resetMapColors();
                return;
            }

            // 1. Obtener países únicos de los puntos seleccionados
            const selectedCountries = new Set();

            eventData.points.forEach(point => {
                // Buscar el país del punto en los datos actuales
                if (currentSimilarityData && currentSimilarityData.embedding) {
                    const pointData = currentSimilarityData.embedding.find(
                        p => String(p.id) === String(point.customdata[0])
                    );

                    if (pointData && pointData.country) {
                        selectedCountries.add(pointData.country);
                    }
                }
            });

            // 2. Obtener perfiles únicos de los puntos seleccionados
            const selectedProfiles = new Set();

            eventData.points.forEach(point => {
                if (currentSimilarityData && currentSimilarityData.embedding) {
                    const pointData = currentSimilarityData.embedding.find(
                        p => String(p.id) === String(point.customdata[0])
                    );

                    if (pointData && pointData.customer_type) {
                        selectedProfiles.add(pointData.customer_type);
                    }
                }
            });

            // 3. Actualizar mapa con países seleccionados
            if (selectedCountries.size > 0) {
                highlightCountriesInMap(Array.from(selectedCountries));
                console.log(`${eventData.points.length} puntos seleccionados de ${selectedCountries.size} países: ${Array.from(selectedCountries).join(', ')}`);
            }

            // 4. Actualizar gráfico de perfiles con perfiles involucrados
            if (selectedProfiles.size > 0) {
                highlightProfilesInChart(Array.from(selectedProfiles));
                console.log(`Perfiles involucrados: ${Array.from(selectedProfiles).join(', ')}`);
            }

            // 5. Obtener CustomerIDs seleccionados y buscar productos
            selectedCustomerIds = eventData.points.map(point => point.customdata[0]);

            if (selectedCustomerIds.length > 0) {
                fetchProductsByCustomers(selectedCustomerIds);
            }
        });

        // Evento cuando el usuario DESELECCIONA (click en área vacía o doble click)
        similarityGraph.on('plotly_deselect', function() {
            selectedCustomerIds = []; // Limpiar CustomerIDs seleccionados
            resetMapColors();
            resetProfileColors();
            resetProductColors();
            console.log('Selección limpiada, mapa, perfiles y productos reseteados');
        });
    }

    // Función para resaltar países en el mapa (Choropleth usa z y colorscale, no marker.color)
    function highlightCountriesInMap(selectedCountries) {
        // Filtrar el país seleccionado por click (si existe) de la lista general
        const countriesForTrace0 = allCountries.filter(c => c !== selectedCountry);

        // Crear array de valores z para trace 0 (países sin el seleccionado)
        // z=1 para gris, z=2 para naranja
        const zValues = countriesForTrace0.map(country => {
            return selectedCountries.includes(country) ? 2 : 1;
        });

        // Colorscale: [0-1] = gris, [1-2] = naranja
        const colorscale = [
            [0, '#6c757d'],    // Gris para z=1
            [0.5, '#6c757d'],  // Gris hasta z=1
            [0.5, '#FF5722'],  // Naranja desde z=1
            [1, '#FF5722']     // Naranja hasta z=2
        ];

        // Actualizar trace 0 (países generales)
        Plotly.restyle(mapDiv, {
            'z': [zValues],
            'colorscale': [colorscale]
        }, [0]);

        // Si hay un país seleccionado por click, verificar si está en los seleccionados
        if (selectedCountry) {
            // Si el país clickeado está en la selección, pintarlo naranja; si no, mantener azul
            if (selectedCountries.includes(selectedCountry)) {
                Plotly.restyle(mapDiv, {
                    'colorscale': [[[0, '#FF5722'], [1, '#FF5722']]]
                }, [1]);
            } else {
                Plotly.restyle(mapDiv, {
                    'colorscale': [[[0, '#0824a4'], [1, '#0824a4']]]
                }, [1]);
            }
        }
    }

    // Función para resetear colores del mapa (volver a estado según selección de país)
    function resetMapColors() {
        // Filtrar el país seleccionado por click (si existe)
        const countriesForTrace0 = allCountries.filter(c => c !== selectedCountry);

        // Todos los países en gris para trace 0 (z=1)
        const zValues = countriesForTrace0.map(() => 1);
        const colorscale = [[0, '#6c757d'], [1, '#6c757d']];

        Plotly.restyle(mapDiv, {
            'z': [zValues],
            'colorscale': [colorscale]
        }, [0]);

        // Si hay un país seleccionado por click, mantenerlo en azul
        if (selectedCountry) {
            Plotly.restyle(mapDiv, {
                'colorscale': [[[0, '#0824a4'], [1, '#0824a4']]]
            }, [1]);
        }
    }

    // Función para resaltar perfiles en el gráfico de perfiles de clientes
    function highlightProfilesInChart(selectedProfiles) {
        if (!profilesDiv || !profilesDiv.data || !profilesDiv.data[0]) return;

        const currentData = profilesDiv.data[0];
        const profiles = currentData.x;

        // Crear array de colores: naranja para involucrados, color original para el resto
        const colors = profiles.map(profile => {
            if (selectedProfiles.includes(profile)) {
                return '#FF5722'; // Naranja para perfiles involucrados
            } else {
                // Mantener color original del perfil
                return profileColors[profile] || '#6c757d';
            }
        });

        // Actualizar colores de las barras
        Plotly.restyle(profilesDiv, {
            'marker.color': [colors]
        }, [0]);
    }

    // Función para resetear colores del gráfico de perfiles
    function resetProfileColors() {
        if (!profilesDiv || !profilesDiv.data || !profilesDiv.data[0]) return;

        const currentData = profilesDiv.data[0];
        const profiles = currentData.x;

        // Restaurar colores originales
        const colors = profiles.map(profile => {
            // Si hay un perfil seleccionado por click, mantener el color azul La Salle
            if (selectedProfile === profile) {
                return selectedColor; // '#0824a4'
            } else {
                return profileColors[profile] || '#6c757d';
            }
        });

        Plotly.restyle(profilesDiv, {
            'marker.color': [colors]
        }, [0]);
    }

    // Función para obtener y mostrar Top 5 productos de clientes seleccionados
    function fetchProductsByCustomers(customerIds) {
        console.log('fetchProductsByCustomers llamada con', customerIds.length, 'clientes');

        // Obtener filtros actuales de categoría/subcategoría
        const category = selectedCategory || null;
        const subcategory = selectedSubcategory || null;

        // Hacer petición POST al backend
        fetch('/api/products-by-customers/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                customer_ids: customerIds,
                category: category,
                subcategory: subcategory
            })
        })
        .then(response => {
            console.log('Respuesta recibida:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('Datos recibidos:', data);

            if (data.error) {
                console.error('Error al obtener productos:', data.error);
                resetProductColors();
                return;
            }

            if (data.graph) {
                console.log('Reemplazando gráfico de productos...');
                // Reemplazar gráfico completo con Top 5 de clientes seleccionados
                const newGraphData = JSON.parse(data.graph);
                Plotly.react(productsDiv, newGraphData.data, newGraphData.layout, {
                    responsive: true,
                    displayModeBar: false,
                    staticPlot: true
                }).then(() => {
                    console.log('Gráfico de productos actualizado exitosamente');
                });
                console.log(`Top 5 productos de ${data.total_customers} clientes seleccionados`);
            } else {
                console.warn('No se recibió gráfico en la respuesta');
            }
        })
        .catch(error => {
            console.error('Error al obtener productos:', error);
            resetProductColors();
        });
    }

    // Función para resetear el gráfico de productos al estado original
    function resetProductColors() {
        if (!productsDiv || !originalProductsGraph) return;

        // Restaurar gráfico original completo
        Plotly.react(productsDiv, originalProductsGraph.data, originalProductsGraph.layout, {
            responsive: true,
            displayModeBar: false,
            staticPlot: true
        });
    }

    // Función auxiliar para obtener el CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    // Event listeners
    if (applyButton) {
        applyButton.addEventListener('click', updateSimilarityGraph);
    }
    
    // Función para reiniciar todo a valores por defecto
    function resetSimilarityGraph() {
        // Resetear controles a valores por defecto
        customerSelect.value = defaultSimilaritySettings.customerId || '';
        kNeighbors.value = defaultSimilaritySettings.k;
        normalization.value = defaultSimilaritySettings.normalization;
        metric.value = defaultSimilaritySettings.metric;
        dimred.value = defaultSimilaritySettings.dimred;
        document.getElementById('xAxisFeature').value = defaultSimilaritySettings.xAxisFeature;
        document.getElementById('yAxisFeature').value = defaultSimilaritySettings.yAxisFeature;

        // Deshabilitar K
        kNeighbors.disabled = true;
        kNeighbors.style.backgroundColor = '#e0e0e0';
        kNeighbors.style.cursor = 'not-allowed';

        // Limpiar caché para forzar recarga
        similarityGraphCache = {};

        // Limpiar selección de puntos en el gráfico (deseleccionar visualmente)
        if (similarityGraph) {
            Plotly.restyle(similarityGraph, {'selectedpoints': [null]});
        }

        // Limpiar CustomerIDs seleccionados
        selectedCustomerIds = [];

        // Resetear mapa, perfiles y productos
        resetMapColors();
        resetProfileColors();
        resetProductColors();

        // Actualizar gráfico
        updateSimilarityGraph();
    }
    
    // Event listener para botón de reiniciar
    if (resetButton) {
        resetButton.addEventListener('click', resetSimilarityGraph);
    }
    
    // Event listener para bloquear/desbloquear K según cliente seleccionado
    if (customerSelect && kNeighbors) {
        customerSelect.addEventListener('change', function() {
            if (customerSelect.value === '' || customerSelect.value === null) {
                // "Todos los clientes" seleccionado - bloquear K
                kNeighbors.disabled = true;
                kNeighbors.value = 10; // Valor por defecto
                kNeighbors.style.backgroundColor = '#e0e0e0';
                kNeighbors.style.cursor = 'not-allowed';
            } else {
                // Cliente específico seleccionado - habilitar K
                kNeighbors.disabled = false;
                kNeighbors.style.backgroundColor = '';
                kNeighbors.style.cursor = '';
            }
        });
        
        // Ejecutar al cargar para establecer estado inicial
        if (customerSelect.value === '' || customerSelect.value === null) {
            kNeighbors.disabled = true;
            kNeighbors.style.backgroundColor = '#e0e0e0';
            kNeighbors.style.cursor = 'not-allowed';
        }
    }
    
    // Event listeners para los selectores de ejes
    const xAxisFeature = document.getElementById('xAxisFeature');
    const yAxisFeature = document.getElementById('yAxisFeature');
    
    if (xAxisFeature && yAxisFeature) {
        xAxisFeature.addEventListener('change', function() {
            // Solo actualizar si ambos ejes están seleccionados
            if (xAxisFeature.value !== '' && yAxisFeature.value !== '') {
                updateSimilarityGraph();
            }
        });
        
        yAxisFeature.addEventListener('change', function() {
            // Solo actualizar si ambos ejes están seleccionados
            if (xAxisFeature.value !== '' && yAxisFeature.value !== '') {
                updateSimilarityGraph();
            }
        });
    }
    
    // Cargar IDs de clientes al iniciar
    if (similarityContainer) {
        loadCustomerIds();
    }

    // =============================
    // FILTROS DE PRODUCTOS (CATEGORÍA Y SUBCATEGORÍA)
    // =============================

    const categoryFilter = document.getElementById('productCategoryFilter');
    const subcategoryFilter = document.getElementById('productSubcategoryFilter');
    let categoriesData = null;

    // Cargar categorías desde el servidor
    function loadProductCategories() {
        fetch('/api/categories/')
            .then(response => response.json())
            .then(data => {
                categoriesData = data;
                populateCategoryFilter(data.categories);
            })
            .catch(error => {
                console.error('Error al cargar categorías:', error);
            });
    }

    // Poblar selector de categorías
    function populateCategoryFilter(categories) {
        if (!categoryFilter) return;

        categoryFilter.innerHTML = '<option value="">Todas las categorías</option>';
        categories.forEach(category => {
            const option = document.createElement('option');
            option.value = category;
            option.textContent = category;
            categoryFilter.appendChild(option);
        });
    }

    // Manejar cambio en selector de categoría
    if (categoryFilter) {
        categoryFilter.addEventListener('change', function() {
            const category = categoryFilter.value;

            if (category === '') {
                // Sin categoría - deshabilitar subcategorías
                subcategoryFilter.disabled = true;
                subcategoryFilter.innerHTML = '<option value="">Todas las subcategorías</option>';
                selectedCategory = null;
                selectedSubcategory = null;
            } else {
                // Categoría seleccionada - habilitar y poblar subcategorías
                selectedCategory = category;
                selectedSubcategory = null;
                subcategoryFilter.disabled = false;
                subcategoryFilter.innerHTML = '<option value="">Todas las subcategorías</option>';

                if (categoriesData && categoriesData.subcategories_by_category[category]) {
                    categoriesData.subcategories_by_category[category].forEach(subcategory => {
                        const option = document.createElement('option');
                        option.value = subcategory;
                        option.textContent = subcategory;
                        subcategoryFilter.appendChild(option);
                    });
                }
            }

            // Actualizar gráfico
            updateTopProducts();
        });
    }

    // Manejar cambio en selector de subcategoría
    if (subcategoryFilter) {
        subcategoryFilter.addEventListener('change', function() {
            selectedSubcategory = subcategoryFilter.value || null;
            // Actualizar gráfico
            updateTopProducts();
        });
    }

    // Cargar categorías al iniciar
    if (categoryFilter && subcategoryFilter) {
        loadProductCategories();
    }

    // ====================================
    // NAVEGACIÓN FLOTANTE
    // ====================================

    const navButtons = document.querySelectorAll('.nav-btn');

    // Smooth scroll al hacer click en los botones
    navButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetId = this.getAttribute('data-target');

            // Si es el botón "scroll to top"
            if (this.classList.contains('scroll-top')) {
                window.scrollTo({
                    top: 0,
                    behavior: 'smooth'
                });
                return;
            }

            // Para otros botones, scroll al contenedor correspondiente
            const targetElement = document.getElementById(targetId);
            if (targetElement) {
                const offset = 80; // Offset para el navbar
                const elementPosition = targetElement.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - offset;

                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });

    // Scroll spy: resaltar botón activo según sección visible
    function updateActiveNavButton() {
        const scrollPosition = window.scrollY + 150;

        // Array de secciones en orden
        const sections = [
            'worldMap',
            'customerProfiles',
            'sales-container',
            'products-container',
            'client-similarity-container'
        ];

        let activeSection = null;

        // Encontrar qué sección está visible
        sections.forEach(sectionId => {
            const section = document.getElementById(sectionId);
            if (section) {
                const sectionTop = section.offsetTop;
                const sectionBottom = sectionTop + section.offsetHeight;

                if (scrollPosition >= sectionTop && scrollPosition < sectionBottom) {
                    activeSection = sectionId;
                }
            }
        });

        // Actualizar clase active en botones
        navButtons.forEach(button => {
            const targetId = button.getAttribute('data-target');
            if (targetId === activeSection) {
                button.classList.add('active');
            } else {
                button.classList.remove('active');
            }
        });
    }

    // Ejecutar scroll spy al hacer scroll
    window.addEventListener('scroll', updateActiveNavButton);

    // Ejecutar al cargar
    updateActiveNavButton();
});
