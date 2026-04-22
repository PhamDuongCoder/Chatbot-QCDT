@echo off
REM Streamlit Chatbot Launcher for QCDT
REM This script starts the Streamlit chatbot application

cd /d "c:\Users\LENOVO\Documents\GitHub\Chatbot QCĐT"

REM Check if streamlit is installed
python -m pip show streamlit >nul 2>&1
if errorlevel 1 (
    echo.
    echo ===================================================
    echo ERROR: Streamlit is not installed!
    echo ===================================================
    echo.
    echo Please install it first:
    echo   pip install streamlit chromadb google-genai python-dotenv
    echo.
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist ".env" (
    echo.
    echo ===================================================
    echo WARNING: .env file not found!
    echo ===================================================
    echo.
    echo Please create a .env file with:
    echo   GOOGLE_API_KEY=your_api_key_here
    echo.
    echo Continuing anyway...
    pause
)

REM Check if VectorStore exists and has data
if not exist "VectorStore\chroma.sqlite3" (
    echo.
    echo ===================================================
    echo ERROR: Database not found!
    echo ===================================================
    echo.
    echo Please run the batch embedding script first:
    echo   python Script/Indexing/batch_embedding.py
    echo.
    pause
    exit /b 1
)

REM Start Streamlit
echo.
echo ===================================================
echo Starting QCDT Chatbot...
echo ===================================================
echo.
echo Browser should open automatically at:
echo http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo.

python -m streamlit run App/chatbot_app.py

pause
