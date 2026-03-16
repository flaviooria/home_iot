# Etapa 1: Constructor
FROM python:3.12-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# 1. Copiar archivos de configuración del workspace
# OJO: Debes copiar TODOS los toml de los miembros declarados en el workspace
COPY pyproject.toml uv.lock ./
COPY shared/pyproject.toml ./shared/
COPY api/pyproject.toml ./api/
COPY subscriber/pyproject.toml ./subscriber/
COPY publisher/pyproject.toml ./publisher/

# 2. Instalar dependencias
# Usamos --no-install-workspace para que no falle si aún no hemos copiado el código
RUN uv sync --frozen --no-dev --no-install-workspace

# 3. Copiar el código fuente necesario
COPY shared/ ./shared/
COPY api/ ./api/

# 4. Sincronizar el proyecto de la API específicamente
RUN uv sync --frozen --no-dev --package api

# Etapa 2: Final
FROM python:3.12-slim
WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY shared/ ./shared/
COPY api/ ./api/

ENV PATH="/app/.venv/bin:$PATH"
# Añadimos AMBAS al path por seguridad
ENV PYTHONPATH="/app:/app/api"

# Ejecutamos DESDE la carpeta api
WORKDIR /app/api

# Ejecución con uvicorn
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]