#!/bin/bash
set -e

# 1. Crear venv inicial si no existe
if [ ! -d ".venv" ]; then
    echo "Creando entorno virtual inicial..."
    python3 -m venv .venv
fi

# 2. Instalar uv localmente
echo "Instalando uv en el entorno..."
.venv/bin/pip install uv

# 3. Sincronizar monorepo (usará el Python definido en .python-version)
echo "Sincronizando todos los servicios del monorepo..."
.venv/bin/uv sync --all-packages

echo "Entorno 'home_iot' configurado con éxito."