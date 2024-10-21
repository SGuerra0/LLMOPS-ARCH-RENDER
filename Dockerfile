# Imagen base de Python
FROM python:3.9-slim

# Establecer directorio de trabajo
WORKDIR /app

# Copiar el archivo de base de datos y dependencias
COPY data/universal/chroma.sqlite3 /app/chroma.sqlite3
COPY requirements.txt /app/requirements.txt

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto para la API de ChromaDB
EXPOSE 7700

# Comando de inicio para el servicio ChromaDB
CMD ["python", "-m", "chromadb", "--host", "0.0.0.0", "--port", "7700"]
