FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "worker.py"] 
# worker.py est le script qui contient la logique de travailleur pour traiter les tâches en arrière-plan.

