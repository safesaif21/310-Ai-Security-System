#!/bin/bash

# Navigate to the project root directory
cd "$(dirname "$0")"

# Check if .venv exists and activate it
if [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/Scripts/activate || source .venv/bin/activate
else
    echo "Warning: .venv not found. Running with global python (ensure dependencies are installed)."
fi

# Set python path
export PYTHONPATH=$PYTHONPATH:.

echo "Starting Local Camera Service..."
python -m backend.services.camera.main
