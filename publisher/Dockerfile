FROM python:3.12-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app

# 1. Copiamos todos los toml (Workspace completo)
COPY pyproject.toml uv.lock ./
COPY shared/pyproject.toml ./shared/
COPY publisher/pyproject.toml ./publisher/
COPY api/pyproject.toml ./api/
COPY publisher/pyproject.toml ./publisher/

# 2. Instalamos dependencias externas
RUN uv sync --frozen --no-dev --no-install-workspace

# 3. Código del publisher y shared
COPY shared/ ./shared/
COPY publisher/ ./publisher/

# 4. Sincronización final
RUN uv sync --frozen --no-dev --package publisher

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY shared/ ./shared/
COPY publisher/ ./publisher/

ENV PATH="/app/.venv/bin:$PATH"
# Añadimos AMBAS al path por seguridad
ENV PYTHONPATH="/app:/app/publisher"

# Ejecutamos DESDE la carpeta api
WORKDIR /app/publisher

# Ejecutamos el suscriptor (asumiendo que main.py está en publisher/main.py)
CMD ["python", "-m", "publisher.main"]