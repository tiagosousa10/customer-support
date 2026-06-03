FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1 \
    PYTHONUNBUFFERED 1 \
    PIP_NO_CACHE_DIR=1 \
    UV_LINK_MODE=copy

WORKDIR /app

RUN apt-get update && apt-get install -y  --no-install-recommends\
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip uv

# Install dependencies only (cached layer). --no-install-project skips
# building the local package here, which would fail because README.md
# (referenced by pyproject's `readme` field) isn't copied yet.
COPY pyproject.toml uv.lock /app/
RUN uv sync --frozen --no-dev --no-install-project

COPY . /app

# Now the full source (incl. README.md) is present, install the project.
RUN uv sync --frozen --no-dev

EXPOSE 8000 8501

CMD ["uv", "run" , "python", "main.py"]
