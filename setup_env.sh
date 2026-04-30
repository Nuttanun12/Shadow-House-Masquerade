#!/bin/bash

echo "Setting up Shadow House Masquerade environment..."

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install requirements
pip install --upgrade pip
pip install -r requirements.txt

echo "Environment setup complete!"
echo "To run the game, use: source venv/bin/activate && python main.py"
