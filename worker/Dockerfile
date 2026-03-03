FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y libreoffice-writer \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PYTHONUNBUFFERED=1
ENV LIBREOFFICE_PATH=/usr/bin/libreoffice
CMD ["python", "worker.py"]