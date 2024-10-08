# Use an official Python runtime as a base image
FROM python:3.9

# Set environment variables
# RUN export $(grep -v '^#' .env | xargs)

# Set the working directory
WORKDIR /fai_inf01_tp01_01

# Copy the application code
COPY fai_inf01_tp01_01 .

# Install dependencies
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Expose the ports for FastAPI and Streamlit
EXPOSE 8000
EXPOSE 8501

# Start the FastAPI server and Streamlit application
CMD ["bash", "-c", "uvicorn main:app --host 0.0.0.0 --port 8000 & streamlit run frontend/main_streamlit.py --server.port 8501"]