FROM python:3.9-slim

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar el archivo requirements.txt desde la raíz del proyecto
COPY ../../requirements.txt /app/requirements.txt

# Copiar todo el contenido de la carpeta API al contenedor
COPY . /app/

# Instalar las dependencias
RUN pip install --no-cache-dir -r /app/requirements.txt

# Exponer el puerto 8000 para la API
EXPOSE 8000

# Comando para ejecutar la API con Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
