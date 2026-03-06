#!/bin/bash

echo "Starting ActuLLM..."

python -m pip install --upgrade pip
pip install -r requirements.txt

streamlit run app.py --server.port $PORT --server.address 0.0.0.0