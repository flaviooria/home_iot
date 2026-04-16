FROM python:3.12-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY shared/pyproject.toml ./shared/
COPY subscriber/pyproject.toml ./subscriber/
COPY api/pyproject.toml ./api/
COPY publisher/pyproject.toml ./publisher/

RUN uv sync --frozen --no-dev --no-install-workspace

COPY shared/ ./shared/
COPY subscriber/ ./subscriber/

RUN uv sync --frozen --no-dev --package subscriber

FROM python:3.12-slim
WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY shared/ ./shared/
COPY subscriber/ ./subscriber/

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app:/app/subscriber:/app/shared/src"

WORKDIR /app/subscriber
# Usamos -m para asegurar que los imports relativos funcionen si es un paquete
CMD ["python", "main.py"]