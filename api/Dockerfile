FROM python:3.12-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY shared/pyproject.toml ./shared/pyproject.toml
COPY api/pyproject.toml ./api/pyproject.toml
COPY subscriber/pyproject.toml ./subscriber/pyproject.toml
COPY publisher/pyproject.toml ./publisher/pyproject.toml

# Resolver dependencias (sin --no-dev porque alembic es producción)
RUN uv sync --frozen --no-install-workspace

COPY shared/ ./shared/
COPY api/ ./api/
COPY migrations/ ./migrations/
COPY alembic.ini ./alembic.ini

# Instalar solo el paquete api (incluye alembic)
RUN uv sync --frozen --package api

# Etapa 2: Runtime
FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY shared/ ./shared/
COPY api/ ./api/
COPY migrations/ ./migrations/
COPY alembic.ini ./alembic.ini

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app:/app/api:/app/shared/src"

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]