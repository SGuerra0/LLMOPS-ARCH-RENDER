# Usar una imagen base oficial de Python
FROM python:3.9

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Copiar el archivo requirements.txt
COPY requirements.txt /app/requirements.txt

# Instalar las dependencias
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copiar todo el código de la aplicación
COPY . /app

# Exponer el puerto asignado por Render
EXPOSE ${PORT}

# Iniciar el servidor FastAPI
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT}
