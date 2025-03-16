# Proyecto Cliente-Servidor Series Trigonométricas

Este proyecto implementa un sistema cliente-servidor en Python para calcular aproximaciones de series trigonométricas (seno, coseno y tangente) utilizando series de Taylor. Incluye un dashboard web para visualizar los resultados y análisis de errores.

## Características

- **Servidor de cálculo**: Procesa solicitudes para calcular aproximaciones de series trigonométricas.
- **Cliente de consola**: Permite a los usuarios realizar cálculos desde la terminal.
- **Dashboard web**: Visualiza datos, gráficos y análisis de errores en un navegador web.
- **Calculadora web**: Interfaz para realizar cálculos directamente desde el navegador.
- **Base de datos**: Almacena usuarios, cálculos y resultados.

## Series implementadas

1. **Seno (sin)**: Serie de Taylor para aproximar la función seno
   ```
   sin(x) = x - x^3/3! + x^5/5! - x^7/7! + ...
   ```

2. **Coseno (cos)**: Serie de Taylor para aproximar la función coseno
   ```
   cos(x) = 1 - x^2/2! + x^4/4! - x^6/6! + ...
   ```

3. **Tangente (tan)**: Calculada como sin(x)/cos(x)

## Requisitos

- Python 3.7+
- SQLite
- Flask
- Plotly
- Pandas
- Numpy

## Instalación

1. Clonar el repositorio o descargar los archivos

2. Instalar dependencias:
   ```bash
   pip install flask plotly pandas numpy
   ```

## Uso

### Iniciar el sistema completo

```bash
python run.py
```

Esto iniciará tanto el servidor de cálculos (en el puerto 5555) como el dashboard web (en el puerto 5000).

### Opciones de inicio

- Solo servidor de cálculos:
  ```bash
  python run.py --mode calc
  ```

- Solo dashboard web:
  ```bash
  python run.py --mode dash
  ```

### Acceder al sistema

- **Dashboard**: Abrir un navegador web y acceder a `http://localhost:5000/dashboard`
- **Calculadora web**: Acceder a `http://localhost:5000`
- **Cliente de consola**: Ejecutar `python client.py`

## Estructura del proyecto

- `server.py`: Servidor que maneja conexiones y cálculos
- `client.py`: Cliente de consola para interactuar con el servidor
- `database.py`: Gestión de la base de datos
- `series_calculator.py`: Implementación de las series trigonométricas
- `dashboard.py`: Aplicación Flask para el dashboard web
- `run.py`: Script para iniciar el sistema
- `templates/`: Plantillas HTML para la interfaz web
- `static/`: Archivos JavaScript y CSS para la interfaz web

## API REST (Dashboard)

El dashboard proporciona las siguientes rutas API:

- `GET /api/summary`: Resumen general de cálculos
- `GET /api/user_data?username={username}`: Datos específicos de un usuario
- `GET /api/series_data?type={type}`: Datos específicos de un tipo de serie
- `GET /api/error_analysis`: Análisis detallado de errores
- `POST /api/calculate`: Realizar un nuevo cálculo
- `GET /api/user_history?username={username}`: Historial de cálculos de un usuario
- `GET /api/last_calculation`: Último cálculo realizado

## Autores

- Nombre del Estudiante
- Institución Educativa
