FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt \
    --index-url https://mirror-pypi.runflare.com/simple \
    --trusted-host mirror-pypi.runflare.com

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && uvicorn App.main:app --host 0.0.0.0 --port 8000"]
