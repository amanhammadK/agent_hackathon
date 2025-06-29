"""
Virtual Environment Setup Script
Creates a proper virtual environment and installs all dependencies
"""

import subprocess
import sys
import os
from pathlib import Path

def setup_virtual_environment():
    """Set up virtual environment and install dependencies"""
    
    print("🚀 Setting up Virtual Environment for AI Finance Advisor")
    print("=" * 60)
    
    # Create virtual environment
    venv_path = Path("venv")
    if not venv_path.exists():
        print("📦 Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Virtual environment created!")
    else:
        print("✅ Virtual environment already exists!")
    
    # Determine the correct python executable path
    if os.name == 'nt':  # Windows
        python_exe = venv_path / "Scripts" / "python.exe"
        pip_exe = venv_path / "Scripts" / "pip.exe"
    else:  # Unix/Linux/Mac
        python_exe = venv_path / "bin" / "python"
        pip_exe = venv_path / "bin" / "pip"
    
    # Upgrade pip
    print("📦 Upgrading pip...")
    subprocess.run([str(pip_exe), "install", "--upgrade", "pip"], check=True)
    
    # Install requirements
    print("📦 Installing dependencies...")
    subprocess.run([str(pip_exe), "install", "-r", "requirements_agent.txt"], check=True)
    
    # Install additional advanced packages
    advanced_packages = [
        "plotly-dash",
        "streamlit-aggrid", 
        "streamlit-option-menu",
        "langchain",
        "faiss-cpu",
        "sentence-transformers",
        "transformers",
        "torch",
        "scikit-learn",
        "ta-lib",
        "alpha-vantage",
        "newsapi-python",
        "tweepy",
        "beautifulsoup4",
        "selenium",
        "redis",
        "celery",
        "fastapi",
        "uvicorn",
        "websockets"
    ]
    
    print("🚀 Installing advanced AI packages...")
    for package in advanced_packages:
        try:
            subprocess.run([str(pip_exe), "install", package], check=True, capture_output=True)
            print(f"✅ Installed {package}")
        except subprocess.CalledProcessError:
            print(f"⚠️ Failed to install {package} (optional)")
    
    print("\n🎉 Virtual environment setup complete!")
    print(f"🐍 Python executable: {python_exe}")
    print(f"📦 Pip executable: {pip_exe}")
    
    # Create activation script
    if os.name == 'nt':  # Windows
        activate_script = """
@echo off
echo 🚀 Activating AI Finance Advisor Virtual Environment...
call venv\\Scripts\\activate.bat
echo ✅ Virtual environment activated!
echo 🎯 Run: python run_advanced_chainlit.py
cmd /k
        """
        with open("activate_venv.bat", "w") as f:
            f.write(activate_script)
        print("💻 Created activate_venv.bat for Windows")
    else:
        activate_script = """#!/bin/bash
echo "🚀 Activating AI Finance Advisor Virtual Environment..."
source venv/bin/activate
echo "✅ Virtual environment activated!"
echo "🎯 Run: python run_advanced_chainlit.py"
bash
        """
        with open("activate_venv.sh", "w") as f:
            f.write(activate_script)
        os.chmod("activate_venv.sh", 0o755)
        print("💻 Created activate_venv.sh for Unix/Linux/Mac")
    
    return str(python_exe)

if __name__ == "__main__":
    try:
        python_path = setup_virtual_environment()
        print(f"\n🎯 Next steps:")
        print(f"1. Activate virtual environment")
        print(f"2. Run: {python_path} run_advanced_chainlit.py")
        print(f"3. Open: http://localhost:8505")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
