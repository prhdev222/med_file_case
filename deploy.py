#!/usr/bin/env python3
"""
Deployment script for Hospital Administration System
"""

import os
import subprocess
import sys
from pathlib import Path

def check_environment():
    """Check if environment is ready for deployment"""
    print("Checking deployment environment...")
    
    # Check if virtual environment is activated
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Warning: Virtual environment not detected")
        print("   It's recommended to use a virtual environment for deployment")
    
    # Check required files
    required_files = [
        "app.py",
        "requirements.txt",
        ".env"
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        return False
    
    print("✅ Environment check passed")
    return True

def setup_production_config():
    """Setup production configuration"""
    print("Setting up production configuration...")
    
    env_file = Path(".env")
    if not env_file.exists():
        print("Creating .env file...")
        with open(env_file, "w") as f:
            f.write("# Production Environment Configuration\n")
            f.write("FLASK_ENV=production\n")
            f.write("SECRET_KEY=your-secret-key-here\n")
            f.write("JWT_SECRET_KEY=your-jwt-secret-key-here\n")
            f.write("DATABASE_URL=sqlite:///hospital_admin.db\n")
            f.write("CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000\n")
        
        print("⚠️  Please update .env file with your production values!")
        return False
    
    print("✅ Production configuration ready")
    return True

def install_production_server():
    """Install production WSGI server"""
    print("Installing production server (Gunicorn)...")
    
    result = subprocess.run(["pip", "install", "gunicorn"], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Failed to install Gunicorn: {result.stderr}")
        return False
    
    print("✅ Gunicorn installed successfully")
    return True

def create_wsgi_file():
    """Create WSGI entry point"""
    print("Creating WSGI entry point...")
    
    wsgi_content = '''#!/usr/bin/env python3
"""
WSGI entry point for Hospital Administration System
"""

from app import app

if __name__ == "__main__":
    app.run()
'''
    
    with open("wsgi.py", "w") as f:
        f.write(wsgi_content)
    
    print("✅ WSGI file created")
    return True

def create_systemd_service():
    """Create systemd service file template"""
    print("Creating systemd service template...")
    
    service_content = '''[Unit]
Description=Hospital Administration System
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/your/app
Environment="PATH=/path/to/your/app/venv/bin"
ExecStart=/path/to/your/app/venv/bin/gunicorn --workers 3 --bind unix:hospital-admin.sock -m 007 wsgi:app
Restart=always

[Install]
WantedBy=multi-user.target
'''
    
    with open("hospital-admin.service", "w") as f:
        f.write(service_content)
    
    print("✅ Systemd service template created")
    print("   Please update paths in hospital-admin.service before deployment")
    return True

def create_nginx_config():
    """Create Nginx configuration template"""
    print("Creating Nginx configuration template...")
    
    nginx_content = '''server {
    listen 80;
    server_name your-domain.com;

    location / {
        include proxy_params;
        proxy_pass http://unix:/path/to/your/app/hospital-admin.sock;
    }

    location /static {
        alias /path/to/your/app/static;
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
}
'''
    
    with open("nginx-hospital-admin", "w") as f:
        f.write(nginx_content)
    
    print("✅ Nginx configuration template created")
    print("   Please update paths and domain in nginx-hospital-admin before deployment")
    return True

def main():
    """Main deployment setup process"""
    print("Hospital Administration System - Deployment Setup")
    print("=" * 50)
    
    if not check_environment():
        print("\n❌ Environment check failed. Please fix issues before deployment.")
        return
    
    if not setup_production_config():
        print("\n❌ Please configure .env file before proceeding.")
        return
    
    if not install_production_server():
        print("\n❌ Failed to install production server.")
        return
    
    create_wsgi_file()
    create_systemd_service()
    create_nginx_config()
    
    print("\n✅ Deployment setup completed!")
    print("\nNext steps for production deployment:")
    print("1. Update .env file with production values")
    print("2. Update paths in hospital-admin.service")
    print("3. Update domain and paths in nginx-hospital-admin")
    print("4. Copy hospital-admin.service to /etc/systemd/system/")
    print("5. Copy nginx-hospital-admin to /etc/nginx/sites-available/")
    print("6. Enable and start the service")
    print("\nFor development, you can run:")
    print("  python app.py")
    print("\nFor production testing, you can run:")
    print("  gunicorn --workers 3 --bind 0.0.0.0:8000 wsgi:app")

if __name__ == "__main__":
    main()