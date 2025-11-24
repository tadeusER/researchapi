# Stage 1: Generar requirements.txt
FROM python:3.12.10-slim as requirements-stage

WORKDIR /tmp

# Instalar pipenv y generar requirements.txt
RUN pip install pipenv
COPY Pipfile Pipfile.lock ./
RUN pipenv requirements > requirements.txt

# Stage 2: Imagen final
FROM python:3.12.10-slim

WORKDIR /app

# Copiar requirements.txt desde el stage anterior
COPY --from=requirements-stage /tmp/requirements.txt .

# Instalar dependencias con pip
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Crear usuario no root (practica de seguridad)
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "src.researchapi.main:app", "--host", "0.0.0.0", "--port", "8000"]

