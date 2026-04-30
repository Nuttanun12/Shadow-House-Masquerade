@echo off
echo Setting up Shadow House Masquerade environment for Windows...

:: Create virtual environment
python -m venv venv

:: Activate virtual environment and install requirements
call venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt

echo Environment setup complete!
echo To run the game, use: venv\Scripts\activate ^&^& python main.py
pause
