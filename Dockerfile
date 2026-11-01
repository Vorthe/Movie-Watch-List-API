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

CMD ["sh", "-c", "echo 'Starting application...'; uvicorn App.main:app --host 0.0.0.0 --port 8000 & echo 'Waiting for DB...'; python wait_for_db.py && alembic upgrade head; echo 'Migrations done!'; wait"]