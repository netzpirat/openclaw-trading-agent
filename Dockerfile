FROM python:3.12-slim

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl ca-certificates git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy project metadata and install deps
COPY pyproject.toml poetry.lock ./

# Install Poetry lightweightly
ENV POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1
RUN pip install --no-cache-dir poetry && \
    poetry install --no-interaction --no-ansi --no-root

# Copy source
COPY src ./src

# API defaults
ENV APP_PORT=3000
EXPOSE 3000

# Default command: run as module to keep absolute imports working
ENTRYPOINT ["poetry", "run", "python", "-m", "src.main"]


