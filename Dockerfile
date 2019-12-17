FROM python:3-slim
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && rm -rf /root/.cache

COPY src .
CMD ["python", "-u", "/app/Mercatus.py"]