"""
🚀 AI Finance Advisor Launcher
Clean, error-free launcher with proper virtual environment handling
"""

import subprocess
import sys
import os
from pathlib import Path

def run_chainlit():
    """Run the AI Finance Advisor Chainlit application"""
    try:
        # Change to the correct directory
        os.chdir(os.path.dirname(os.path.abspath(__file__)))

        # Check for virtual environment
        venv_path = Path("venv")
        if venv_path.exists():
            # Determine Python executable path based on OS
            python_exe = venv_path / ("Scripts/python.exe" if os.name == 'nt' else "bin/python")

            if python_exe.exists():
                print("🎯 Using virtual environment Python")
                python_cmd = str(python_exe)
            else:
                print("⚠️ Virtual environment found but Python not found, using system Python")
                python_cmd = sys.executable
        else:
            print("⚠️ No virtual environment found, using system Python")
            python_cmd = sys.executable

        # Run Chainlit app on localhost only (security best practice)
        cmd = [
            python_cmd, "-m", "chainlit", "run", "main_app.py",
            "--port", "8509", "--host", "127.0.0.1"
        ]

        print("🚀 Starting AI Finance Advisor...")
        print("🎯 Features: Stock Analysis, Portfolio Optimization, Risk Assessment")
        print(f"🔧 Command: {' '.join(cmd)}")
        print("🌐 URL: http://localhost:8509")
        print("=" * 60)

        # Run the command
        result = subprocess.run(cmd, capture_output=False, text=True)

        if result.returncode != 0:
            print(f"❌ Error running Chainlit: {result.returncode}")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Set up virtual environment: python setup_venv.py")
        print("2. Install dependencies: pip install chainlit pandas numpy plotly yfinance")
        print("3. Try running directly: python -m chainlit run main_app.py")
        print("4. Check if port 8509 is available")

if __name__ == "__main__":
    run_chainlit()
