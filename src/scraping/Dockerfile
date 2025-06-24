# FROM python:3.12-slim
FROM selenium/standalone-chrome:latest

USER root

ENV CHROME_VERSION=114.0.5735.90 \
    POETRY_VERSION=2.1.3 \
    POETRY_VIRTUALENVS_CREATE=false \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    RUNNING_IN_DOCKER=true

# Install OS dependencies
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     curl unzip gnupg build-essential ca-certificates fonts-liberation libappindicator3-1 libasound2 \
#     libatk-bridge2.0-0 libatk1.0-0 libcups2 libdbus-1-3 libgdk-pixbuf2.0-0 libnspr4 libnss3 \
#     libxcomposite1 libxdamage1 libxrandr2 xdg-utils wget && \
#     rm -rf /var/lib/apt/lists/*
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl build-essential ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Install Chrome
# RUN curl -sSL https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google.gpg && \
#     echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
#     apt-get update && apt-get install -y google-chrome-stable && \
#     rm -rf /var/lib/apt/lists/*

# RUN curl -sSL https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_${CHROME_VERSION}-1_amd64.deb -o chrome.deb && \
#     curl -fSL https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_114.0.5735.90-1_amd64.deb -o chrome.deb
#     apt-get update && \
#     apt-get install -y ./chrome.deb && \
#     rm chrome.deb && rm -rf /var/lib/apt/lists/*

# # Install chromedriver
# RUN curl -sSL "https://chromedriver.storage.googleapis.com/${CHROME_VERSION}/chromedriver_linux64.zip" -o chromedriver.zip && \
#     unzip chromedriver.zip && \
#     mv chromedriver /usr/bin/chromedriver && \
#     chmod +x /usr/bin/chromedriver && \
#     rm chromedriver.zip

# Install Poetry
# RUN curl -sSL https://install.python-poetry.org | python3 - && \
#     apt-get purge -y curl && apt-get clean
RUN python3 -m pip install poetry==${POETRY_VERSION}

# ENV PATH="/root/.local/bin:$PATH"

# RUN ls -la /root/.local/bin/ && echo $PATH && which poetry
RUN which poetry && poetry --version  # Simple check instead

WORKDIR /app

COPY pyproject.toml poetry.lock* ./
RUN poetry install --no-interaction --no-ansi --no-root --only main

COPY src/gcp.env src/config.py src/config.yaml src/__init__.py .
COPY src/utilities ./utilities
COPY src/scraping ./scraping

ENTRYPOINT ["python", "-m", "scraping.run"]