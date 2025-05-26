# Dockerfile for agent/Dockerfile
FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime

# Assuming you start FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime or your chosen base

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .
RUN pip install -e .
EXPOSE 5007

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5007"]

