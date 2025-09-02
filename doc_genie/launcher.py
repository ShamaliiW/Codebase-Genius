#!/usr/bin/env python3
"""
GitHub Codebase Analyzer Launcher
=================================

Python launcher script for the Jac-based GitHub codebase analyzer.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def check_jaseci_installation():
    """Check if dependencies are properly installed"""
    try:
        # Check if our analyzer can run
        result = subprocess.run([sys.executable, 'analyzer.py', '--help'], 
                              capture_output=True, text=True, timeout=10)
        
        # Check if help output contains expected content
        if result.returncode == 0 and 'GitHub Codebase Analyzer' in result.stdout:
            print(f"GitHub Codebase Analyzer ready")
            return True
        else:
            print("❌ Analyzer not working properly")
            print(f"Return code: {result.returncode}")
            if result.stderr:
                print(f"Error output: {result.stderr}")
            return False
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        print(f"❌ Python analyzer check failed: {e}")
        return False

def install_dependencies():
    """Install required Python dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def run_analyzer(github_url=None, config_file=None):
    """Run the GitHub codebase analyzer"""
    
    print("🚀 Starting GitHub Codebase Analyzer...")
    
    try:
        # Use the pure Python implementation
        cmd = [sys.executable, 'analyzer.py', '--url', github_url or 'https://github.com/DinalieLiyanage/geveoFinal']
        
        # Add token if available
        github_token = os.getenv("GITHUB_TOKEN")
        if github_token:
            cmd.extend(['--token', github_token])
        
        # Add output directory
        cmd.extend(['--output', 'output'])
        
        result = subprocess.run(cmd, check=True)
        print("✅ Analysis completed successfully!")
        print("📁 Check the 'output' directory for generated documentation")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Analysis failed: {e}")
        return False

def run_tests():
    """Run the test suite"""
    print("🧪 Running test suite...")
    
    try:
        # Run basic functionality test
        result = subprocess.run([sys.executable, 'analyzer.py', '--url', 'https://github.com/octocat/Hello-World'], check=True)
        print("✅ Tests completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Tests failed: {e}")
        return False

def main():
    """Main launcher function"""
    parser = argparse.ArgumentParser(description='GitHub Codebase Analyzer')
    parser.add_argument('--url', help='GitHub repository URL to analyze')
    parser.add_argument('--config', help='Path to configuration file')
    parser.add_argument('--test', action='store_true', help='Run test suite')
    parser.add_argument('--install-deps', action='store_true', help='Install dependencies')
    parser.add_argument('--check', action='store_true', help='Check installation')
    
    args = parser.parse_args()
    
    print("GitHub Codebase Analyzer")
    print("========================")
    
    # Check installation
    if args.check or not check_jaseci_installation():
        if not check_jaseci_installation():
            print("\n🔧 To install dependencies:")
            print("   pip install -r requirements.txt")
            return False
    
    # Install dependencies
    if args.install_deps:
        if not install_dependencies():
            return False
    
    # Run tests
    if args.test:
        return run_tests()
    
    # Run analyzer
    return run_analyzer(args.url, args.config)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
