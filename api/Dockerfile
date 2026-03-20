# Etapa 1: Constructor
FROM python:3.12-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copiamos la configuración del workspace completo desde la raíz
COPY pyproject.toml uv.lock ./
COPY shared/pyproject.toml ./shared/
COPY api/pyproject.toml ./api/
COPY subscriber/pyproject.toml ./subscriber/
COPY publisher/pyproject.toml ./publisher/

# Instalamos dependencias sin el código todavía para aprovechar la caché
RUN uv sync --frozen --no-dev --no-install-workspace

# Ahora copiamos el código necesario
COPY shared/ ./shared/
COPY api/ ./api/

# Sincronización final del paquete específico
RUN uv sync --frozen --no-dev --package api

# Etapa 2: Final
FROM python:3.12-slim
WORKDIR /app

# Copiamos solo el entorno virtual y el código fuente
COPY --from=builder /app/.venv /app/.venv
COPY shared/ ./shared/
COPY api/ ./api/

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app:/app/api:/app/shared/src"

# Ejecución desde la carpeta de la api
WORKDIR /app/api
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]