@echo off

REM Step 2: Check if a virtual environment exists
if not exist venv\Scripts\activate.bat (
    echo Creating virtual environment...
    REM Step 3: Create virtual environment
    python -m venv venv
    echo Virtual environment created.
)

REM Step 3: Activate virtual environment and install requirements
echo Activating virtual environment...
call venv\Scripts\activate
pip install --upgrade pip
echo Installing requirements...
pip install --no-deps -r requirements.txt
echo Requirements installed.

REM Step 4: Run Python file using the virtual environment
echo Running Python file...
python Interface.py

REM Cleanup: Deactivate virtual environment
echo Deactivating virtual environment...
deactivate
echo Virtual environment deactivated.

REM End of batch file
echo Batch file execution completed.
pause