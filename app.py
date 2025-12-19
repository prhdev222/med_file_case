from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager
from models import db, AdminUser
from routes import register_blueprints
import os
from datetime import datetime, timezone
from dotenv import load_dotenv
from services import BackupSystem, start_scheduled_backup, run_backup_now

def generate_safe_filename(original_filename, custom_filename=None, first_name=None, last_name=None):
    """สร้างชื่อไฟล์ที่ปลอดภัย"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    _, ext = os.path.splitext(original_filename)
    
    if custom_filename:
        # ใช้ชื่อไฟล์ที่ผู้ใช้กำหนด
        safe_custom_name = "".join(c for c in custom_filename if c.isalnum() or c in ('_', '-', ' '))
        safe_custom_name = safe_custom_name.replace(' ', '_')
        return f"{safe_custom_name}_{timestamp}{ext}"
    else:
        # ใช้ชื่อไฟล์เดิมหรือสร้างใหม่
        if any(ord(char) > 127 for char in original_filename):
            # ชื่อไฟล์ภาษาไทย - ใช้ข้อมูลผู้ป่วย
            if first_name and last_name:
                new_filename = f"{first_name}_{last_name}_{timestamp}{ext}"
                return "".join(c for c in new_filename if c.isalnum() or c in ('_', '-', '.'))
            else:
                return f"file_{timestamp}{ext}"
        else:
            # ชื่อไฟล์ภาษาอังกฤษ
            from werkzeug.utils import secure_filename
            safe_filename = secure_filename(original_filename)
            name, _ = os.path.splitext(safe_filename)
            return f"{name}_{timestamp}{ext}"

# Load environment variables
load_dotenv()

# แก้ไขปัญหา encoding สำหรับ console output บน Windows
import sys
if sys.platform == 'win32':
    import codecs
    # ตั้งค่า encoding สำหรับ stdout และ stderr
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    if hasattr(sys.stderr, 'buffer'):
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

app = Flask(__name__)

# Enable CORS for all routes
# ตั้งค่า CORS จาก environment variable หรือใช้ค่า default
cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:5174').split(',')
CORS(app, origins=cors_origins, supports_credentials=True)

# Configuration from environment variables
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///hospital.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'storage/uploads')
# เพิ่มการจำกัดขนาดไฟล์
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 50 * 1024 * 1024))  # 50MB
app.config['MAX_FILE_SIZE'] = int(os.getenv('MAX_FILE_SIZE', 25 * 1024 * 1024))  # 25MB per file

# สร้างโฟลเดอร์ storage ถ้ายังไม่มี (เฉพาะ local)
# ใน serverless ใช้ external storage (Supabase Storage)
try:
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'guidelines'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'images'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'cases'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'temp'), exist_ok=True)
except (OSError, PermissionError) as e:
    # ใน serverless อาจไม่สามารถสร้าง directory ได้ - ไม่เป็นไร
    print(f"Warning: Could not create upload directories: {e}")

# Initialize database with app
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin.admin_login'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(AdminUser, int(user_id))

# Register all blueprints
register_blueprints(app)

# ตรวจสอบว่า run บน serverless platform (ต้องตรวจสอบก่อน)
IS_VERCEL = os.getenv('VERCEL') == '1'
IS_NETLIFY = os.getenv('NETLIFY') == 'true'
IS_SERVERLESS = IS_VERCEL or IS_NETLIFY

# Debug: Print all registered routes (เฉพาะ local)
if not IS_SERVERLESS:
    with app.app_context():
        print("\n=== Registered Routes ===")
        for rule in app.url_map.iter_rules():
            print(f"{rule.methods} {rule.rule} -> {rule.endpoint}")
        print("========================\n")

# Initialize database tables (เฉพาะเมื่อ run local)
# ใน serverless จะ initialize เมื่อ function ถูกเรียกครั้งแรก
if not IS_SERVERLESS:
    with app.app_context():
        try:
            db.create_all()
            print("เริ่มต้นฐานข้อมูลเรียบร้อยแล้ว")
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการเริ่มต้นฐานข้อมูล: {e}")

# Initialize backup system
def init_backup_system():
    """เริ่มต้นระบบสำรองข้อมูล"""
    try:
        # เริ่มระบบสำรองข้อมูลอัตโนมัติ (ฟังก์ชันจะสร้าง BackupSystem instance เอง)
        backup_system_instance = start_scheduled_backup()
        
        # ทำความสะอาดไฟล์สำรองเก่า
        backup_system_instance.cleanup_old_backups(keep_days=30)
        
        print("เริ่มระบบสำรองข้อมูลอัตโนมัติทุก 168 ชั่วโมง")
        return backup_system_instance
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการเริ่มระบบสำรองข้อมูล: {e}")
        return None

def init_db():
    """เริ่มต้นฐานข้อมูล"""
    with app.app_context():
        try:
            db.create_all()
            print("เริ่มต้นฐานข้อมูลเรียบร้อยแล้ว")
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการเริ่มต้นฐานข้อมูล: {e}")

if IS_SERVERLESS:
    # ปรับ settings สำหรับ serverless
    app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB (serverless limit)
    # ปิด backup system (ไม่ทำงานใน serverless)
    print("Running on serverless platform (Vercel/Netlify)")
    
    # Initialize database tables เมื่อ function ถูกเรียกครั้งแรก (lazy initialization)
    _db_initialized = False
    _db_init_error = None
    
    @app.before_request
    def ensure_db_initialized():
        global _db_initialized, _db_init_error
        if not _db_initialized and _db_init_error is None:
            try:
                with app.app_context():
                    # Test database connection first
                    db.session.execute(db.text('SELECT 1'))
                    db.session.commit()
                    # Create tables if they don't exist
                    db.create_all()
                    print("Database tables initialized successfully")
                _db_initialized = True
            except Exception as e:
                _db_init_error = str(e)
                print(f"Error initializing database: {e}")
                import traceback
                traceback.print_exc()
                # Don't fail the request, but log the error
                # The route handlers will handle database errors gracefully

if __name__ == '__main__':
    init_db()
    
    # เริ่มระบบสำรองข้อมูลอัตโนมัติ (เฉพาะ local)
    if not IS_SERVERLESS:
        backup_system = init_backup_system()
    
    # ใช้ environment variables สำหรับ host และ port
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'True').lower() == 'true'
    
    app.run(host=host, port=port, debug=debug)
