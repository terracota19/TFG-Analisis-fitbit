@echo off

REM 
SET MONGO_PATH="C:\Program Files\MongoDB\Server\7.0\bin\mongod.exe"
SET DB_PATH="C:\hlocal\datos"

REM 
IF NOT EXIST %DB_PATH% (
    echo Creating directory %DB_PATH%...
    mkdir %DB_PATH%
)

REM 
python -m pip --version
IF %ERRORLEVEL% NEQ 0 (
    echo Installing pip...
    python -m ensurepip --default-pip
)

REM
echo Installing dependencies...
pip install -r requirements.txt

REM 
start "" /B %MONGO_PATH% --dbpath %DB_PATH%

REM 
start "" "python.exe" "main.py"
