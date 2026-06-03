#!/bin/bash
cd "$(dirname "$0")"
STREAMLIT="$HOME/Library/Python/3.9/bin/streamlit"
if [ ! -f "$STREAMLIT" ]; then
    STREAMLIT=$(python3 -m site --user-base)/bin/streamlit
fi
"$STREAMLIT" run app.py --server.port 8501 --server.headless false
