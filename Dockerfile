# Usar una imagen base de Python
FROM python:3.10

# Establecer un directorio de trabajo
WORKDIR /app

# Copiar el archivo de requerimientos al contenedor
COPY requirements.txt .

# Instalar las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código de la aplicación al contenedor
COPY ./src/ .

# Establecer variables de entorno si es necesario (por ejemplo, configuraciones, modo debug, etc.)
# ENV VARIABLE=value

# Exponer el puerto en el que se ejecutará la aplicación
EXPOSE 8000

# Comando por defecto para ejecutar la aplicación cuando el contenedor arranque
CMD ["python", "src/main.py"]
