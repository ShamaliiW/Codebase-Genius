@echo off
REM GitHub Codebase Analyzer - Windows Batch Script
REM ================================================

echo GitHub Codebase Analyzer
echo ========================

REM Check if URL parameter is provided
if "%1"=="" (
    echo Usage: analyze.bat "https://github.com/owner/repo"
    echo Example: analyze.bat "https://github.com/microsoft/vscode"
    pause
    exit /b 1
)

REM Set the repository URL
set REPO_URL=%1

REM Check for Python virtual environment
if exist ".venv\Scripts\python.exe" (
    set PYTHON_EXE=.venv\Scripts\python.exe
    echo Using virtual environment Python
) else (
    set PYTHON_EXE=python
    echo Using system Python
)

REM Check for GitHub token
if defined GITHUB_TOKEN (
    echo Using GitHub token for enhanced rate limits
    %PYTHON_EXE% analyzer.py --url %REPO_URL% --token %GITHUB_TOKEN%
) else (
    echo Warning: No GITHUB_TOKEN environment variable found
    echo You may encounter rate limiting. Set GITHUB_TOKEN for better performance.
    %PYTHON_EXE% analyzer.py --url %REPO_URL%
)

REM Check if analysis was successful
if %errorlevel% equ 0 (
    echo.
    echo ✅ Analysis completed successfully!
    echo 📁 Check the 'output' directory for results
    echo.
    echo Generated files:
    if exist "output\README.md" echo    - README.md
    if exist "output\analysis" echo    - Technology and dependency analysis
    if exist "output\uml" echo    - UML diagrams
    if exist "output\api" echo    - API documentation
    if exist "output\architecture" echo    - Architecture documentation
    echo.
) else (
    echo ❌ Analysis failed. Check the error messages above.
)

pause
