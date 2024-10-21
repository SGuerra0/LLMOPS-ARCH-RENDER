FROM python:3.9-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia el archivo requirements.txt desde la raíz del proyecto al contenedor
COPY ../../requirements.txt /app/requirements.txt

# Copia todo el contenido de la carpeta frontend al contenedor
COPY . /app/

# Instala las dependencias
RUN pip install --no-cache-dir -r /app/requirements.txt

# Exponer el puerto de Streamlit
EXPOSE 8501

# Comando para ejecutar Streamlit
CMD ["streamlit", "run", "main_streamlit.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
