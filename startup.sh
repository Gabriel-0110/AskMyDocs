#!/bin/bash
# Start Streamlit app
streamlit run AskMyDocs/main.py \
    --server.port=$PORT \
    --server.address=0.0.0.0
