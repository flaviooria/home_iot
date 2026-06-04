FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_LINK_MODE=copy

# uv
COPY --from=ghcr.io/astral-sh/uv:0.11.9 /uv /bin/uv

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
RUN uv sync \
    --frozen \
    --no-dev \
    --package api \
    --no-cache

RUN rm -rf /root/.cache

# Etapa 2: Runtime
FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv

COPY --from=builder /app/shared /app/shared
COPY --from=builder /app/migrations /app/migrations
COPY --from=builder /app/alembic.ini /app/alembic.ini
COPY --from=builder /app/api /app/api


ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app:/app/api"

RUN useradd -ms /bin/bash appuser
USER appuser

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]