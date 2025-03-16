FROM python:3.9-slim

WORKDIR /app

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar archivos del proyecto
COPY . .

# Puerto para el dashboard
EXPOSE 5000
# Puerto para el servidor de cálculos
EXPOSE 5555

# Comando por defecto (ejecutar ambos servicios)
CMD ["python", "run.py"]
