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

CMD ["sh", "-c", "for i in 1 2 3 4 5; do echo \"Attempting alembic upgrade (try $i)...\"; alembic upgrade head && break; echo \"Migration failed. Retrying in 5 seconds...\"; sleep 5; done && uvicorn App.main:app --host 0.0.0.0 --port 8000"]