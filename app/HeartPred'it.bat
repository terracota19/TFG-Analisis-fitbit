@echo off

REM Iniciar MongoDB en segundo plano
start "" /B "C:\Program Files\MongoDB\Server\7.0\bin\mongod.exe" --dbpath "C:\hlocal\datos"

REM Esperar 7 segundos
timeout /t 7

REM Ejecutar la app de Python
start "" "python.exe" "main.py"
