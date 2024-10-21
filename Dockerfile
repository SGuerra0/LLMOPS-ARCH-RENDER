# Usar una imagen base oficial de Python
FROM python:3.9

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Copiar el archivo requirements.txt
COPY requirements.txt /app/requirements.txt

# Instalar dependencias
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . /app

# Exponer el puerto asignado por Render
EXPOSE ${PORT}

# Iniciar la aplicación Streamlit
CMD streamlit run frontend/main_streamlit.py --server.port ${PORT} --server.address 0.0.0.0
