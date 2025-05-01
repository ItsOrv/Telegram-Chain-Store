#!/bin/bash
# Script to set up virtual environment and install dependencies

# Create a new virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
else
    echo "Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

echo "Environment setup complete!"
echo "To activate the environment, run: source venv/bin/activate"
echo "To run the bot, use one of these commands:"
echo "  python3 -m src.main"
echo "  python3 run.py"
echo "  python3 run_with_path.py" 