FROM python:3.12-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app

# 1. Copiamos todos los toml (Workspace completo)
COPY pyproject.toml uv.lock ./
COPY shared/pyproject.toml ./shared/
COPY subscriber/pyproject.toml ./subscriber/
COPY api/pyproject.toml ./api/
COPY publisher/pyproject.toml ./publisher/

# 2. Instalamos dependencias externas
RUN uv sync --frozen --no-dev --no-install-workspace

# 3. Código del subscriber y shared
COPY shared/ ./shared/
COPY subscriber/ ./subscriber/

# 4. Sincronización final
RUN uv sync --frozen --no-dev --package subscriber

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY shared/ ./shared/
COPY subscriber/ ./subscriber/

ENV PATH="/app/.venv/bin:$PATH"
# Añadimos AMBAS al path por seguridad
ENV PYTHONPATH="/app:/app/subscriber"

# Ejecutamos DESDE la carpeta api
WORKDIR /app/subscriber

# Ejecutamos el suscriptor (asumiendo que main.py está en subscriber/main.py)
CMD ["python", "-m", "subscriber.main"]