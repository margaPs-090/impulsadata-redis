# Imagen de la aplicación Python (scripts de Redis + MySQL)
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .
RUN python -m pip install --upgrade pip && pip install -r requirements.txt

COPY app/ .

# Por defecto ejecuta los ejercicios 1-20
CMD ["python", "tutorial_redis.py"]
