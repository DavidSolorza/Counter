FROM python:3.12-slim

WORKDIR /workspace

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY back/flask-analytics/requirements.txt /workspace/requirements.txt
RUN pip install --no-cache-dir -r /workspace/requirements.txt

# Copiar estructura respetando rutas relativas de tracker.js y prueba.html
COPY back/flask-analytics /workspace/back/flask-analytics
COPY back/library /workspace/back/library
COPY prueba.html /workspace/prueba.html
COPY app.py /workspace/app.py

WORKDIR /workspace/back/flask-analytics

ENV PYTHONUNBUFFERED=1
ENV PORT=5000

EXPOSE 5000

CMD ["gunicorn", "--workers", "4", "--threads", "2", "--bind", "0.0.0.0:5000", "app:create_app()"]
