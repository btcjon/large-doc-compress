#!/bin/bash

# Ensure uv is installed
if ! command -v uv &> /dev/null
then
    echo "uv could not be found, installing..."
    pip install uv
fi

# Update requirements.txt based on pyproject.toml
uv pip compile pyproject.toml -o requirements.txt

# Ensure uvicorn is in requirements.txt
if ! grep -q "uvicorn" requirements.txt; then
    echo "uvicorn not found in requirements.txt, adding..."
    echo "uvicorn==0.23.2" >> requirements.txt
fi

# Install packages
uv pip sync requirements.txt

echo "Packages updated successfully!"