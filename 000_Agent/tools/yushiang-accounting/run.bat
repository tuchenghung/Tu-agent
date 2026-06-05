@echo off
cd /d %~dp0
set PYTHON=C:\Users\deco01\AppData\Local\Python\pythoncore-3.14-64\python.exe
%PYTHON% -m pip install -r requirements.txt -q
%PYTHON% -m streamlit run app.py --server.port 8502
pause
