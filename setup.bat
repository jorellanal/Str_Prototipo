@echo off
REM setup.bat - Bootstrap del entorno SVP-IPS (Windows cmd).
REM Crea el .venv e instala dependencias. Ejecutar una vez por clonacion.
REM
REM Uso:
REM   setup.bat

setlocal

cd /d "%~dp0"

echo === SVP-IPS - Setup (cmd) ===

if not exist ".venv\Scripts\python.exe" (
    echo [1/3] Creando entorno virtual .venv...
    python -m venv .venv
) else (
    echo [1/3] .venv ya existe, se omite.
)

echo [2/3] Actualizando pip...
".venv\Scripts\python.exe" -m pip install --upgrade pip --quiet

echo [3/3] Instalando requirements.txt...
".venv\Scripts\python.exe" -m pip install -r requirements.txt --quiet

echo.
echo Listo. Para ejecutar la app:
echo   .venv\Scripts\activate.bat
echo   streamlit run app.py

endlocal