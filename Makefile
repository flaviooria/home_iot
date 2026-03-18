# 1. Detección del Sistema Operativo
ifeq ($(OS),Windows_NT)
    # Configuración para Windows
    OS_TYPE := Windows
    VENV_BIN := .venv/Scripts
    PYTHON := $(VENV_BIN)/python.exe
    UV := $(VENV_BIN)/uv.exe
    ALEMBIC := $(VENV_BIN)/alembic.exe
    RM := rmdir /s /q
    MKDIR := mkdir
    SEP := \\
else
    # Configuración para Unix (Linux/macOS)
    OS_TYPE := Unix
    VENV_BIN := .venv/bin
    PYTHON := $(VENV_BIN)/python
    UV := $(VENV_BIN)/uv
    ALEMBIC := $(VENV_BIN)/alembic
    RM := rm -rf
    MKDIR := mkdir -p
    SEP := /
endif

.PHONY: setup install up down clean migrate-up migrate-new

# --- COMANDOS PRINCIPALES ---

setup:
	@echo "Detectado: $(OS_TYPE)"
	@if [ "$(OS_TYPE)" = "Unix" ]; then \
		chmod +x scripts/setup_env.sh && ./scripts/setup_env.sh; \
	else \
		powershell.exe -ExecutionPolicy Bypass -File ./setup_env.ps1; \
	fi

install:
	$(UV) sync --all-packages

up:
	docker compose up --build -d

down:
	docker compose down

# --- MIGRACIONES ---

migrate-up:
	$(ALEMBIC) upgrade head

# Uso: make migrate-new m="descripcion"
migrate-new:
	$(ALEMBIC) revision --autogenerate -m "$(m)"

clean:
	$(RM) .venv
	@echo "Entorno eliminado."