@echo off
echo Instalando dependencias para RadiaCode...

:: Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo Python no encontrado. Descargando Python...
    curl https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe -o python-installer.exe
    python-installer.exe /quiet InstallAllUsers=1 PrependPath=1
    del python-installer.exe
)

:: Ejecutar script de instalación
python install_dependencies.py

pause 