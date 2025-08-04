@echo off
echo Starting Gmail AI Summarizer...
echo.
echo Make sure you have:
echo 1. Python installed
echo 2. Dependencies installed (pip install -r requirements.txt)
echo 3. credentials.json file in this directory
echo 4. .env file with your OpenAI API key
echo.
pause
streamlit run gmail_ai_summarizer.py
pause 