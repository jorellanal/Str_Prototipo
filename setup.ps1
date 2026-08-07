# setup.ps1 - Bootstrap del entorno SVP-IPS
# Crea el .venv e instala dependencias. Ejecutar una vez por clonacion.
#
# Uso:
#   .\setup.ps1

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -LiteralPath $root

Write-Host "=== SVP-IPS - Setup ===" -ForegroundColor Cyan

if (-not (Test-Path -LiteralPath ".venv\Scripts\python.exe")) {
    Write-Host "[1/3] Creando entorno virtual .venv..." -ForegroundColor Yellow
    python -m venv .venv
} else {
    Write-Host "[1/3] .venv ya existe, se omite." -ForegroundColor Green
}

Write-Host "[2/3] Actualizando pip..." -ForegroundColor Yellow
.\.venv\Scripts\python.exe -m pip install --upgrade pip --quiet

Write-Host "[3/3] Instalando requirements.txt..." -ForegroundColor Yellow
.\.venv\Scripts\python.exe -m pip install -r requirements.txt --quiet

Write-Host ""
Write-Host "Listo. Para ejecutar la app:" -ForegroundColor Green
Write-Host "  .\.venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "  streamlit run app.py" -ForegroundColor White
