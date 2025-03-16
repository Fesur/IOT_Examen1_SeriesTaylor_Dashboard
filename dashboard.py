from flask import Flask, render_template, jsonify, request, redirect, url_for
import plotly
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
import math
import numpy as np
from database import Database
from series_calculator import SeriesCalculator
from datetime import datetime
import os
import socket
import threading

app = Flask(__name__)
app.config['SECRET_KEY'] = 'series_trigonometricas_dashboard'

# Asegurarse de que el directorio de templates existe
os.makedirs('templates', exist_ok=True)
os.makedirs(os.path.join('static', 'js'), exist_ok=True)
os.makedirs(os.path.join('static', 'css'), exist_ok=True)

# Conexión a la base de datos
db = Database()

# Variable global para almacenar el ID del último cálculo
last_calculation_id = 0

@app.route('/')
def home():
    """Página principal de la aplicación."""
    return render_template('calculator.html')

@app.route('/dashboard')
def index():
    """Página del dashboard."""
    return render_template('index.html')

@app.route('/api/calculate', methods=['POST'])
def calculate():
    """API para calcular series directamente desde la web."""
    data = request.json
    
    if not data:
        return jsonify({'status': 'error', 'message': 'No se proporcionaron datos'})
    
    required_fields = ['username', 'series_type', 'x_value', 'n_terms']
    if not all(field in data for field in required_fields):
        return jsonify({'status': 'error', 'message': 'Faltan campos requeridos'})
    
    username = data['username']
    series_type = data['series_type']
    x_value = data['x_value']
    n_terms = data['n_terms']
    
    # Validaciones
    if series_type not in ['sin', 'cos', 'tan']:
        return jsonify({'status': 'error', 'message': f'Tipo de serie no soportado: {series_type}'})
    
    if n_terms <= 0:
        return jsonify({'status': 'error', 'message': 'El número de términos debe ser positivo'})
    
    try:
        # Registrar usuario
        user_id = db.add_user(username)
        
        # Calcular serie
        result, exact_value, error = SeriesCalculator.calculate_series(series_type, x_value, n_terms)
        
        # Guardar cálculo en la base de datos
        calculation_id = db.save_calculation(user_id, series_type, x_value, n_terms, result, exact_value, error)
        
        global last_calculation_id
        last_calculation_id = calculation_id
        
        return jsonify({
            'status': 'success',
            'calculation_id': calculation_id,
            'result': result,
            'exact_value': exact_value,
            'error': error
        })
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/user_history')
def user_history():
    """API para obtener el historial de cálculos de un usuario por nombre."""
    username = request.args.get('username', '')
    
    if not username:
        return jsonify({'status': 'error', 'message': 'Nombre de usuario no proporcionado'})
    
    try:
        # Obtener ID del usuario
        cursor = db.conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        
        if not result:
            return jsonify({'status': 'error', 'message': 'Usuario no encontrado'})
        
        user_id = result[0]
        
        # Obtener cálculos del usuario
        calculations = db.get_user_calculations(user_id)
        
        return jsonify({
            'status': 'success',
            'username': username,
            'calculations': calculations
        })
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/summary')
def get_summary():
    """API para obtener el resumen de cálculos."""
    calculations = db.get_all_calculations()
    
    # Convertir los datos a un formato adecuado para pandas
    data = []
    for calc in calculations:
        username, series_type, x_value, n_terms, result, exact_value, error, time = calc
        data.append({
            'username': username,
            'series_type': series_type,
            'x_value': x_value,
            'n_terms': n_terms,
            'result': result,
            'exact_value': exact_value,
            'error': error,
            'time': time
        })
    
    # Crear gráfico de distribución de series
    df = pd.DataFrame(data)
    
    if not df.empty:
        # Gráfico de barras para tipos de serie
        series_counts = df['series_type'].value_counts().reset_index()
        series_counts.columns = ['series_type', 'count']
        
        fig1 = px.bar(
            series_counts, 
            x='series_type', 
            y='count', 
            title='Distribución de Cálculos por Tipo de Serie',
            labels={'series_type': 'Tipo de Serie', 'count': 'Cantidad de Cálculos'},
            color='series_type'
        )
        
        # Gráfico de caja para errores por tipo de serie
        fig2 = px.box(
            df, 
            x='series_type', 
            y='error',
            title='Distribución de Errores por Tipo de Serie',
            labels={'series_type': 'Tipo de Serie', 'error': 'Error'},
            color='series_type'
        )
        
        # Gráfico de dispersión para error vs. términos
        fig3 = px.scatter(
            df,
            x='n_terms',
            y='error',
            color='series_type',
            title='Error vs. Número de Términos',
            labels={'n_terms': 'Número de Términos', 'error': 'Error'},
            hover_data=['username', 'x_value', 'result']
        )
        
        # Convertir a JSON
        graph1_json = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)
        graph2_json = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
        graph3_json = json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)
        
        return jsonify({
            'data': data,
            'graphs': {
                'series_distribution': graph1_json,
                'error_distribution': graph2_json,
                'error_vs_terms': graph3_json
            },
            'users': df['username'].unique().tolist(),
            'series_types': df['series_type'].unique().tolist()
        })
    
    return jsonify({'data': [], 'graphs': {}, 'users': [], 'series_types': []})

@app.route('/api/user_data')
def get_user_data():
    """API para obtener datos de un usuario específico."""
    username = request.args.get('username', '')
    
    # Obtener todos los cálculos
    all_calcs = db.get_all_calculations()
    
    # Filtrar por usuario
    user_calcs = [calc for calc in all_calcs if calc[0] == username]
    
    # Convertir a formato para pandas
    data = []
    for calc in user_calcs:
        username, series_type, x_value, n_terms, result, exact_value, error, time = calc
        data.append({
            'username': username,
            'series_type': series_type,
            'x_value': x_value,
            'n_terms': n_terms,
            'result': result,
            'exact_value': exact_value,
            'error': error,
            'time': time
        })
    
    df = pd.DataFrame(data)
    
    if not df.empty:
        # Gráfico de línea de errores vs tiempo
        df['time'] = pd.to_datetime(df['time'])
        df = df.sort_values('time')
        
        fig1 = px.line(
            df,
            x='time',
            y='error',
            color='series_type',
            title=f'Evolución de errores para {username}',
            labels={'time': 'Tiempo', 'error': 'Error'},
            hover_data=['x_value', 'n_terms', 'result']
        )
        
        # Gráfico de dispersión de resultados vs valores exactos
        fig2 = px.scatter(
            df,
            x='exact_value',
            y='result',
            color='series_type',
            title=f'Resultados vs Valores Exactos para {username}',
            labels={'exact_value': 'Valor Exacto', 'result': 'Resultado Calculado'},
            hover_data=['x_value', 'n_terms', 'error']
        )
        
        # Añadir línea y=x para referencia
        min_val = min(df['exact_value'].min(), df['result'].min())
        max_val = max(df['exact_value'].max(), df['result'].max())
        fig2.add_trace(go.Scatter(
            x=[min_val, max_val],
            y=[min_val, max_val],
            mode='lines',
            name='Valor Exacto',
            line=dict(color='black', dash='dash')
        ))
        
        # Convertir a JSON
        graph1_json = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)
        graph2_json = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
        
        return jsonify({
            'data': data,
            'graphs': {
                'error_evolution': graph1_json,
                'results_vs_exact': graph2_json
            }
        })
    
    return jsonify({'data': [], 'graphs': {}})

@app.route('/api/series_data')
def get_series_data():
    """API para obtener datos de un tipo específico de serie."""
    series_type = request.args.get('type', 'sin')
    
    # Obtener todos los cálculos
    all_calcs = db.get_all_calculations()
    
    # Filtrar por tipo de serie
    series_calcs = [calc for calc in all_calcs if calc[1] == series_type]
    
    # Convertir a formato para pandas
    data = []
    for calc in series_calcs:
        username, _, x_value, n_terms, result, exact_value, error, time = calc
        data.append({
            'username': username,
            'x_value': x_value,
            'n_terms': n_terms,
            'result': result,
            'exact_value': exact_value,
            'error': error,
            'time': time
        })
    
    df = pd.DataFrame(data)
    
    if not df.empty:
        # Gráfico de dispersión de error vs n_terms
        fig1 = px.scatter(
            df,
            x='n_terms',
            y='error',
            color='username',
            title=f'Error vs Número de Términos para {series_type}',
            labels={'n_terms': 'Número de Términos', 'error': 'Error'},
            hover_data=['x_value', 'result', 'exact_value']
        )
        
        # Gráficas de las funciones
        x_range = np.linspace(-2*math.pi, 2*math.pi, 1000)
        
        if series_type == 'sin':
            y_exact = np.sin(x_range)
            title = 'Función seno'
        elif series_type == 'cos':
            y_exact = np.cos(x_range)
            title = 'Función coseno'
        elif series_type == 'tan':
            # Evitar discontinuidades en tangente
            mask = np.abs(np.cos(x_range)) > 0.1
            x_range_tan = x_range[mask]
            y_exact = np.tan(x_range_tan)
            x_range = x_range_tan
            title = 'Función tangente'
        
        # Crear figura para la función exacta
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=x_range,
            y=y_exact,
            mode='lines',
            name='Función Exacta'
        ))
        
        # Agregar puntos calculados
        fig2.add_trace(go.Scatter(
            x=df['x_value'],
            y=df['result'],
            mode='markers',
            name='Aproximaciones',
            marker=dict(
                size=10,
                color=df['error'],
                colorscale='Viridis',
                colorbar=dict(title='Error'),
                showscale=True
            ),
            text=[f"Usuario: {u}<br>Términos: {n}<br>Error: {e:.2e}" 
                 for u, n, e in zip(df['username'], df['n_terms'], df['error'])],
            hoverinfo='text'
        ))
        
        fig2.update_layout(
            title=title,
            xaxis_title='x',
            yaxis_title=f'{series_type}(x)'
        )
        
        # Convertir a JSON
        graph1_json = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)
        graph2_json = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
        
        return jsonify({
            'data': data,
            'graphs': {
                'error_vs_terms': graph1_json,
                'function_plot': graph2_json
            }
        })
    
    return jsonify({'data': [], 'graphs': {}})

@app.route('/api/error_analysis')
def error_analysis():
    """API para análisis detallado de errores."""
    # Obtener todos los cálculos
    all_calcs = db.get_all_calculations()
    
    # Convertir a formato para pandas
    data = []
    for calc in all_calcs:
        username, series_type, x_value, n_terms, result, exact_value, error, time = calc
        data.append({
            'username': username,
            'series_type': series_type,
            'x_value': x_value,
            'n_terms': n_terms,
            'result': result,
            'exact_value': exact_value,
            'error': error,
            'time': time,
            'error_rel': error / abs(exact_value) if abs(exact_value) > 1e-10 else float('inf')
        })
    
    df = pd.DataFrame(data)
    
    if not df.empty:
        # Gráfico 3D de error vs x_value vs n_terms
        fig1 = go.Figure(data=[
            go.Scatter3d(
                x=df[df['series_type'] == st]['x_value'],
                y=df[df['series_type'] == st]['n_terms'],
                z=df[df['series_type'] == st]['error'],
                mode='markers',
                name=st,
                marker=dict(
                    size=5,
                    opacity=0.8
                ),
                text=[f"Usuario: {u}<br>Error: {e:.2e}" 
                     for u, e in zip(df[df['series_type'] == st]['username'], 
                                     df[df['series_type'] == st]['error'])],
                hoverinfo='text'
            ) for st in df['series_type'].unique()
        ])
        
        fig1.update_layout(
            title='Análisis 3D de Errores',
            scene=dict(
                xaxis_title='Valor de x',
                yaxis_title='Número de Términos',
                zaxis_title='Error'
            )
        )
        
        # Heatmap de error para cada tipo de serie
        heatmap_data = []
        
        for st in df['series_type'].unique():
            st_df = df[df['series_type'] == st]
            
            # Crear bins para x_value y n_terms
            x_bins = np.linspace(st_df['x_value'].min(), st_df['x_value'].max(), 20)
            n_bins = np.unique(st_df['n_terms'])
            
            # Matriz para el heatmap
            z_matrix = np.zeros((len(n_bins), len(x_bins)-1))
            
            # Llenar la matriz con los errores promedio
            for i, n in enumerate(n_bins):
                for j in range(len(x_bins)-1):
                    mask = (st_df['n_terms'] == n) & (st_df['x_value'] >= x_bins[j]) & (st_df['x_value'] < x_bins[j+1])
                    if mask.any():
                        z_matrix[i, j] = st_df.loc[mask, 'error'].mean()
            
            heatmap = go.Heatmap(
                z=z_matrix,
                x=[(x_bins[i] + x_bins[i+1])/2 for i in range(len(x_bins)-1)],
                y=n_bins,
                colorscale='Viridis',
                name=st
            )
            
            heatmap_data.append(
                go.Figure(
                    data=[heatmap],
                    layout=dict(
                        title=f'Distribución de errores para {st}',
                        xaxis_title='Valor de x',
                        yaxis_title='Número de Términos',
                        height=500,
                        width=700
                    )
                )
            )
        
        # Convertir a JSON
        graph1_json = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)
        heatmap_json = [json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder) for fig in heatmap_data]
        
        return jsonify({
            'data': data,
            'graphs': {
                'error_3d': graph1_json,
                'heatmaps': heatmap_json,
                'series_types': df['series_type'].unique().tolist()
            }
        })
    
    return jsonify({'data': [], 'graphs': {}})

@app.route('/api/last_calculation')
def get_last_calculation():
    """API para obtener el último cálculo realizado (para actualizaciones en tiempo real)."""
    global last_calculation_id
    
    if last_calculation_id == 0:
        return jsonify({'status': 'error', 'message': 'No hay cálculos recientes'})
    
    try:
        cursor = db.conn.cursor()
        cursor.execute('''
            SELECT u.username, c.series_type, c.x_value, c.n_terms, c.result, c.exact_value, c.error, c.calculation_time 
            FROM calculations c
            JOIN users u ON c.user_id = u.id
            WHERE c.id = ?
            ''', (last_calculation_id,))
        
        calculation = cursor.fetchone()
        
        if not calculation:
            return jsonify({'status': 'error', 'message': 'Cálculo no encontrado'})
        
        username, series_type, x_value, n_terms, result, exact_value, error, time = calculation
        
        return jsonify({
            'status': 'success',
            'calculation': {
                'username': username,
                'series_type': series_type,
                'x_value': x_value,
                'n_terms': n_terms,
                'result': result,
                'exact_value': exact_value,
                'error': error,
                'time': time
            }
        })
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
