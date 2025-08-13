FROM python:3.12-slim

ENV POETRY_VERSION=2.1.3 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    RUNNING_IN_DOCKER=true

RUN python3 -m pip install poetry==${POETRY_VERSION}

WORKDIR /app

COPY README.md pyproject.toml poetry.lock .

# cached:
RUN poetry install --no-interaction --no-ansi --no-root --only main

COPY config.py config.yaml .
COPY ./utilities ./utilities/
COPY ./scraper/ ./scraper/
COPY ./feature_eng/ ./feature_eng/

# install the project as a package:
RUN poetry install --no-interaction --no-ansi --only main

ENTRYPOINT ["poetry", "run", "python", "-m", "feature_eng.feature_eng.run"]
