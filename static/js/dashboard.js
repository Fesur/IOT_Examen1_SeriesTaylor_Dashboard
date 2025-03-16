document.addEventListener('DOMContentLoaded', function() {
    // Actualizar la hora de la última actualización
    updateTimestamp();
    
    // Cargar resumen inicial
    loadSummaryData();
    
    // Configurar eventos
    document.getElementById('refresh-btn').addEventListener('click', function() {
        loadSummaryData();
        updateTimestamp();
    });
    
    document.getElementById('toggle-table').addEventListener('click', function() {
        const tableContainer = document.getElementById('data-table-container');
        if (tableContainer.style.display === 'none') {
            tableContainer.style.display = 'block';
            loadTableData();
        } else {
            tableContainer.style.display = 'none';
        }
    });
    
    document.getElementById('user-select').addEventListener('change', function() {
        const username = this.value;
        if (username) {
            document.getElementById('user-content').style.display = 'block';
            document.getElementById('no-user-selected').style.display = 'none';
            loadUserData(username);
        } else {
            document.getElementById('user-content').style.display = 'none';
            document.getElementById('no-user-selected').style.display = 'block';
        }
    });
    
    document.getElementById('series-select').addEventListener('change', function() {
        loadSeriesData(this.value);
    });
    
    // Configurar pestaña de errores
    document.getElementById('errors-tab').addEventListener('click', function() {
        loadErrorAnalysisData();
    });
    
    // Configurar cambio de pestañas
    document.querySelectorAll('button[data-bs-toggle="tab"]').forEach(function(tab) {
        tab.addEventListener('shown.bs.tab', function(e) {
            if (e.target.id === 'users-tab') {
                // Ya tenemos los usuarios cargados del resumen, pero podemos recargar si es necesario
            } else if (e.target.id === 'series-tab') {
                loadSeriesData(document.getElementById('series-select').value);
            } else if (e.target.id === 'errors-tab') {
                loadErrorAnalysisData();
            }
        });
    });
    
    // Iniciar actualizaciones en tiempo real
    startRealTimeUpdates();
});

function updateTimestamp() {
    const now = new Date();
    document.getElementById('update-time').textContent = now.toLocaleString();
}

function showLoading(elementId) {
    const element = document.getElementById(elementId);
    element.innerHTML = `
        <div class="loading">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Cargando...</span>
            </div>
        </div>
    `;
}

function showError(elementId, message) {
    const element = document.getElementById(elementId);
    element.innerHTML = `<div class="error-message">${message}</div>`;
}

function loadSummaryData() {
    showLoading('series-distribution');
    showLoading('error-distribution');
    showLoading('error-vs-terms');
    
    fetch('/api/summary')
        .then(response => {
            if (!response.ok) {
                throw new Error('Error al obtener datos del resumen');
            }
            return response.json();
        })
        .then(data => {
            // Actualizar gráficos
            if (data.graphs && Object.keys(data.graphs).length > 0) {
                Plotly.newPlot('series-distribution', JSON.parse(data.graphs.series_distribution));
                Plotly.newPlot('error-distribution', JSON.parse(data.graphs.error_distribution));
                Plotly.newPlot('error-vs-terms', JSON.parse(data.graphs.error_vs_terms));
                
                // Guardar datos para la tabla
                window.summaryData = data.data;
                
                // Actualizar selector de usuarios
                const userSelect = document.getElementById('user-select');
                userSelect.innerHTML = '';
                
                const defaultOption = document.createElement('option');
                defaultOption.value = '';
                defaultOption.textContent = 'Seleccione un usuario';
                userSelect.appendChild(defaultOption);
                
                data.users.forEach(username => {
                    const option = document.createElement('option');
                    option.value = username;
                    option.textContent = username;
                    userSelect.appendChild(option);
                });
            } else {
                showError('series-distribution', 'No hay datos disponibles');
                showError('error-distribution', 'No hay datos disponibles');
                showError('error-vs-terms', 'No hay datos disponibles');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showError('series-distribution', error.message);
            showError('error-distribution', error.message);
            showError('error-vs-terms', error.message);
        });
}

function loadTableData() {
    const tableBody = document.querySelector('#data-table tbody');
    tableBody.innerHTML = '';
    
    if (window.summaryData && window.summaryData.length > 0) {
        window.summaryData.forEach(row => {
            const tr = document.createElement('tr');
            
            // Formatear valores numéricos
            const formattedRow = {
                username: row.username,
                series_type: row.series_type,
                x_value: row.x_value.toFixed(4),
                n_terms: row.n_terms,
                result: row.result.toExponential(4),
                exact_value: row.exact_value.toExponential(4),
                error: row.error.toExponential(4),
                time: new Date(row.time).toLocaleString()
            };
            
            Object.values(formattedRow).forEach(value => {
                const td = document.createElement('td');
                td.textContent = value;
                tr.appendChild(td);
            });
            
            tableBody.appendChild(tr);
        });
    } else {
        const tr = document.createElement('tr');
        const td = document.createElement('td');
        td.colSpan = 8;
        td.textContent = 'No hay datos disponibles';
        td.className = 'text-center';
        tr.appendChild(td);
        tableBody.appendChild(tr);
    }
}

function loadUserData(username) {
    showLoading('user-error-evolution');
    showLoading('user-results-vs-exact');
    
    fetch(`/api/user_data?username=${encodeURIComponent(username)}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Error al obtener datos del usuario');
            }
            return response.json();
        })
        .then(data => {
            if (data.graphs && Object.keys(data.graphs).length > 0) {
                Plotly.newPlot('user-error-evolution', JSON.parse(data.graphs.error_evolution));
                Plotly.newPlot('user-results-vs-exact', JSON.parse(data.graphs.results_vs_exact));
            } else {
                showError('user-error-evolution', 'No hay datos disponibles para este usuario');
                showError('user-results-vs-exact', 'No hay datos disponibles para este usuario');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showError('user-error-evolution', error.message);
            showError('user-results-vs-exact', error.message);
        });
}

function loadSeriesData(seriesType) {
    showLoading('series-error-vs-terms');
    showLoading('series-function-plot');
    
    fetch(`/api/series_data?type=${encodeURIComponent(seriesType)}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Error al obtener datos de la serie');
            }
            return response.json();
        })
        .then(data => {
            if (data.graphs && Object.keys(data.graphs).length > 0) {
                Plotly.newPlot('series-error-vs-terms', JSON.parse(data.graphs.error_vs_terms));
                Plotly.newPlot('series-function-plot', JSON.parse(data.graphs.function_plot));
            } else {
                showError('series-error-vs-terms', `No hay datos disponibles para la serie ${seriesType}`);
                showError('series-function-plot', `No hay datos disponibles para la serie ${seriesType}`);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showError('series-error-vs-terms', error.message);
            showError('series-function-plot', error.message);
        });
}

function loadErrorAnalysisData() {
    showLoading('error-3d');
    
    // Limpiar contenedor de heatmaps
    const heatmapContainer = document.getElementById('heatmap-container');
    heatmapContainer.innerHTML = '';
    
    fetch('/api/error_analysis')
        .then(response => {
            if (!response.ok) {
                throw new Error('Error al obtener análisis de errores');
            }
            return response.json();
        })
        .then(data => {
            if (data.graphs && Object.keys(data.graphs).length > 0) {
                // Gráfico 3D
                Plotly.newPlot('error-3d', JSON.parse(data.graphs.error_3d));
                
                // Mapas de calor
                if (data.graphs.heatmaps && data.graphs.heatmaps.length > 0) {
                    data.graphs.heatmaps.forEach((heatmapJson, index) => {
                        const seriesType = data.graphs.series_types[index] || `Serie ${index + 1}`;
                        
                        // Crear contenedor para el heatmap
                        const heatmapDiv = document.createElement('div');
                        heatmapDiv.className = 'card mb-4';
                        
                        const cardHeader = document.createElement('div');
                        cardHeader.className = 'card-header';
                        cardHeader.textContent = `Mapa de Calor para ${seriesType}`;
                        
                        const cardBody = document.createElement('div');
                        cardBody.className = 'card-body';
                        
                        const graphDiv = document.createElement('div');
                        graphDiv.id = `heatmap-${seriesType}`;
                        graphDiv.className = 'graph-container';
                        
                        cardBody.appendChild(graphDiv);
                        heatmapDiv.appendChild(cardHeader);
                        heatmapDiv.appendChild(cardBody);
                        heatmapContainer.appendChild(heatmapDiv);
                        
                        // Renderizar el heatmap
                        Plotly.newPlot(`heatmap-${seriesType}`, JSON.parse(heatmapJson));
                    });
                }
            } else {
                showError('error-3d', 'No hay datos disponibles para análisis de errores');
                heatmapContainer.innerHTML = '<div class="error-message">No hay datos disponibles para mapas de calor</div>';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showError('error-3d', error.message);
            heatmapContainer.innerHTML = `<div class="error-message">${error.message}</div>`;
        });
}

// Función para actualizar los datos en tiempo real
function startRealTimeUpdates() {
    let lastId = 0;
    
    // Comprobar nuevos cálculos cada 5 segundos
    setInterval(function() {
        fetch('/api/last_calculation')
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Actualizar solo si hay un nuevo cálculo
                    const calculation = data.calculation;
                    
                    // Añadir al resumen si es un nuevo cálculo y estamos en la pestaña principal
                    if (document.getElementById('overview').classList.contains('active')) {
                        const newRow = {
                            username: calculation.username,
                            series_type: calculation.series_type,
                            x_value: calculation.x_value,
                            n_terms: calculation.n_terms,
                            result: calculation.result,
                            exact_value: calculation.exact_value,
                            error: calculation.error,
                            time: calculation.time
                        };
                        
                        // Verificar si el cálculo ya está en la tabla
                        let found = false;
                        if (window.summaryData) {
                            for (let i = 0; i < window.summaryData.length; i++) {
                                // Comparar los campos clave para identificar duplicados
                                if (window.summaryData[i].username === newRow.username && 
                                    window.summaryData[i].time === newRow.time) {
                                    found = true;
                                    break;
                                }
                            }
                        }
                        
                        // Añadir el nuevo cálculo si no está duplicado
                        if (!found && window.summaryData) {
                            window.summaryData.unshift(newRow);
                            
                            // Actualizar la tabla si está visible
                            if (document.getElementById('data-table-container').style.display !== 'none') {
                                loadTableData();
                            }
                            
                            // Mostrar notificación
                            showNotification(`Nuevo cálculo: ${calculation.series_type}(${calculation.x_value}) por ${calculation.username}`);
                            
                            // Actualizar gráficos si el panel está visible
                            loadSummaryData();
                        }
                    }
                }
            })
            .catch(error => console.error('Error en actualización en tiempo real:', error));
    }, 5000);
}

// Función para mostrar notificaciones
function showNotification(message) {
    // Verificar si ya existe un contenedor de notificaciones
    let notificationContainer = document.getElementById('notification-container');
    
    if (!notificationContainer) {
        notificationContainer = document.createElement('div');
        notificationContainer.id = 'notification-container';
        notificationContainer.style.position = 'fixed';
        notificationContainer.style.bottom = '20px';
        notificationContainer.style.right = '20px';
        notificationContainer.style.zIndex = '9999';
        document.body.appendChild(notificationContainer);
    }
    
    // Crear notificación
    const notification = document.createElement('div');
    notification.className = 'toast show';
    notification.setAttribute('role', 'alert');
    notification.setAttribute('aria-live', 'assertive');
    notification.setAttribute('aria-atomic', 'true');
    
    notification.innerHTML = `
        <div class="toast-header">
            <strong class="me-auto">Nuevo cálculo</strong>
            <small>${new Date().toLocaleTimeString()}</small>
            <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
        <div class="toast-body">
            ${message}
        </div>
    `;
    
    // Añadir notificación al contenedor
    notificationContainer.appendChild(notification);
    
    // Configurar botón de cierre
    notification.querySelector('.btn-close').addEventListener('click', function() {
        notification.remove();
    });
    
    // Auto-cerrar después de 5 segundos
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}
