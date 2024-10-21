FROM python:3.9-slim

# Establecer directorio de trabajo
WORKDIR /app

# Copiar el archivo requirements.txt desde la raíz del proyecto
COPY ../../../../requirements.txt /app/requirements.txt

# Copiar todo el contenido de la API al contenedor
COPY . /app/

# Instalar las dependencias necesarias
RUN pip install --no-cache-dir -r /app/requirements.txt

# Exponer el puerto 8000 para la API
EXPOSE 8000

# Ejecutar la API usando Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
