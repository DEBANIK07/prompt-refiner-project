#!/bin/bash
# Starts the FastAPI backend on port 8000.
# Run this from the project root: bash run.sh

cd "$(dirname "$0")/backend" || exit 1

echo "Starting AI Prompt Refiner backend on http://localhost:8000 ..."
uv run uvicorn main:app --reload --port 8000
