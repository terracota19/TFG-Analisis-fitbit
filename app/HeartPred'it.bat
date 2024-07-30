@echo off

REM GLOBAL VARIABLES
SET MONGO_PATH="C:\Program Files\MongoDB\Server\7.0\bin\mongod.exe"
SET DB_PATH="C:\hlocal\datos"

REM CHECK WHETHER %DB_PATH% exists or not, and creating if it does not exist
IF NOT EXIST %DB_PATH% (
    echo Creating directory %DB_PATH%...
    mkdir %DB_PATH%
)

REM Check pip version and ensuring localhost has it, in order to install HeartPred'it dependancies.
python -m pip --version
IF %ERRORLEVEL% NEQ 0 (
    echo Installing pip...
    python -m ensurepip --default-pip
)

REM Installing HeartPred'it dependencies.
echo Installing HeartPred'it dependencies...
pip install -r requirements.txt

REM Start MongoDB on %DB_PATH%.
start "" /B %MONGO_PATH% --dbpath %DB_PATH%

REM Start HeartPred'it App.
start "" "python.exe" "main.py"
