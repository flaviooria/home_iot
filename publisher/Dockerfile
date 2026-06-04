FROM python:3.11-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:0.11.9 /uv /bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock ./

COPY shared/pyproject.toml ./shared/
COPY api/pyproject.toml ./api/
COPY subscriber/pyproject.toml ./subscriber/
COPY publisher/pyproject.toml ./publisher/

RUN uv sync --frozen --no-dev --no-install-workspace

COPY shared/ ./shared/
COPY publisher/ ./publisher/

RUN uv sync --frozen --no-dev --package publisher --no-cache \
    && rm -rf /root/.cache

FROM python:3.11-slim
WORKDIR /app

COPY --from=builder /app/.venv /app/.venv

COPY --from=builder /app/shared/ /app/shared/
COPY --from=builder /app/publisher/ /app/publisher/

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app:/app/publisher"

RUN useradd -ms /bin/bash appuser \
    && mkdir -p /app/.logs \
    && chown appuser:appuser /app/.logs

USER appuser

CMD ["python", "publisher/main.py"]