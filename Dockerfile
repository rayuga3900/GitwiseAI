FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN apt-get update && apt-get install -y git && \
    pip install -r requirements.txt

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080"]
