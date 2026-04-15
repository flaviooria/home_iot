FROM python:3.12-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY shared/pyproject.toml ./shared/
COPY api/pyproject.toml ./api/
COPY subscriber/pyproject.toml ./subscriber/
COPY publisher/pyproject.toml ./publisher/

RUN uv sync --frozen --no-dev --no-install-workspace

COPY shared/ ./shared/
COPY publisher/ ./publisher/

RUN uv sync --frozen --no-dev --package publisher

FROM python:3.12-slim
WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY shared/ ./shared/
COPY publisher/ ./publisher/

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app:/app/publisher:/app/shared/src"

WORKDIR /app/publisher
CMD ["python", "main.py"]
