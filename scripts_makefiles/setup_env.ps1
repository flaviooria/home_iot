# setup_env.ps1
if (!(Test-Path ".venv")) {
    Write-Host "Creando entorno virtual..."
    python -m venv .venv
}

Write-Host "Instalando uv localmente..."
& .venv\Scripts\pip.exe install uv

Write-Host "Sincronizando monorepo..."
& .venv\Scripts\uv.exe sync --all-packages