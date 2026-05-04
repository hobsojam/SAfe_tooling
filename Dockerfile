FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
COPY safe/ safe/

RUN pip install --no-cache-dir "."

ENV SAFE_API_HOST=0.0.0.0
ENV SAFE_API_PORT=8000
ENV SAFE_DB_PATH=/data/db.json

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "safe.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
