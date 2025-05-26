# Dockerfile for server/Dockerfile
FROM python:3.11-slim

WORKDIR /

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .
RUN pip install -e .
RUN pip install -e src/xenq_server/components/LightRAG
EXPOSE 8000

CMD ["chainlit", "run", "main.py", "--host", "0.0.0.0", "--port", "8000"]]

