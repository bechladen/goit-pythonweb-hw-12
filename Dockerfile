FROM python:3.10-slim

WORKDIR /app

RUN pip install --no-cache-dir poetry

COPY pyproject.toml /app/pyproject.toml
COPY poetry.lock /app/poetry.lock

RUN poetry config virtualenvs.create false \
  && poetry install --only main --no-interaction --no-ansi

COPY . /app

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
