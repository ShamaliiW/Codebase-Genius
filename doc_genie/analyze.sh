#!/bin/bash
# GitHub Codebase Analyzer - Shell Script
# ========================================

echo "GitHub Codebase Analyzer"
echo "========================"

# Check if URL parameter is provided
if [ $# -eq 0 ]; then
    echo "Usage: ./analyze.sh \"https://github.com/owner/repo\""
    echo "Example: ./analyze.sh \"https://github.com/microsoft/vscode\""
    exit 1
fi

REPO_URL="$1"

# Check for Python virtual environment
if [ -f ".venv/bin/python" ]; then
    PYTHON_EXE=".venv/bin/python"
    echo "Using virtual environment Python"
elif [ -f "venv/bin/python" ]; then
    PYTHON_EXE="venv/bin/python"
    echo "Using virtual environment Python"
else
    PYTHON_EXE="python3"
    echo "Using system Python"
fi

# Check for GitHub token
if [ -n "$GITHUB_TOKEN" ]; then
    echo "Using GitHub token for enhanced rate limits"
    $PYTHON_EXE analyzer.py --url "$REPO_URL" --token "$GITHUB_TOKEN"
else
    echo "Warning: No GITHUB_TOKEN environment variable found"
    echo "You may encounter rate limiting. Set GITHUB_TOKEN for better performance."
    $PYTHON_EXE analyzer.py --url "$REPO_URL"
fi

# Check if analysis was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Analysis completed successfully!"
    echo "📁 Check the 'output' directory for results"
    echo ""
    echo "Generated files:"
    [ -f "output/README.md" ] && echo "   - README.md"
    [ -d "output/analysis" ] && echo "   - Technology and dependency analysis"
    [ -d "output/uml" ] && echo "   - UML diagrams"
    [ -d "output/api" ] && echo "   - API documentation"
    [ -d "output/architecture" ] && echo "   - Architecture documentation"
    echo ""
else
    echo "❌ Analysis failed. Check the error messages above."
fi
