FROM selenium/standalone-chrome:latest

USER root

ENV CHROME_VERSION=114.0.5735.90 \
    POETRY_VERSION=2.1.3 \
    POETRY_VIRTUALENVS_CREATE=false \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    RUNNING_IN_DOCKER=true

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl build-essential ca-certificates && \
    rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install poetry==${POETRY_VERSION}

WORKDIR /app

COPY pyproject.toml poetry.lock* ./
RUN poetry install --no-interaction --no-ansi --no-root --only main

COPY src/gcp.env src/config.py src/config.yaml src/__init__.py .
COPY src/utilities ./utilities
COPY src/scraping ./scraping

ENTRYPOINT ["python", "-m", "scraping.run"]