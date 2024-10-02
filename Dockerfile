# Step 1: Define the base image
FROM python:3.9

# Step 2: Set the working directory inside the container
WORKDIR /FAI-STG01-TP01-01

# Step 3: Copy the local code into the container
COPY FAI-STG01-TP01-01 .

# Step 4: Install dependencies
RUN pip install --upgrade pip

# !python3 -m spacy download es_core_news_sm
RUN pip install --no-cache-dir -r requirements.txt

RUN python3 -m spacy download es_core_news_sm

# Step 5: Specify the command to run your application
#CMD ["python", "main.py"]