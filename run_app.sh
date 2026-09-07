#!/bin/bash
echo "Installing dependencies..."
pip install -r requirements.txt
echo ""
echo "Starting BTP-Engineering Dashboard..."
streamlit run app.py
