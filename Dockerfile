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

CMD ["python", "start.py"]