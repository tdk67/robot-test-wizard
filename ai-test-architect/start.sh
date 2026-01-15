#!/bin/bash
# start.sh

echo "--- KILLING OLD PROCESSES ---"
pkill -f uvicorn
pkill -f streamlit

echo "--- STARTING BACKEND (Port 8000) ---"
# Run Uvicorn in background (&)
uvicorn backend.main:app --host 0.0.0.0 --port 8000 &

echo "Waiting for backend..."
sleep 3

echo "--- STARTING FRONTEND (Port 8501) ---"
streamlit run frontend/app.py --server.port 8501