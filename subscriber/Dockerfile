FROM python:3.12-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:0.11.9 /uv /bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY shared/pyproject.toml ./shared/
COPY subscriber/pyproject.toml ./subscriber/
COPY api/pyproject.toml ./api/
COPY publisher/pyproject.toml ./publisher/

RUN uv sync --frozen --no-dev --no-install-workspace

COPY shared/ ./shared/
COPY subscriber/ ./subscriber/

RUN uv sync --frozen --no-dev --package subscriber --no-cache \
    && rm -rf /root/.cache

FROM python:3.12-slim
WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/shared/ /app/shared/
COPY --from=builder /app/subscriber/ /app/subscriber/

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app:/app/subscriber"

RUN useradd -ms /bin/bash appuser \
    && mkdir -p /app/.logs \
    && chown appuser:appuser /app/.logs
USER appuser

# Usamos -m para asegurar que los imports relativos funcionen si es un paquete
CMD ["python", "subscriber/main.py"]