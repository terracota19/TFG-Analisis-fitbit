@echo off

REM Configurar variables
SET MONGO_PATH="C:\Program Files\MongoDB\Server\7.0\bin\mongod.exe"
SET DB_PATH="C:\hlocal\datos"

REM Verificar si pip está instalado
python -m pip --version
IF %ERRORLEVEL% NEQ 0 (
    echo Installing pip...
    python -m ensurepip --default-pip
)

REM Instalar dependencias desde requirements.txt
echo Installing dependencies...
pip install -r app/main/requirements.txt

REM Iniciar MongoDB en segundo plano
start "" /B %MONGO_PATH% --dbpath %DB_PATH%

REM Ejecutar la app de Python
start "" "python.exe" "/app/main/main.py"
