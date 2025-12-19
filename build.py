#!/usr/bin/env python3
"""
Build script for Hospital Administration System
"""

import os
import subprocess
import shutil
from pathlib import Path

def build_frontend():
    """Build Vue.js frontend"""
    print("Building Vue.js frontend...")
    frontend_dir = Path("frontend")
    
    if not frontend_dir.exists():
        print("Frontend directory not found!")
        return False
    
    # Install dependencies
    result = subprocess.run(["npm", "install"], cwd=frontend_dir, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"npm install failed: {result.stderr}")
        return False
    
    # Build frontend
    result = subprocess.run(["npm", "run", "build"], cwd=frontend_dir, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"npm build failed: {result.stderr}")
        return False
    
    print("Frontend build completed successfully!")
    return True

def setup_static_files():
    """Copy built frontend files to Flask static directory"""
    print("Setting up static files...")
    
    frontend_dist = Path("frontend/dist")
    static_dir = Path("static")
    templates_dir = Path("templates")
    
    if not frontend_dist.exists():
        print("Frontend dist directory not found! Please build frontend first.")
        return False
    
    # Create directories if they don't exist
    static_dir.mkdir(exist_ok=True)
    templates_dir.mkdir(exist_ok=True)
    
    # Copy static assets
    if (frontend_dist / "assets").exists():
        if (static_dir / "assets").exists():
            shutil.rmtree(static_dir / "assets")
        shutil.copytree(frontend_dist / "assets", static_dir / "assets")
    
    # Copy index.html to templates
    if (frontend_dist / "index.html").exists():
        shutil.copy2(frontend_dist / "index.html", templates_dir / "index.html")
    
    print("Static files setup completed!")
    return True

def install_python_dependencies():
    """Install Python dependencies"""
    print("Installing Python dependencies...")
    
    result = subprocess.run(["pip", "install", "-r", "requirements.txt"], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"pip install failed: {result.stderr}")
        return False
    
    print("Python dependencies installed successfully!")
    return True

def main():
    """Main build process"""
    print("Starting Hospital Administration System build process...")
    
    # Install Python dependencies
    if not install_python_dependencies():
        print("Build failed: Python dependencies installation failed")
        return
    
    # Build frontend
    if not build_frontend():
        print("Build failed: Frontend build failed")
        return
    
    # Setup static files
    if not setup_static_files():
        print("Build failed: Static files setup failed")
        return
    
    print("\n✅ Build completed successfully!")
    print("\nTo run the application:")
    print("  python app.py")
    print("\nThe application will be available at:")
    print("  http://localhost:5000")

if __name__ == "__main__":
    main()