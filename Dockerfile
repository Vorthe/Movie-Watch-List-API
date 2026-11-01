FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .

ARG PIP_INDEX_URL=https://pypi.org/simple
ARG PIP_TRUSTED_HOST=pypi.org

RUN pip install --no-cache-dir -r requirements.txt \
    --index-url ${PIP_INDEX_URL} \
    --trusted-host ${PIP_TRUSTED_HOST}

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "echo 'Waiting for database to be ready...'; for i in $(seq 1 10); do alembic upgrade head && break; echo \"Migration attempt $i failed. Retrying in 10 seconds...\"; sleep 10; done; echo 'Starting application...'; uvicorn App.main:app --host 0.0.0.0 --port 8000"]