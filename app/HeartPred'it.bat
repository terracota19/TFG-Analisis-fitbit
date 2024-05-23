@echo off

REM Iniciar MongoDB
start "" /B "C:\Program Files\MongoDB\Server\7.0\bin\mongod.exe" --dbpath "C:\hlocal\datos"

REM Esperar 5 segundos
timeout /t 5

REM Ejecutar la app
start "" "python.exe" "main.py"
