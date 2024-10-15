FROM python:3.9

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY frontend /app/frontend

EXPOSE ${PORT}

CMD ["streamlit", "run", "frontend/main_streamlit.py", "--server.port", "${PORT}", "--server.address", "0.0.0.0"]
