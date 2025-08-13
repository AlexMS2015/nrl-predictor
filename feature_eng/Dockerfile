FROM python:3.12-slim

RUN python3 -m pip install poetry==${POETRY_VERSION}

WORKDIR /app

COPY ../README.md ../pyproject.toml ../poetry.lock .

# cached:
RUN poetry install --no-interaction --no-ansi --no-root --only main

COPY ../config.py ../config.yaml .
COPY ../utilities ./utilities/
COPY feature_eng/ ./feature_eng/

# install the project as a package:
RUN poetry install --no-interaction --no-ansi --only main

WORKDIR /app/scraper
ENTRYPOINT ["poetry", "run", "python", "-m", "feature_eng.run"]
