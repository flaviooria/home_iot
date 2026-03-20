# Etapa 1: Constructor
FROM python:3.12-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app
# 1. Copiar archivos de configuración del workspace
COPY pyproject.toml uv.lock ./
COPY shared/pyproject.toml ./shared/
COPY api/pyproject.toml ./api/
COPY subscriber/pyproject.toml ./subscriber/
COPY publisher/pyproject.toml ./publisher/
# 2. Instalar dependencias
RUN uv sync --frozen --no-dev --no-install-workspace
# 3. Copiar el código fuente necesario
COPY shared/ ./shared/
COPY publisher/ ./publisher/
# 4. Sincronizar el proyecto del publisher específicamente
RUN uv sync --frozen --no-dev --package publisher
# Etapa 2: Final
FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY shared/ ./shared/
COPY publisher/ ./publisher/
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app:/app/publisher"
WORKDIR /app/publisher
CMD ["python", "main.py"]
