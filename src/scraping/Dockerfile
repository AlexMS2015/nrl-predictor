# FROM python:3.12-slim
FROM selenium/standalone-chrome:124.0-20250606

ENV POETRY_VERSION=2.1.3 \
    POETRY_VIRTUALENVS_CREATE=false \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    RUNNING_IN_DOCKER=true

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl build-essential && \
    curl -sSL https://install.python-poetry.org | python3 - && \
    apt-get purge -y curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

COPY pyproject.toml poetry.lock* ./
RUN poetry install --no-interaction --no-ansi --no-root --only main

COPY src/gcp.env src/config.py src/config.yaml src/__init__.py .
COPY src/utilities ./utilities
COPY src/scraping ./scraping

ENTRYPOINT ["python", "-m", "scraping.run"]