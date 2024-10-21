FROM python:3.9-slim

WORKDIR /app

# Copy the shared requirements.txt file
COPY ../../../../requirements.txt /app/requirements.txt

# Copy the Streamlit app files
COPY . /app/

RUN pip install --no-cache-dir -r /app/requirements.txt

EXPOSE 8501

CMD ["streamlit", "run", "main_streamlit.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
