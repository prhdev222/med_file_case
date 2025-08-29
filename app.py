from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify, abort, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
import shutil
import sqlite3
import threading
import logging
from datetime import datetime, timezone, timedelta
import mimetypes
from dotenv import load_dotenv
from backup_system import BackupSystem, start_scheduled_backup, run_backup_now

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
            safe_filename = secure_filename(original_filename)
            name, _ = os.path.splitext(safe_filename)
            return f"{name}_{timestamp}{ext}"

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configuration from environment variables
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///hospital.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'storage/uploads')
# เพิ่มการจำกัดขนาดไฟล์
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 50 * 1024 * 1024))  # 50MB
app.config['MAX_FILE_SIZE'] = int(os.getenv('MAX_FILE_SIZE', 25 * 1024 * 1024))  # 25MB per file

# สร้างโฟลเดอร์ storage ถ้ายังไม่มี
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'guidelines'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'images'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'cases'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'temp'), exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'

# Models
class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(10), nullable=False, unique=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class Guideline(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    file_path = db.Column(db.String(500))  # เปลี่ยนเป็น nullable=True
    file_size = db.Column(db.Integer)
    upload_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    description = db.Column(db.Text)
    external_link = db.Column(db.String(500))  # เพิ่มฟิลด์สำหรับ external link
    link_type = db.Column(db.String(50))  # ประเภทลิงก์ เช่น Google Drive, OneDrive, Website
    department = db.relationship('Department', backref=db.backref('guidelines', lazy=True))

class Knowledge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text)  # จำกัดความยาว 500 ตัวอักษร
    image_path = db.Column(db.String(500))  # เพิ่มฟิลด์สำหรับรูปภาพ
    external_link = db.Column(db.String(500))  # เพิ่มฟิลด์สำหรับลิงก์ภายนอก
    link_type = db.Column(db.String(50))  # ประเภทลิงก์
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    department = db.relationship('Department', backref=db.backref('knowledge', lazy=True))

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)  # จำกัดความยาว 300 ตัวอักษร
    image_path = db.Column(db.String(500))  # เพิ่มฟิลด์สำหรับรูปภาพ
    external_link = db.Column(db.String(500))  # เพิ่มฟิลด์สำหรับลิงก์ภายนอก
    link_type = db.Column(db.String(50))  # ประเภทลิงก์
    activity_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    department = db.relationship('Department', backref=db.backref('activities', lazy=True))

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    line_id = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    other_contact = db.Column(db.Text)
    department = db.relationship('Department', backref=db.backref('contacts', lazy=True))

class PatientCase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hn = db.Column(db.String(20), nullable=False)  # Hospital Number
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    case_date = db.Column(db.Date, nullable=False)
    notes = db.Column(db.Text)
    # เพิ่มฟิลด์สำหรับเอกสาร
    file_path = db.Column(db.String(500))  # ไฟล์ที่อัปโหลด
    file_size = db.Column(db.Integer)  # ขนาดไฟล์
    external_link = db.Column(db.String(500))  # ลิงก์ภายนอก
    link_type = db.Column(db.String(50))  # ประเภทลิงก์
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    created_by = db.Column(db.Integer, db.ForeignKey('admin_user.id'))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    is_deleted = db.Column(db.Boolean, default=False)
    
    department = db.relationship('Department', backref=db.backref('cases', lazy=True))
    created_by_user = db.relationship('AdminUser', backref=db.backref('created_cases', lazy=True))

class CaseAudit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('patient_case.id'), nullable=False)
    action = db.Column(db.String(20), nullable=False)  # 'CREATE', 'UPDATE', 'DELETE'
    user_id = db.Column(db.Integer, db.ForeignKey('admin_user.id'))
    ip_address = db.Column(db.String(45))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    case = db.relationship('PatientCase', backref=db.backref('audit_logs', lazy=True))
    user = db.relationship('AdminUser', backref=db.backref('case_audits', lazy=True))

class AdminUser(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_login = db.Column(db.DateTime)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(AdminUser, int(user_id))

# Routes
@app.route('/')
def home():
    departments = db.session.query(Department).all()
    return render_template('home.html', departments=departments)

@app.route('/department/<int:dept_id>')
def department(dept_id):
    dept = db.session.get(Department, dept_id)
    if dept is None:
        abort(404)
    return render_template('department.html', department=dept)

@app.route('/download/<int:guideline_id>')
def download_guideline(guideline_id):
    guideline = db.session.get(Guideline, guideline_id)
    if guideline is None:
        abort(404)
    
    # ถ้ามี external link ให้ redirect ไปที่ลิงก์นั้น
    if guideline.external_link:
        return redirect(guideline.external_link)
    
    # ถ้ามีไฟล์ให้ดาวน์โหลด
    if guideline.file_path and os.path.exists(guideline.file_path):
        return send_file(guideline.file_path, as_attachment=True)
    
    flash('ไฟล์ไม่พบ', 'error')
    return redirect(url_for('department', dept_id=guideline.department_id))



@app.route('/stats')
def stats():
    """หน้าแสดงสถิติสาธารณะ"""
    # ดึงข้อมูลสถิติจากฐานข้อมูล
    try:
        # จำนวน cases ทั้งหมด
        total_cases = db.session.query(PatientCase).filter_by(is_deleted=False).count()
        
        # จำนวน cases ตามหน่วยงาน - ใช้วิธีง่ายกว่า
        dept_stats = []
        departments = db.session.query(Department).all()
        
        for dept in departments:
            case_count = db.session.query(PatientCase).filter(
                PatientCase.department_id == dept.id,
                PatientCase.is_deleted == False
            ).count()
            
            if case_count > 0:  # แสดงเฉพาะหน่วยงานที่มี cases
                dept_stats.append({
                    'name': str(dept.name),
                    'case_count': int(case_count)
                })
        
        # Debug: แสดงข้อมูลที่สร้าง
        print(f"Processed dept_stats: {dept_stats}")
        
        # จำนวน cases ตามเดือน (6 เดือนล่าสุด) - ใช้วิธีง่ายกว่า
        from datetime import datetime, timedelta
        six_months_ago = datetime.now() - timedelta(days=180)
        
        monthly_stats = []
        current_date = datetime.now()
        
        # สร้างรายการเดือน 6 เดือนล่าสุด
        for i in range(6):
            month_date = current_date - timedelta(days=30*i)
            month_key = month_date.strftime('%Y-%m')
            
            case_count = db.session.query(PatientCase).filter(
                db.func.strftime('%Y-%m', PatientCase.case_date) == month_key,
                PatientCase.is_deleted == False
            ).count()
            
            if case_count > 0:  # แสดงเฉพาะเดือนที่มี cases
                monthly_stats.append({
                    'month': str(month_key),
                    'case_count': int(case_count)
                })
        
        # เรียงลำดับตามเดือน
        monthly_stats.sort(key=lambda x: x['month'])
        
        # Debug: แสดงข้อมูลที่สร้าง
        print(f"Processed monthly_stats: {monthly_stats}")
        
        # จำนวน cases ที่มีไฟล์แนบ
        cases_with_files = db.session.query(PatientCase).filter(
            PatientCase.file_path.isnot(None),
            PatientCase.is_deleted == False
        ).count()
        
        # จำนวน cases ที่มี external link
        cases_with_links = db.session.query(PatientCase).filter(
            PatientCase.external_link.isnot(None),
            PatientCase.is_deleted == False
        ).count()
        
        stats_data = {
            'total_cases': total_cases,
            'dept_stats': dept_stats,
            'monthly_stats': monthly_stats,
            'cases_with_files': cases_with_files,
            'cases_with_links': cases_with_links
        }
        
        # Debug logging
        print(f"Stats data being sent to template:")
        print(f"  total_cases: {total_cases}")
        print(f"  dept_stats: {dept_stats}")
        print(f"  monthly_stats: {monthly_stats}")
        print(f"  cases_with_files: {cases_with_files}")
        print(f"  cases_with_links: {cases_with_links}")
        
    except Exception as e:
        print(f"Error getting stats: {e}")
        stats_data = {
            'total_cases': 0,
            'dept_stats': [],
            'monthly_stats': [],
            'cases_with_files': 0,
            'cases_with_links': 0
        }
    
    return render_template('stats.html', stats=stats_data)

@app.route('/admin/cases')
@login_required
def admin_cases():
    """หน้าแสดงรายการ cases ทั้งหมด"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    search = request.args.get('search', '')
    department_id = request.args.get('department_id', type=int)
    
    query = db.session.query(PatientCase).join(Department).filter(PatientCase.is_deleted == False)
    
    if search:
        query = query.filter(
            db.or_(
                PatientCase.hn.contains(search),
                PatientCase.first_name.contains(search),
                PatientCase.last_name.contains(search)
            )
        )
    
    if department_id:
        query = query.filter(PatientCase.department_id == department_id)
    
    cases = query.order_by(PatientCase.case_date.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    departments = db.session.query(Department).all()
    return render_template('admin/cases.html', cases=cases, departments=departments, search=search, department_id=department_id)

@app.route('/admin/cases/add', methods=['GET', 'POST'])
@login_required
def admin_add_case():
    """เพิ่ม case ใหม่"""
    if request.method == 'POST':
        hn = request.form['hn']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        department_id = request.form['department_id']
        case_date = request.form['case_date']
        notes = request.form.get('notes', '')
        upload_type = request.form.get('upload_type', 'none')
        
        # ตรวจสอบว่า HN ซ้ำในวันเดียวกันหรือไม่
        existing_case = db.session.query(PatientCase).filter_by(
            hn=hn, case_date=case_date, is_deleted=False
        ).first()
        
        if existing_case:
            flash('HN นี้มีในระบบแล้วในวันที่เลือก', 'error')
        else:
            case = PatientCase(
                hn=hn,
                first_name=first_name,
                last_name=last_name,
                department_id=department_id,
                case_date=datetime.strptime(case_date, '%Y-%m-%d').date(),
                notes=notes,
                created_by=current_user.id
            )
            
            # จัดการไฟล์หรือลิงก์
            if upload_type == 'file':
                file = request.files['file']
                if file and file.filename:
                    print(f"กำลังอัปโหลดไฟล์: {file.filename}")
                    
                    # ตรวจสอบขนาดไฟล์
                    file.seek(0, 2)
                    file_size = file.tell()
                    file.seek(0)
                    
                    print(f"ขนาดไฟล์: {file_size} bytes")
                    
                    if file_size > app.config['MAX_FILE_SIZE']:
                        flash(f'ไฟล์มีขนาดใหญ่เกินไป (สูงสุด {app.config["MAX_FILE_SIZE"] // (1024*1024)} MB)', 'error')
                        return redirect(url_for('admin_add_case'))
                    
                    # สร้างโฟลเดอร์ใหม่ตามหน่วยงาน
                    dept = db.session.get(Department, department_id)
                    dept_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'cases', dept.code.lower())
                    os.makedirs(dept_folder, exist_ok=True)
                    
                    print(f"โฟลเดอร์ปลายทาง: {dept_folder}")
                    
                    # จัดการชื่อไฟล์
                    original_filename = file.filename
                    custom_filename = request.form.get('custom_filename', '').strip()
                    print(f"ชื่อไฟล์ต้นฉบับ: {original_filename}")
                    print(f"ชื่อไฟล์ที่ต้องการ: {custom_filename}")
                    
                    # สร้างชื่อไฟล์ใหม่
                    new_filename = generate_safe_filename(
                        original_filename, 
                        custom_filename, 
                        first_name, 
                        last_name
                    )
                    print(f"ชื่อไฟล์ใหม่: {new_filename}")
                    
                    file_path = os.path.join(dept_folder, new_filename)
                    
                    print(f"บันทึกไฟล์ที่: {file_path}")
                    
                    try:
                        # บันทึกไฟล์
                        file.save(file_path)
                        
                        # ตรวจสอบว่าไฟล์ถูกบันทึกจริง
                        if os.path.exists(file_path):
                            actual_size = os.path.getsize(file_path)
                            print(f"ไฟล์ถูกบันทึกสำเร็จ ขนาดจริง: {actual_size} bytes")
                            
                            # อัปเดตข้อมูลในฐานข้อมูล
                            case.file_path = file_path
                            case.file_size = actual_size
                            case.external_link = None
                            case.link_type = None
                            
                            flash(f'อัปโหลดไฟล์สำเร็จ: {new_filename}', 'success')
                        else:
                            print("ไฟล์ไม่ถูกบันทึก!")
                            flash('เกิดข้อผิดพลาดในการบันทึกไฟล์', 'error')
                            return redirect(url_for('admin_add_case'))
                            
                    except Exception as e:
                        print(f"เกิดข้อผิดพลาดในการบันทึกไฟล์: {e}")
                        flash(f'เกิดข้อผิดพลาดในการบันทึกไฟล์: {str(e)}', 'error')
                        return redirect(url_for('admin_add_case'))
                        
            elif upload_type == 'link':
                external_link = request.form['external_link']
                link_type = request.form['link_type']
                
                if external_link and link_type:
                    case.external_link = external_link
                    case.link_type = link_type
                    case.file_path = None
                    case.file_size = None
                    
                    flash('เพิ่มลิงก์ภายนอกสำเร็จ', 'success')
                else:
                    flash('กรุณากรอกลิงก์และเลือกประเภทลิงก์', 'error')
                    return redirect(url_for('admin_add_case'))
            
            db.session.add(case)
            db.session.commit()  # Commit case ก่อนเพื่อให้ได้ ID
            
            try:
                # บันทึก audit log หลังจาก commit case แล้ว
                audit = CaseAudit(
                    case_id=case.id,  # ตอนนี้ case.id จะมีค่าแล้ว
                    action='CREATE',
                    user_id=current_user.id,
                    ip_address=request.remote_addr
                )
                db.session.add(audit)
                db.session.commit()  # Commit audit log
                
                # สร้างข้อความแจ้งเตือนที่มีรายละเอียด
                dept = db.session.get(Department, department_id)
                success_message = f'✅ เพิ่มผู้ป่วยสำเร็จ: {first_name} {last_name} (HN: {hn}) - {dept.name}'
                flash(success_message, 'success')
                return redirect(url_for('admin_cases'))
            except Exception as e:
                # หากเกิดข้อผิดพลาดในการสร้าง audit log ให้ rollback และลบไฟล์ที่อัปโหลด
                db.session.rollback()
                if upload_type == 'file' and case.file_path and os.path.exists(case.file_path):
                    os.remove(case.file_path)
                flash(f'เกิดข้อผิดพลาดในการบันทึกข้อมูล: {str(e)}', 'error')
                return redirect(url_for('admin_add_case'))
    
    departments = db.session.query(Department).all()
    return render_template('admin/add_case.html', departments=departments, config=app.config)

@app.route('/admin/cases/edit/<int:case_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_case(case_id):
    """แก้ไข case"""
    case = db.session.get(PatientCase, case_id)
    if case is None or case.is_deleted:
        abort(404)
    
    if request.method == 'POST':
        hn = request.form['hn']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        department_id = request.form['department_id']
        case_date = request.form['case_date']
        notes = request.form.get('notes', '')
        upload_type = request.form.get('upload_type', 'none')
        
        # ตรวจสอบ HN ซ้ำ (ยกเว้นตัวเอง)
        existing_case = db.session.query(PatientCase).filter(
            db.and_(
                PatientCase.hn == hn,
                PatientCase.case_date == datetime.strptime(case_date, '%Y-%m-%d').date(),
                PatientCase.id != case_id,
                PatientCase.is_deleted == False
            )
        ).first()
        
        if existing_case:
            flash('HN นี้มีในระบบแล้วในวันที่เลือก', 'error')
        else:
            case.hn = hn
            case.first_name = first_name
            case.last_name = last_name
            case.department_id = department_id
            case.case_date = datetime.strptime(case_date, '%Y-%m-%d').date()
            case.notes = notes
            case.updated_at = datetime.now(timezone.utc)
            
            # จัดการไฟล์หรือลิงก์
            if upload_type == 'file':
                file = request.files['file']
                if file and file.filename:
                    print(f"กำลังอัปโหลดไฟล์: {file.filename}")
                    
                    # ตรวจสอบขนาดไฟล์
                    file.seek(0, 2)
                    file_size = file.tell()
                    file.seek(0)
                    
                    print(f"ขนาดไฟล์: {file_size} bytes")
                    
                    if file_size > app.config['MAX_FILE_SIZE']:
                        flash(f'ไฟล์มีขนาดใหญ่เกินไป (สูงสุด {app.config["MAX_FILE_SIZE"] // (1024*1024)} MB)', 'error')
                        return redirect(url_for('admin_edit_case', case_id=case_id))
                    
                    # ลบไฟล์เก่าถ้ามี
                    if case.file_path and os.path.exists(case.file_path):
                        try:
                            os.remove(case.file_path)
                            print(f"ลบไฟล์เก่า: {case.file_path}")
                        except Exception as e:
                            print(f"ไม่สามารถลบไฟล์เก่าได้: {e}")
                    
                    # สร้างโฟลเดอร์ใหม่ตามหน่วยงาน
                    dept = db.session.get(Department, department_id)
                    dept_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'cases', dept.code.lower())
                    os.makedirs(dept_folder, exist_ok=True)
                    
                    print(f"โฟลเดอร์ปลายทาง: {dept_folder}")
                    
                    # จัดการชื่อไฟล์
                    original_filename = file.filename
                    custom_filename = request.form.get('custom_filename', '').strip()
                    print(f"ชื่อไฟล์ต้นฉบับ: {original_filename}")
                    print(f"ชื่อไฟล์ที่ต้องการ: {custom_filename}")
                    
                    # สร้างชื่อไฟล์ใหม่
                    new_filename = generate_safe_filename(
                        original_filename, 
                        custom_filename, 
                        first_name, 
                        last_name
                    )
                    print(f"ชื่อไฟล์ใหม่: {new_filename}")
                    
                    file_path = os.path.join(dept_folder, new_filename)
                    
                    print(f"บันทึกไฟล์ที่: {file_path}")
                    
                    try:
                        # บันทึกไฟล์
                        file.save(file_path)
                        
                        # ตรวจสอบว่าไฟล์ถูกบันทึกจริง
                        if os.path.exists(file_path):
                            actual_size = os.path.getsize(file_path)
                            print(f"ไฟล์ถูกบันทึกสำเร็จ ขนาดจริง: {actual_size} bytes")
                            
                            # อัปเดตข้อมูลในฐานข้อมูล
                            case.file_path = file_path
                            case.file_size = actual_size
                            case.external_link = None
                            case.link_type = None
                            
                            flash(f'อัปโหลดไฟล์สำเร็จ: {new_filename}', 'success')
                        else:
                            print("ไฟล์ไม่ถูกบันทึก!")
                            flash('เกิดข้อผิดพลาดในการบันทึกไฟล์', 'error')
                            return redirect(url_for('admin_edit_case', case_id=case_id))
                            
                    except Exception as e:
                        print(f"เกิดข้อผิดพลาดในการบันทึกไฟล์: {e}")
                        flash(f'เกิดข้อผิดพลาดในการบันทึกไฟล์: {str(e)}', 'error')
                        return redirect(url_for('admin_edit_case', case_id=case_id))
                        
                else:
                    flash('กรุณาเลือกไฟล์เมื่อเลือกแก้ไขไฟล์', 'error')
                    return redirect(url_for('admin_edit_case', case_id=case_id))
                    
            elif upload_type == 'link':
                external_link = request.form['external_link']
                link_type = request.form['link_type']
                
                if external_link and link_type:
                    # ลบไฟล์เก่าถ้ามี
                    if case.file_path and os.path.exists(case.file_path):
                        try:
                            os.remove(case.file_path)
                            print(f"ลบไฟล์เก่า: {case.file_path}")
                        except Exception as e:
                            print(f"ไม่สามารถลบไฟล์เก่าได้: {e}")
                    
                    case.external_link = external_link
                    case.link_type = link_type
                    case.file_path = None
                    case.file_size = None
                    
                    flash('อัปเดตลิงก์ภายนอกสำเร็จ', 'success')
                else:
                    flash('กรุณากรอกลิงก์และเลือกประเภทลิงก์', 'error')
                    return redirect(url_for('admin_edit_case', case_id=case_id))
                    
            elif upload_type == 'none':
                # ลบเอกสารทั้งหมด
                if case.file_path and os.path.exists(case.file_path):
                    try:
                        os.remove(case.file_path)
                        print(f"ลบไฟล์: {case.file_path}")
                    except Exception as e:
                        print(f"ไม่สามารถลบไฟล์ได้: {e}")
                
                case.file_path = None
                case.file_size = None
                case.external_link = None
                case.link_type = None
                
                flash('ลบเอกสารทั้งหมดสำเร็จ', 'success')
            
            # บันทึก audit log
            try:
                audit = CaseAudit(
                    case_id=case.id,
                    action='UPDATE',
                    user_id=current_user.id,
                    ip_address=request.remote_addr
                )
                db.session.add(audit)
            except Exception as e:
                print(f"ไม่สามารถสร้าง audit log ได้: {e}")
            
            try:
                db.session.commit()
                flash('แก้ไขข้อมูลผู้ป่วยสำเร็จ', 'success')
                return redirect(url_for('admin_cases'))
            except Exception as e:
                print(f"เกิดข้อผิดพลาดในการบันทึกฐานข้อมูล: {e}")
                db.session.rollback()
                flash(f'เกิดข้อผิดพลาดในการบันทึก: {str(e)}', 'error')
                return redirect(url_for('admin_edit_case', case_id=case_id))
    
    # GET request - แสดงหน้าแก้ไข
    departments = db.session.query(Department).all()
    return render_template('admin/edit_case.html', case=case, departments=departments)

@app.route('/admin/cases/delete/<int:case_id>', methods=['POST'])
@login_required
def admin_delete_case(case_id):
    """ลบ case"""
    case = db.session.get(PatientCase, case_id)
    if case is None or case.is_deleted:
        abort(404)
    
    case.is_deleted = True
    case.updated_at = datetime.now(timezone.utc)
    
    # บันทึก audit log
    audit = CaseAudit(
        case_id=case.id,
        action='DELETE',
        user_id=current_user.id,
        ip_address=request.remote_addr
    )
    db.session.add(audit)
    
    db.session.commit()
    flash('ลบข้อมูลผู้ป่วยสำเร็จ', 'success')
    return redirect(url_for('admin_cases'))

@app.route('/download/case/<int:case_id>')
def download_case_file(case_id):
    """ดาวน์โหลดไฟล์ของ case"""
    case = db.session.get(PatientCase, case_id)
    if case is None or case.is_deleted or not case.file_path:
        abort(404)
    
    if os.path.exists(case.file_path):
        return send_file(case.file_path, as_attachment=True)
    else:
        flash('ไฟล์ไม่พบ', 'error')
        return redirect(url_for('admin_cases'))

@app.route('/admin/cases/search')
@login_required
def admin_search_cases():
    """ค้นหา cases สำหรับแสดงตัวอย่างก่อน export"""
    # รับพารามิเตอร์จาก query string
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    department_id = request.args.get('department_id')
    
    # สร้าง query
    query = db.session.query(PatientCase).join(Department).filter(PatientCase.is_deleted == False)
    
    # กรองตามวันที่
    if start_date:
        query = query.filter(PatientCase.case_date >= start_date)
    if end_date:
        query = query.filter(PatientCase.case_date <= end_date)
    
    # กรองตามหน่วยงาน
    if department_id:
        query = query.filter(PatientCase.department_id == department_id)
    
    # ดึงข้อมูล (จำกัดจำนวนเพื่อแสดงตัวอย่าง)
    cases = query.limit(10).all()
    
    # แปลงเป็น JSON
    result = []
    for case in cases:
        # ตรวจสอบว่ามีไฟล์หรือ external link
        document_info = ''
        if case.file_path:
            document_info = 'มีไฟล์แนบ'
        elif case.external_link:
            document_info = case.external_link
        
        result.append({
            'id': case.id,
            'hn': case.hn,
            'first_name': case.first_name,
            'last_name': case.last_name,
            'department_name': case.department.name if case.department else 'ไม่ระบุ',
            'case_date': case.case_date.strftime('%d/%m/%Y') if case.case_date else '',
            'notes': case.notes or '',
            'document_info': document_info
        })
    
    return jsonify(result)

@app.route('/admin/cases/export')
@login_required
def admin_export_cases():
    """Export ข้อมูล cases เป็น CSV"""
    from io import StringIO
    import csv
    
    # รับพารามิเตอร์จาก query string
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    department_id = request.args.get('department_id')
    
    # สร้าง query
    query = db.session.query(PatientCase).join(Department).filter(PatientCase.is_deleted == False)
    
    # กรองตามวันที่
    if start_date:
        query = query.filter(PatientCase.case_date >= start_date)
    if end_date:
        query = query.filter(PatientCase.case_date <= end_date)
    
    # กรองตามหน่วยงาน
    if department_id:
        query = query.filter(PatientCase.department_id == department_id)
    
    # ดึงข้อมูล
    cases = query.all()
    
    # สร้าง CSV
    output = StringIO()
    writer = csv.writer(output)
    
    # เขียน header
    writer.writerow(['HN', 'ชื่อ', 'นามสกุล', 'หน่วยงาน', 'วันที่วินิจฉัย', 'หมายเหตุ', 'เอกสาร'])
    
    # เขียนข้อมูล
    for case in cases:
        # ตรวจสอบว่ามีไฟล์หรือ external link
        document_info = ''
        if case.file_path:
            document_info = 'มีไฟล์แนบ'
        elif case.external_link:
            document_info = case.external_link
        
        writer.writerow([
            case.hn,
            case.first_name,
            case.last_name,
            case.department.name,
            case.case_date.strftime('%d/%m/%Y') if case.case_date else '',
            case.notes or '',
            document_info
        ])
    
    # สร้าง response
    output.seek(0)
    csv_data = output.getvalue()
    output.close()
    
    # สร้าง filename
    filename = f"cases_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    # ส่งไฟล์ - ใช้ BytesIO สำหรับ binary data
    from io import BytesIO
    csv_bytes = csv_data.encode('utf-8-sig')  # เพิ่ม BOM สำหรับ Excel
    csv_buffer = BytesIO(csv_bytes)
    
    return send_file(
        csv_buffer,
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename
    )

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = db.session.query(AdminUser).filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            user.last_login = datetime.now(timezone.utc)
            db.session.commit()
            return redirect(url_for('admin_dashboard'))
        else:
            flash('ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง', 'error')
    
    return render_template('admin/login.html')

@app.route('/admin/cases/login', methods=['GET', 'POST'])
def admin_cases_login():
    """หน้า login แยกสำหรับระบบจัดการข้อมูลผู้ป่วย"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = db.session.query(AdminUser).filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            user.last_login = datetime.now(timezone.utc)
            db.session.commit()
            return redirect(url_for('admin_cases'))
        else:
            flash('ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง', 'error')
    
    return render_template('admin/cases_login.html')

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    stats = {
        'departments': db.session.query(Department).count(),
        'guidelines': db.session.query(Guideline).count(),
        'knowledge': db.session.query(Knowledge).count(),
        'activities': db.session.query(Activity).count(),
        'total_cases': db.session.query(PatientCase).filter_by(is_deleted=False).count()
    }
    return render_template('admin/dashboard.html', stats=stats)

@app.route('/api/notifications/recent-patients')
@login_required
def get_recent_patients():
    """API สำหรับดึงข้อมูลผู้ป่วยใหม่ในช่วง 3 วันก่อน"""
    try:
        # คำนวณวันที่ 3 วันก่อน
        three_days_ago = datetime.now(timezone.utc) - timedelta(days=3)
        
        # ดึงข้อมูลผู้ป่วยที่สร้างในช่วง 3 วันก่อน
        recent_patients = db.session.query(PatientCase).join(Department).filter(
            PatientCase.created_at >= three_days_ago,
            PatientCase.is_deleted == False
        ).order_by(PatientCase.created_at.desc()).all()
        
        # แปลงข้อมูลเป็น JSON
        patients_data = []
        for patient in recent_patients:
            patients_data.append({
                'id': patient.id,
                'hn': patient.hn,
                'first_name': patient.first_name,
                'last_name': patient.last_name,
                'department_name': patient.department.name,
                'department_code': patient.department.code,
                'created_at': patient.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'case_date': patient.case_date.strftime('%Y-%m-%d') if patient.case_date else None
            })
        
        return jsonify({
            'success': True,
            'count': len(patients_data),
            'patients': patients_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/notifications/recent-patients-public')
def get_recent_patients_public():
    """API สำหรับผู้ใช้ทั่วไป - แสดงเฉพาะจำนวนและหน่วยงาน ไม่เปิดเผยข้อมูลส่วนตัว"""
    try:
        # คำนวณวันที่ 3 วันก่อน
        three_days_ago = datetime.now(timezone.utc) - timedelta(days=3)
        
        # ดึงข้อมูลจำนวนผู้ป่วยใหม่แยกตามหน่วยงาน
        department_stats = db.session.query(
            Department.name.label('department_name'),
            func.count(PatientCase.id).label('patient_count')
        ).join(
            PatientCase, PatientCase.department_id == Department.id
        ).filter(
            PatientCase.created_at >= three_days_ago,
            PatientCase.is_deleted == False
        ).group_by(
            Department.id, Department.name
        ).order_by(
            func.count(PatientCase.id).desc()
        ).all()
        
        # แปลงข้อมูลเป็น list of dictionaries
        departments_data = []
        total_count = 0
        for dept in department_stats:
            departments_data.append({
                'department_name': dept.department_name,
                'patient_count': dept.patient_count
            })
            total_count += dept.patient_count
        
        return jsonify({
            'success': True,
            'total_count': total_count,
            'departments': departments_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/admin/departments')
@login_required
def admin_departments():
    departments = db.session.query(Department).all()
    return render_template('admin/departments.html', departments=departments)

@app.route('/admin/guidelines')
@login_required
def admin_guidelines():
    guidelines = db.session.query(Guideline).join(Department).all()
    return render_template('admin/guidelines.html', guidelines=guidelines)

@app.route('/admin/guidelines/edit/<int:guideline_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_guideline(guideline_id):
    guideline = db.session.get(Guideline, guideline_id)
    if guideline is None:
        abort(404)
    
    if request.method == 'POST':
        department_id = request.form['department_id']
        title = request.form['title']
        description = request.form['description']
        upload_type = request.form['upload_type']
        
        guideline.department_id = department_id
        guideline.title = title
        guideline.description = description
        
        if upload_type == 'file':
            file = request.files['file']
            if file and file.filename:
                # ตรวจสอบขนาดไฟล์
                file.seek(0, 2)
                file_size = file.tell()
                file.seek(0)
                
                if file_size > app.config['MAX_FILE_SIZE']:
                    flash(f'ไฟล์มีขนาดใหญ่เกินไป (สูงสุด {app.config["MAX_FILE_SIZE"] // (1024*1024)} MB)', 'error')
                    return redirect(url_for('admin_edit_guideline', guideline_id=guideline_id))
                
                # ลบไฟล์เก่าถ้ามี
                if guideline.file_path and os.path.exists(guideline.file_path):
                    try:
                        os.remove(guideline.file_path)
                        print(f"ลบไฟล์เก่า: {guideline.file_path}")
                    except Exception as e:
                        print(f"ไม่สามารถลบไฟล์เก่าได้: {e}")
                
                # จัดการชื่อไฟล์
                original_filename = file.filename
                custom_filename = request.form.get('custom_filename', '').strip()
                print(f"ชื่อไฟล์ต้นฉบับ: {original_filename}")
                print(f"ชื่อไฟล์ที่ต้องการ: {custom_filename}")
                
                # สร้างชื่อไฟล์ใหม่
                new_filename = generate_safe_filename(
                    original_filename, 
                    custom_filename
                )
                print(f"ชื่อไฟล์ใหม่: {new_filename}")
                
                dept = db.session.get(Department, department_id)
                dept_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'guidelines', dept.code.lower())
                os.makedirs(dept_folder, exist_ok=True)
                
                file_path = os.path.join(dept_folder, new_filename)
                print(f"บันทึกไฟล์ที่: {file_path}")
                
                # บันทึกไฟล์
                try:
                    file.save(file_path)
                    # ตรวจสอบว่าไฟล์ถูกบันทึกจริงหรือไม่
                    if os.path.exists(file_path):
                        actual_size = os.path.getsize(file_path)
                        print(f"ไฟล์ถูกบันทึกสำเร็จ ขนาดจริง: {actual_size} bytes")
                        
                        guideline.file_path = file_path
                        guideline.file_size = actual_size
                        guideline.external_link = None
                        guideline.link_type = None
                        
                        flash(f'อัปโหลดไฟล์ใหม่สำเร็จ: {new_filename}', 'success')
                    else:
                        print("ไฟล์ไม่ถูกบันทึก!")
                        flash('เกิดข้อผิดพลาดในการบันทึกไฟล์', 'error')
                        return redirect(url_for('admin_edit_guideline', guideline_id=guideline_id))
                except Exception as e:
                    print(f"เกิดข้อผิดพลาด: {e}")
                    flash('เกิดข้อผิดพลาดในการบันทึกไฟล์', 'error')
                    return redirect(url_for('admin_edit_guideline', guideline_id=guideline_id))
        elif upload_type == 'link':
            external_link = request.form['external_link']
            link_type = request.form['link_type']
            
            if external_link:
                guideline.external_link = external_link
                guideline.link_type = link_type
                guideline.file_path = None
                guideline.file_size = None
        
        db.session.commit()
        flash('แก้ไข guideline สำเร็จ', 'success')
        return redirect(url_for('admin_guidelines'))
    
    departments = db.session.query(Department).all()
    return render_template('admin/edit_guideline.html', guideline=guideline, departments=departments)

@app.route('/admin/guidelines/delete/<int:guideline_id>', methods=['POST'])
@login_required
def admin_delete_guideline(guideline_id):
    guideline = db.session.get(Guideline, guideline_id)
    if guideline is None:
        abort(404)
    
    # ลบไฟล์ถ้ามี
    if guideline.file_path and os.path.exists(guideline.file_path):
        os.remove(guideline.file_path)
    
    db.session.delete(guideline)
    db.session.commit()
    flash('ลบ guideline สำเร็จ', 'success')
    return redirect(url_for('admin_guidelines'))

@app.route('/admin/guidelines/delete_file/<int:guideline_id>', methods=['POST'])
@login_required
def admin_delete_guideline_file(guideline_id):
    """ลบไฟล์ที่แนบกับ guideline"""
    guideline = db.session.get(Guideline, guideline_id)
    if guideline is None:
        abort(404)
    
    if guideline.file_path and os.path.exists(guideline.file_path):
        try:
            os.remove(guideline.file_path)
            print(f"ลบไฟล์: {guideline.file_path}")
            
            # อัปเดตฐานข้อมูล
            guideline.file_path = None
            guideline.file_size = None
            db.session.commit()
            
            flash('ลบไฟล์สำเร็จ', 'success')
        except Exception as e:
            print(f"ไม่สามารถลบไฟล์ได้: {e}")
            flash('เกิดข้อผิดพลาดในการลบไฟล์', 'error')
    else:
        flash('ไฟล์ไม่พบ', 'error')
    
    return redirect(url_for('admin_edit_guideline', guideline_id=guideline_id))

@app.route('/admin/upload_guideline', methods=['GET', 'POST'])
@login_required
def upload_guideline():
    if request.method == 'POST':
        department_id = request.form['department_id']
        title = request.form['title']
        description = request.form['description']
        upload_type = request.form['upload_type']  # 'file' หรือ 'link'
        
        if upload_type == 'file':
            file = request.files['file']
            if file and file.filename:
                # ตรวจสอบขนาดไฟล์
                file.seek(0, 2)  # ไปที่ท้ายไฟล์
                file_size = file.tell()
                file.seek(0)  # กลับไปที่ต้นไฟล์
                
                if file_size > app.config['MAX_FILE_SIZE']:
                    flash(f'ไฟล์มีขนาดใหญ่เกินไป (สูงสุด {app.config["MAX_FILE_SIZE"] // (1024*1024)} MB)', 'error')
                    return redirect(url_for('admin_upload_guideline'))
                
                # จัดการชื่อไฟล์
                original_filename = file.filename
                custom_filename = request.form.get('custom_filename', '').strip()
                print(f"ชื่อไฟล์ต้นฉบับ: {original_filename}")
                print(f"ชื่อไฟล์ที่ต้องการ: {custom_filename}")
                
                # สร้างชื่อไฟล์ใหม่
                new_filename = generate_safe_filename(
                    original_filename, 
                    custom_filename
                )
                print(f"ชื่อไฟล์ใหม่: {new_filename}")
                
                dept = db.session.get(Department, department_id)
                dept_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'guidelines', dept.code.lower())
                os.makedirs(dept_folder, exist_ok=True)
                
                file_path = os.path.join(dept_folder, new_filename)
                print(f"บันทึกไฟล์ที่: {file_path}")
                
                # บันทึกไฟล์
                try:
                    file.save(file_path)
                    # ตรวจสอบว่าไฟล์ถูกบันทึกจริงหรือไม่
                    if os.path.exists(file_path):
                        actual_size = os.path.getsize(file_path)
                        print(f"ไฟล์ถูกบันทึกสำเร็จ ขนาดจริง: {actual_size} bytes")
                        
                        guideline = Guideline(
                            department_id=department_id,
                            title=title,
                            file_path=file_path,
                            file_size=actual_size,
                            description=description,
                            external_link=None,
                            link_type=None
                        )
                        db.session.add(guideline)
                        db.session.commit()
                        
                        flash(f'อัปโหลดไฟล์สำเร็จ: {new_filename}', 'success')
                        return redirect(url_for('admin_guidelines'))
                    else:
                        print("ไฟล์ไม่ถูกบันทึก!")
                        flash('เกิดข้อผิดพลาดในการบันทึกไฟล์', 'error')
                except Exception as e:
                    print(f"เกิดข้อผิดพลาด: {e}")
                    flash('เกิดข้อผิดพลาดในการบันทึกไฟล์', 'error')
                    return redirect(url_for('admin_upload_guideline'))
            else:
                flash('กรุณาเลือกไฟล์', 'error')
        elif upload_type == 'link':
            external_link = request.form['external_link']
            link_type = request.form['link_type']
            
            if external_link:
                guideline = Guideline(
                    department_id=department_id,
                    title=title,
                    file_path=None,
                    file_size=None,
                    description=description,
                    external_link=external_link,
                    link_type=link_type
                )
                db.session.add(guideline)
                db.session.commit()
                
                flash('เพิ่มลิงก์ภายนอกสำเร็จ', 'success')
                return redirect(url_for('admin_guidelines'))
            else:
                flash('กรุณาใส่ลิงก์', 'error')
    
    departments = db.session.query(Department).all()
    return render_template('admin/upload_guideline.html', departments=departments)

@app.route('/admin/knowledge')
@login_required
def admin_knowledge():
    knowledge = db.session.query(Knowledge).join(Department).all()
    return render_template('admin/knowledge.html', knowledge=knowledge)

@app.route('/storage/<path:filename>')
def serve_storage(filename):
    """Serve files from storage folder"""
    # ใช้ path โดยตรงจาก storage folder
    storage_path = os.path.join('storage', filename)
    if os.path.exists(storage_path):
        return send_file(storage_path)
    else:
        abort(404)

@app.route('/admin/activities')
@login_required
def admin_activities():
    activities = db.session.query(Activity).join(Department).all()
    return render_template('admin/activities.html', activities=activities)

@app.route('/admin/contacts')
@login_required
def admin_contacts():
    contacts = db.session.query(Contact).join(Department).all()
    departments = db.session.query(Department).all()
    return render_template('admin/contacts.html', contacts=contacts, departments=departments)

@app.route('/admin/contacts/add', methods=['GET', 'POST'])
@login_required
def admin_add_contact():
    if request.method == 'POST':
        department_id = request.form['department_id']
        line_id = request.form['line_id']
        email = request.form['email']
        phone = request.form['phone']
        other_contact = request.form['other_contact']
        
        # ตรวจสอบว่ามีข้อมูลอย่างน้อย 1 อย่าง
        if not any([line_id, email, phone, other_contact]):
            flash('กรุณาใส่ข้อมูลการติดต่ออย่างน้อย 1 อย่าง', 'error')
            return redirect(url_for('admin_add_contact'))
        
        contact = Contact(
            department_id=department_id,
            line_id=line_id if line_id else None,
            email=email if email else None,
            phone=phone if phone else None,
            other_contact=other_contact if other_contact else None
        )
        
        db.session.add(contact)
        db.session.commit()
        flash('เพิ่มข้อมูลการติดต่อสำเร็จ', 'success')
        return redirect(url_for('admin_contacts'))
    
    departments = db.session.query(Department).all()
    return render_template('admin/add_contact.html', departments=departments)

@app.route('/admin/contacts/edit/<int:contact_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_contact(contact_id):
    contact = db.session.get(Contact, contact_id)
    if contact is None:
        abort(404)
    
    if request.method == 'POST':
        department_id = request.form['department_id']
        line_id = request.form['line_id']
        email = request.form['email']
        phone = request.form['phone']
        other_contact = request.form['other_contact']
        
        # ตรวจสอบว่ามีข้อมูลอย่างน้อย 1 อย่าง
        if not any([line_id, email, phone, other_contact]):
            flash('กรุณาใส่ข้อมูลการติดต่ออย่างน้อย 1 อย่าง', 'error')
            return redirect(url_for('admin_edit_contact', contact_id=contact_id))
        
        contact.department_id = department_id
        contact.line_id = line_id if line_id else None
        contact.email = email if email else None
        contact.phone = phone if phone else None
        contact.other_contact = other_contact if other_contact else None
        
        db.session.commit()
        flash('แก้ไขข้อมูลการติดต่อสำเร็จ', 'success')
        return redirect(url_for('admin_contacts'))
    
    departments = db.session.query(Department).all()
    return render_template('admin/edit_contact.html', contact=contact, departments=departments)

@app.route('/admin/contacts/delete/<int:contact_id>', methods=['POST'])
@login_required
def admin_delete_contact(contact_id):
    contact = db.session.get(Contact, contact_id)
    if contact is None:
        abort(404)
    
    db.session.delete(contact)
    db.session.commit()
    flash('ลบข้อมูลการติดต่อสำเร็จ', 'success')
    return redirect(url_for('admin_contacts'))

@app.route('/admin/departments/edit/<int:dept_id>', methods=['GET', 'POST'])
@login_required
def edit_department(dept_id):
    dept = db.session.get(Department, dept_id)
    if dept is None:
        abort(404)
    
    if request.method == 'POST':
        dept.name = request.form['name']
        dept.code = request.form['code']
        dept.description = request.form['description']
        dept.updated_at = datetime.now(timezone.utc)
        
        db.session.commit()
        flash('แก้ไขข้อมูลหน่วยงานสำเร็จ', 'success')
        return redirect(url_for('admin_departments'))
    
    return render_template('admin/edit_department.html', department=dept)

@app.route('/admin/departments/delete/<int:dept_id>', methods=['POST'])
@login_required
def delete_department(dept_id):
    dept = db.session.get(Department, dept_id)
    if dept is None:
        abort(404)
    
    # ลบข้อมูลที่เกี่ยวข้องทั้งหมด
    db.session.query(Guideline).filter_by(department_id=dept_id).delete()
    db.session.query(Knowledge).filter_by(department_id=dept_id).delete()
    db.session.query(Activity).filter_by(department_id=dept_id).delete()
    db.session.query(Contact).filter_by(department_id=dept_id).delete()
    
    # ลบ PatientCase ที่อ้างอิงหน่วยงานนี้
    db.session.query(PatientCase).filter_by(department_id=dept_id).delete()
    
    # ลบหน่วยงาน
    db.session.delete(dept)
    db.session.commit()
    
    flash('ลบหน่วยงานและข้อมูลที่เกี่ยวข้องสำเร็จ', 'success')
    return redirect(url_for('admin_departments'))

# ==================== KNOWLEDGE MANAGEMENT ====================
@app.route('/admin/knowledge/add', methods=['GET', 'POST'])
@login_required
def admin_add_knowledge():
    if request.method == 'POST':
        department_id = request.form['department_id']
        title = request.form['title']
        content = request.form['content']
        upload_type = request.form['upload_type']
        
        # จำกัดความยาวเนื้อหา (500 ตัวอักษร)
        if len(content) > 500:
            flash('เนื้อหามีความยาวเกิน 500 ตัวอักษร', 'error')
            return redirect(url_for('admin_add_knowledge'))
        
        if upload_type == 'image':
            image = request.files['image']
            if image and image.filename:
                filename = secure_filename(image.filename)
                dept = db.session.get(Department, department_id)
                dept_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'knowledge', dept.code.lower())
                os.makedirs(dept_folder, exist_ok=True)
                
                image_path = os.path.join(dept_folder, filename)
                image.save(image_path)
                
                knowledge = Knowledge(
                    department_id=department_id,
                    title=title,
                    content=content,
                    image_path=image_path,
                    external_link=None,
                    link_type=None
                )
            else:
                flash('กรุณาเลือกรูปภาพ', 'error')
                return redirect(url_for('admin_add_knowledge'))
        elif upload_type == 'link':
            external_link = request.form['external_link']
            link_type = request.form['link_type']
            
            if external_link:
                knowledge = Knowledge(
                    department_id=department_id,
                    title=title,
                    content=content,
                    image_path=None,
                    external_link=external_link,
                    link_type=link_type
                )
            else:
                flash('กรุณาใส่ลิงก์', 'error')
                return redirect(url_for('admin_add_knowledge'))
        else:
            # เฉพาะเนื้อหา
            knowledge = Knowledge(
                department_id=department_id,
                title=title,
                content=content,
                image_path=None,
                external_link=None,
                link_type=None
            )
        
        db.session.add(knowledge)
        db.session.commit()
        flash('เพิ่มบทความความรู้สำเร็จ', 'success')
        return redirect(url_for('admin_knowledge'))
    
    departments = db.session.query(Department).all()
    return render_template('admin/add_knowledge.html', departments=departments)

@app.route('/admin/knowledge/edit/<int:knowledge_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_knowledge(knowledge_id):
    knowledge = db.session.get(Knowledge, knowledge_id)
    if knowledge is None:
        abort(404)
    
    if request.method == 'POST':
        knowledge.title = request.form['title']
        content = request.form['content']
        
        # จำกัดความยาวเนื้อหา
        if len(content) > 500:
            flash('เนื้อหามีความยาวเกิน 500 ตัวอักษร', 'error')
            return redirect(url_for('admin_edit_knowledge', knowledge_id=knowledge_id))
        
        knowledge.content = content
        knowledge.updated_at = datetime.now(timezone.utc)
        
        # อัปเดตรูปภาพหรือลิงก์
        upload_type = request.form['upload_type']
        if upload_type == 'image':
            image = request.files['image']
            if image and image.filename:
                filename = secure_filename(image.filename)
                dept = db.session.get(Department, knowledge.department_id)
                dept_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'knowledge', dept.code.lower())
                os.makedirs(dept_folder, exist_ok=True)
                
                image_path = os.path.join(dept_folder, filename)
                image.save(image_path)
                knowledge.image_path = image_path
                knowledge.external_link = None
                knowledge.link_type = None
        elif upload_type == 'link':
            external_link = request.form['external_link']
            link_type = request.form['link_type']
            if external_link:
                knowledge.external_link = external_link
                knowledge.link_type = link_type
                knowledge.image_path = None
        
        db.session.commit()
        flash('แก้ไขบทความความรู้สำเร็จ', 'success')
        return redirect(url_for('admin_knowledge'))
    
    return render_template('admin/edit_knowledge.html', knowledge=knowledge)

@app.route('/admin/knowledge/delete/<int:knowledge_id>', methods=['POST'])
@login_required
def admin_delete_knowledge(knowledge_id):
    knowledge = db.session.get(Knowledge, knowledge_id)
    if knowledge is None:
        abort(404)
    
    # ลบรูปภาพถ้ามี
    if knowledge.image_path and os.path.exists(knowledge.image_path):
        os.remove(knowledge.image_path)
    
    db.session.delete(knowledge)
    db.session.commit()
    flash('ลบบทความความรู้สำเร็จ', 'success')
    return redirect(url_for('admin_knowledge'))

# ==================== ACTIVITY MANAGEMENT ====================
@app.route('/admin/activity/add', methods=['GET', 'POST'])
@login_required
def admin_add_activity():
    if request.method == 'POST':
        department_id = request.form['department_id']
        title = request.form['title']
        description = request.form['description']
        activity_date = request.form['activity_date']
        upload_type = request.form['upload_type']
        
        # จำกัดความยาวคำอธิบาย (300 ตัวอักษร)
        if len(description) > 300:
            flash('คำอธิบายมีความยาวเกิน 300 ตัวอักษร', 'error')
            return redirect(url_for('admin_add_activity'))
        
        if upload_type == 'image':
            image = request.files['image']
            if image and image.filename:
                filename = secure_filename(image.filename)
                dept = db.session.get(Department, department_id)
                dept_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'activities', dept.code.lower())
                os.makedirs(dept_folder, exist_ok=True)
                
                image_path = os.path.join(dept_folder, filename)
                image.save(image_path)
                
                activity = Activity(
                    department_id=department_id,
                    title=title,
                    description=description,
                    activity_date=datetime.strptime(activity_date, '%Y-%m-%d').date(),
                    image_path=image_path,
                    external_link=None,
                    link_type=None
                )
            else:
                flash('กรุณาเลือกรูปภาพ', 'error')
                return redirect(url_for('admin_add_activity'))
        elif upload_type == 'link':
            external_link = request.form['external_link']
            link_type = request.form['link_type']
            
            if external_link:
                activity = Activity(
                    department_id=department_id,
                    title=title,
                    description=description,
                    activity_date=datetime.strptime(activity_date, '%Y-%m-%d').date(),
                    image_path=None,
                    external_link=external_link,
                    link_type=link_type
                )
            else:
                flash('กรุณาใส่ลิงก์', 'error')
                return redirect(url_for('admin_add_activity'))
        else:
            # เฉพาะข้อมูลพื้นฐาน
            activity = Activity(
                department_id=department_id,
                title=title,
                description=description,
                activity_date=datetime.strptime(activity_date, '%Y-%m-%d').date(),
                image_path=None,
                external_link=None,
                link_type=None
            )
        
        db.session.add(activity)
        db.session.commit()
        flash('เพิ่มกิจกรรมสำเร็จ', 'success')
        return redirect(url_for('admin_activities'))
    
    departments = db.session.query(Department).all()
    return render_template('admin/add_activity.html', departments=departments)

@app.route('/admin/activity/edit/<int:activity_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_activity(activity_id):
    activity = db.session.get(Activity, activity_id)
    if activity is None:
        abort(404)
    
    if request.method == 'POST':
        activity.title = request.form['title']
        description = request.form['description']
        activity_date = request.form['activity_date']
        
        # จำกัดความยาวคำอธิบาย
        if len(description) > 300:
            flash('คำอธิบายมีความยาวเกิน 300 ตัวอักษร', 'error')
            return redirect(url_for('admin_edit_activity', activity_id=activity_id))
        
        activity.description = description
        activity.activity_date = datetime.strptime(activity_date, '%Y-%m-%d').date()
        
        # อัปเดตรูปภาพหรือลิงก์
        upload_type = request.form['upload_type']
        if upload_type == 'image':
            image = request.files['image']
            if image and image.filename:
                filename = secure_filename(image.filename)
                dept = db.session.get(Department, activity.department_id)
                dept_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'activities', dept.code.lower())
                os.makedirs(dept_folder, exist_ok=True)
                
                image_path = os.path.join(dept_folder, filename)
                image.save(image_path)
                activity.image_path = image_path
                activity.external_link = None
                activity.link_type = None
        elif upload_type == 'link':
            external_link = request.form['external_link']
            link_type = request.form['link_type']
            if external_link:
                activity.external_link = external_link
                activity.link_type = link_type
                activity.image_path = None
        
        db.session.commit()
        flash('แก้ไขกิจกรรมสำเร็จ', 'success')
        return redirect(url_for('admin_activities'))
    
    return render_template('admin/edit_activity.html', activity=activity)

@app.route('/admin/activity/delete/<int:activity_id>', methods=['POST'])
@login_required
def admin_delete_activity(activity_id):
    activity = db.session.get(Activity, activity_id)
    if activity is None:
        abort(404)
    
    # ลบรูปภาพถ้ามี
    if activity.image_path and os.path.exists(activity.image_path):
        os.remove(activity.image_path)
    
    db.session.delete(activity)
    db.session.commit()
    flash('ลบกิจกรรมสำเร็จ', 'success')
    return redirect(url_for('admin_activities'))

@app.route('/admin/cases/delete_file/<int:case_id>', methods=['POST'])
@login_required
def admin_delete_case_file(case_id):
    """ลบไฟล์ที่แนบกับ case"""
    case = db.session.get(PatientCase, case_id)
    if case is None:
        abort(404)
    
    if case.file_path and os.path.exists(case.file_path):
        try:
            os.remove(case.file_path)
            print(f"ลบไฟล์: {case.file_path}")
            
            # อัปเดตฐานข้อมูล
            case.file_path = None
            case.file_size = None
            db.session.commit()
            
            # บันทึก audit log
            audit = CaseAudit(
                case_id=case.id,
                action='DELETE_FILE',
                user_id=current_user.id,
                ip_address=request.remote_addr
            )
            db.session.add(audit)
            db.session.commit()
            
            flash('ลบไฟล์สำเร็จ', 'success')
        except Exception as e:
            print(f"ไม่สามารถลบไฟล์ได้: {e}")
            flash('เกิดข้อผิดพลาดในการลบไฟล์', 'error')
    else:
        flash('ไฟล์ไม่พบ', 'error')
    
    return redirect(url_for('admin_edit_case', case_id=case_id))

def init_db():
    with app.app_context():
        db.create_all()
        
        # สร้างข้อมูลเริ่มต้น
        if db.session.query(Department).count() == 0:
            departments = [
                Department(name='หน่วยเบาหวาน', code='DM', description='หน่วยดูแลผู้ป่วยเบาหวาน'),
                Department(name='หน่วยปอดอุดกั้นเรื้อรัง', code='COPD', description='หน่วยดูแลผู้ป่วยโรคปอดอุดกั้นเรื้อรัง'),
                Department(name='หน่วยเลือดออกทางเดินอาหารส่วนต้น', code='UGIB', description='หน่วยดูแลผู้ป่วยเลือดออกทางเดินอาหารส่วนต้น'),
                Department(name='หน่วยไตเรื้อรัง', code='CKD', description='หน่วยดูแลผู้ป่วยไตเรื้อรัง'),
                Department(name='หน่วยหัวใจขาดเลือด', code='STEMI_NSTEMI', description='หน่วยดูแลผู้ป่วยหัวใจขาดเลือด'),
                Department(name='หน่วยโรคหลอดเลือดสมอง', code='STROKE', description='หน่วยดูแลผู้ป่วยโรคหลอดเลือดสมอง'),
                Department(name='หน่วยวัณโรค', code='TB', description='หน่วยดูแลผู้ป่วยวัณโรค'),
                Department(name='หน่วยเคมีบำบัด', code='CHEMO', description='หน่วยดูแลผู้ป่วยที่ได้รับเคมีบำบัด'),
                Department(name='หน่วยความดันโลหิตสูง', code='HTN', description='หน่วยดูแลผู้ป่วยโรคความดันโลหิตสูง'),
                Department(name='หน่วยภาวะติดเชื้อในกระแสเลือด', code='SEPSIS', description='หน่วยดูแลผู้ป่วยภาวะติดเชื้อในกระแสเลือด'),
                Department(name='หน่วยโรคข้อและรูมาติสซั่ม', code='RHEUMATO', description='หน่วยดูแลผู้ป่วยโรคข้อและรูมาติสซั่ม'),
                Department(name='หน่วยโรคอ้วน', code='OBESITY', description='หน่วยดูแลผู้ป่วยโรคอ้วน')
            ]
            
            for dept in departments:
                db.session.add(dept)
            
            # สร้างแอดมินเริ่มต้นจาก environment variables
            admin_username = os.getenv('ADMIN_USERNAME', 'admin')
            admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
            admin_email = os.getenv('ADMIN_EMAIL', 'admin@hospital.local')
            
            # ตรวจสอบว่ามี admin user อยู่แล้วหรือไม่
            existing_admin = AdminUser.query.filter_by(username=admin_username).first()
            
            if not existing_admin:
                admin = AdminUser(
                    username=admin_username,
                    password_hash=generate_password_hash(admin_password),
                    email=admin_email
                )
                db.session.add(admin)
                print(f"✅ สร้าง admin user: {admin_username}")
            else:
                print(f"✅ Admin user มีอยู่แล้ว: {admin_username}")
            
            db.session.commit()

# ==================== USER MANAGEMENT ====================
@app.route('/admin/users')
@login_required
def admin_users():
    """หน้าจัดการ Users"""
    if current_user.role != 'admin':
        flash('คุณไม่มีสิทธิ์เข้าถึงหน้านี้', 'error')
        return redirect(url_for('admin_dashboard'))
    
    users = db.session.query(User).order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/users/add', methods=['POST'])
@login_required
def admin_add_user():
    """เพิ่ม User ใหม่"""
    if current_user.role != 'admin':
        flash('คุณไม่มีสิทธิ์เข้าถึงหน้านี้', 'error')
        return redirect(url_for('admin_dashboard'))
    
    try:
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        email = request.form.get('email')
        role = request.form.get('role')
        
        # Validation
        if not username or not password or not role:
            flash('กรุณากรอกข้อมูลให้ครบถ้วน', 'error')
            return redirect(url_for('admin_users'))
        
        if password != confirm_password:
            flash('รหัสผ่านไม่ตรงกัน', 'error')
            return redirect(url_for('admin_users'))
        
        if len(password) < 6:
            flash('รหัสผ่านต้องมีอย่างน้อย 6 ตัวอักษร', 'error')
            return redirect(url_for('admin_users'))
        
        # ตรวจสอบ username ซ้ำ
        existing_user = db.session.query(User).filter_by(username=username).first()
        if existing_user:
            flash('ชื่อผู้ใช้นี้มีอยู่แล้วในระบบ', 'error')
            return redirect(url_for('admin_users'))
        
        # สร้าง user ใหม่
        new_user = User(
            username=username,
            password_hash=generate_password_hash(password),
            email=email if email else None,
            role=role,
            is_active=True
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash(f'เพิ่ม User {username} สำเร็จ', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'เกิดข้อผิดพลาด: {str(e)}', 'error')
    
    return redirect(url_for('admin_users'))

@app.route('/admin/users/delete/<int:user_id>', methods=['POST'])
@login_required
def admin_delete_user(user_id):
    """ลบ User"""
    if current_user.role != 'admin':
        flash('คุณไม่มีสิทธิ์เข้าถึงหน้านี้', 'error')
        return redirect(url_for('admin_dashboard'))
    
    if user_id == current_user.id:
        flash('คุณไม่สามารถลบตัวเองได้', 'error')
        return redirect(url_for('admin_users'))
    
    user = db.session.get(User, user_id)
    if user is None:
        flash('ไม่พบ User ที่ต้องการลบ', 'error')
        return redirect(url_for('admin_users'))
    
    try:
        db.session.delete(user)
        db.session.commit()
        flash(f'ลบ User {user.username} สำเร็จ', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'เกิดข้อผิดพลาด: {str(e)}', 'error')
    
    return redirect(url_for('admin_users'))

# ตัวแปรสำหรับเก็บข้อมูลระบบสำรองข้อมูล
backup_system_instance = None
last_backup_time = None
next_backup_time = None

# ฟังก์ชันสำหรับเริ่มระบบสำรองข้อมูลอัตโนมัติ
def init_backup_system():
    """เริ่มระบบสำรองข้อมูลอัตโนมัติ"""
    global backup_system_instance, last_backup_time, next_backup_time
    
    try:
        # ตั้งค่าระยะเวลาในการสำรองข้อมูล (ชั่วโมง)
        backup_interval = int(os.getenv('BACKUP_INTERVAL_HOURS', 24))
        
        # สร้างโฟลเดอร์สำหรับเก็บข้อมูลสำรอง
        backup_dir = os.getenv('BACKUP_DIR', 'storage/backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        # เริ่มระบบสำรองข้อมูลอัตโนมัติ
        backup_system_instance = start_scheduled_backup(backup_interval)
        
        # ลบข้อมูลสำรองที่เก่าเกิน 30 วัน
        backup_system_instance.cleanup_old_backups(keep_days=30)
        
        # บันทึกเวลาสำรองข้อมูลล่าสุดและครั้งถัดไป
        last_backup_time = datetime.now()
        next_backup_time = last_backup_time + timedelta(hours=backup_interval)
        
        print(f"เริ่มระบบสำรองข้อมูลอัตโนมัติทุก {backup_interval} ชั่วโมง")
        return backup_system_instance
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการเริ่มระบบสำรองข้อมูล: {str(e)}")
        return None

# ฟังก์ชันสำหรับรีสตาร์ทระบบสำรองข้อมูลอัตโนมัติ
def restart_backup_system(interval_hours):
    """รีสตาร์ทระบบสำรองข้อมูลอัตโนมัติด้วยระยะเวลาใหม่"""
    global backup_system_instance, last_backup_time, next_backup_time
    
    # หยุดระบบสำรองข้อมูลเดิม
    if backup_system_instance:
        backup_system_instance.stop_scheduled_backup()
    
    # เริ่มระบบสำรองข้อมูลใหม่
    backup_system_instance = BackupSystem(backup_interval=interval_hours)
    backup_system_instance.start_scheduled_backup()
    
    # บันทึกเวลาสำรองข้อมูลล่าสุดและครั้งถัดไป
    last_backup_time = datetime.now()
    next_backup_time = last_backup_time + timedelta(hours=interval_hours)
    
    return backup_system_instance

# เส้นทางสำหรับจัดการการสำรองข้อมูล
@app.route('/admin/backups')
@login_required
def admin_backups():
    """หน้าจัดการการสำรองข้อมูล"""
    # ตรวจสอบโฟลเดอร์สำรองข้อมูล
    backup_dir = os.getenv('BACKUP_DIR', 'storage/backups')
    db_backup_dir = os.path.join(backup_dir, 'database')
    uploads_backup_dir = os.path.join(backup_dir, 'uploads')
    
    # สร้างโฟลเดอร์ถ้ายังไม่มี
    os.makedirs(db_backup_dir, exist_ok=True)
    os.makedirs(uploads_backup_dir, exist_ok=True)
    
    # ดึงข้อมูลไฟล์สำรองฐานข้อมูล
    database_backups = []
    if os.path.exists(db_backup_dir):
        for filename in os.listdir(db_backup_dir):
            file_path = os.path.join(db_backup_dir, filename)
            if os.path.isfile(file_path):
                file_size = os.path.getsize(file_path)
                file_date = datetime.fromtimestamp(os.path.getctime(file_path))
                database_backups.append({
                    'filename': filename,
                    'date': file_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'size': f"{file_size / (1024 * 1024):.2f} MB"
                })
    
    # เรียงลำดับตามวันที่ล่าสุด
    database_backups.sort(key=lambda x: x['date'], reverse=True)
    
    # ดึงข้อมูลไฟล์สำรองอัปโหลด
    uploads_backups = []
    if os.path.exists(uploads_backup_dir):
        for foldername in os.listdir(uploads_backup_dir):
            folder_path = os.path.join(uploads_backup_dir, foldername)
            if os.path.isdir(folder_path):
                folder_date = datetime.fromtimestamp(os.path.getctime(folder_path))
                file_count = sum([len(files) for _, _, files in os.walk(folder_path)])
                uploads_backups.append({
                    'foldername': foldername,
                    'date': folder_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'file_count': file_count
                })
    
    # เรียงลำดับตามวันที่ล่าสุด
    uploads_backups.sort(key=lambda x: x['date'], reverse=True)
    
    # ดึงการตั้งค่าปัจจุบัน
    backup_interval = int(os.getenv('BACKUP_INTERVAL_HOURS', 24))
    keep_days = int(os.getenv('BACKUP_KEEP_DAYS', 30))
    
    # ข้อมูลเวลาสำรองข้อมูล
    global last_backup_time, next_backup_time
    last_backup_str = last_backup_time.strftime('%Y-%m-%d %H:%M:%S') if last_backup_time else "ยังไม่มีการสำรองข้อมูล"
    next_backup_str = next_backup_time.strftime('%Y-%m-%d %H:%M:%S') if next_backup_time else "ไม่ได้กำหนด"
    
    return render_template('admin/backups.html',
                           database_backups=database_backups,
                           uploads_backups=uploads_backups,
                           backup_interval=backup_interval,
                           keep_days=keep_days,
                           last_backup_time=last_backup_str,
                           next_backup_time=next_backup_str)

@app.route('/admin/backups/update-settings', methods=['POST'])
@login_required
def admin_update_backup_settings():
    """อัปเดตการตั้งค่าการสำรองข้อมูล"""
    try:
        # รับค่าจากฟอร์ม
        backup_interval = int(request.form.get('backup_interval', 24))
        keep_days = int(request.form.get('keep_days', 30))
        
        # ตรวจสอบค่า
        if backup_interval < 1 or backup_interval > 168:
            flash('ระยะเวลาในการสำรองข้อมูลต้องอยู่ระหว่าง 1-168 ชั่วโมง', 'danger')
            return redirect(url_for('admin_backups'))
        
        if keep_days < 1 or keep_days > 365:
            flash('จำนวนวันที่เก็บข้อมูลสำรองต้องอยู่ระหว่าง 1-365 วัน', 'danger')
            return redirect(url_for('admin_backups'))
        
        # อัปเดตค่าใน .env file
        env_path = '.env'
        env_vars = {}
        
        # อ่านไฟล์ .env ถ้ามี
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                for line in f:
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        env_vars[key] = value
        
        # อัปเดตค่า
        env_vars['BACKUP_INTERVAL_HOURS'] = str(backup_interval)
        env_vars['BACKUP_KEEP_DAYS'] = str(keep_days)
        
        # เขียนไฟล์ .env
        with open(env_path, 'w') as f:
            for key, value in env_vars.items():
                f.write(f"{key}={value}\n")
        
        # รีสตาร์ทระบบสำรองข้อมูล
        restart_backup_system(backup_interval)
        
        flash('อัปเดตการตั้งค่าการสำรองข้อมูลเรียบร้อยแล้ว', 'success')
    except Exception as e:
        flash(f'เกิดข้อผิดพลาด: {str(e)}', 'danger')
    
    return redirect(url_for('admin_backups'))

@app.route('/admin/backups/run-now', methods=['POST'])
@login_required
def admin_run_backup_now():
    """สั่งให้ระบบทำการสำรองข้อมูลทันที"""
    try:
        # รับค่าจากฟอร์ม
        backup_database = 'backup_database' in request.form
        backup_uploads = 'backup_uploads' in request.form
        
        if not backup_database and not backup_uploads:
            flash('กรุณาเลือกอย่างน้อยหนึ่งรายการ', 'warning')
            return redirect(url_for('admin_backups'))
        
        # สร้าง instance ของระบบสำรองข้อมูล
        backup_system = BackupSystem()
        
        # ดำเนินการสำรองข้อมูล
        if backup_database:
            if backup_system.backup_database():
                flash('สำรองฐานข้อมูลเรียบร้อยแล้ว', 'success')
            else:
                flash('เกิดข้อผิดพลาดในการสำรองฐานข้อมูล', 'danger')
        
        if backup_uploads:
            if backup_system.backup_uploads():
                flash('สำรองไฟล์อัปโหลดเรียบร้อยแล้ว', 'success')
            else:
                flash('เกิดข้อผิดพลาดในการสำรองไฟล์อัปโหลด', 'danger')
        
        # อัปเดตเวลาสำรองข้อมูลล่าสุด
        global last_backup_time
        last_backup_time = datetime.now()
    except Exception as e:
        flash(f'เกิดข้อผิดพลาด: {str(e)}', 'danger')
    
    return redirect(url_for('admin_backups'))

@app.route('/admin/backups/download/<backup_type>/<path:filename>')
@login_required
def admin_download_backup(backup_type, filename):
    """ดาวน์โหลดไฟล์สำรองข้อมูล"""
    try:
        backup_dir = os.getenv('BACKUP_DIR', 'storage/backups')
        
        if backup_type == 'database':
            file_path = os.path.join(backup_dir, 'database', filename)
            if os.path.exists(file_path) and os.path.isfile(file_path):
                return send_file(file_path, as_attachment=True)
        
        flash('ไม่พบไฟล์สำรองข้อมูล', 'danger')
    except Exception as e:
        flash(f'เกิดข้อผิดพลาด: {str(e)}', 'danger')
    
    return redirect(url_for('admin_backups'))

@app.route('/admin/backups/restore/<backup_type>/<path:filename>')
@login_required
def admin_restore_backup(backup_type, filename):
    """กู้คืนข้อมูลจากไฟล์สำรอง"""
    try:
        backup_dir = os.getenv('BACKUP_DIR', 'storage/backups')
        
        if backup_type == 'database':
            # กู้คืนฐานข้อมูล
            backup_path = os.path.join(backup_dir, 'database', filename)
            db_path = os.getenv('DATABASE_URL', 'sqlite:///hospital.db').replace('sqlite:///', '')
            
            if os.path.exists(backup_path) and os.path.isfile(backup_path):
                # สำรองฐานข้อมูลปัจจุบันก่อน
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                temp_backup = f"pre_restore_backup_{timestamp}.db"
                temp_backup_path = os.path.join(backup_dir, 'database', temp_backup)
                
                # คัดลอกฐานข้อมูลปัจจุบัน
                shutil.copy2(db_path, temp_backup_path)
                
                # กู้คืนฐานข้อมูล
                source = sqlite3.connect(backup_path)
                destination = sqlite3.connect(db_path)
                
                with destination:
                    source.backup(destination)
                
                source.close()
                destination.close()
                
                flash('กู้คืนฐานข้อมูลเรียบร้อยแล้ว', 'success')
            else:
                flash('ไม่พบไฟล์สำรองข้อมูล', 'danger')
        
        elif backup_type == 'uploads':
            # กู้คืนไฟล์อัปโหลด
            backup_path = os.path.join(backup_dir, 'uploads', filename)
            upload_dir = os.getenv('UPLOAD_FOLDER', 'storage/uploads')
            
            if os.path.exists(backup_path) and os.path.isdir(backup_path):
                # สำรองไฟล์ปัจจุบันก่อน
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                temp_backup = f"pre_restore_backup_{timestamp}"
                temp_backup_path = os.path.join(backup_dir, 'uploads', temp_backup)
                
                # คัดลอกไฟล์ปัจจุบัน
                shutil.copytree(upload_dir, temp_backup_path, dirs_exist_ok=True)
                
                # กู้คืนไฟล์อัปโหลด
                shutil.copytree(backup_path, upload_dir, dirs_exist_ok=True)
                
                flash('กู้คืนไฟล์อัปโหลดเรียบร้อยแล้ว', 'success')
            else:
                flash('ไม่พบโฟลเดอร์สำรองข้อมูล', 'danger')
    except Exception as e:
        flash(f'เกิดข้อผิดพลาดในการกู้คืนข้อมูล: {str(e)}', 'danger')
    
    return redirect(url_for('admin_backups'))

@app.route('/admin/backups/delete/<backup_type>/<path:filename>')
@login_required
def admin_delete_backup(backup_type, filename):
    """ลบไฟล์สำรองข้อมูล"""
    try:
        backup_dir = os.getenv('BACKUP_DIR', 'storage/backups')
        
        if backup_type == 'database':
            # ลบไฟล์สำรองฐานข้อมูล
            file_path = os.path.join(backup_dir, 'database', filename)
            if os.path.exists(file_path) and os.path.isfile(file_path):
                os.remove(file_path)
                flash('ลบไฟล์สำรองฐานข้อมูลเรียบร้อยแล้ว', 'success')
            else:
                flash('ไม่พบไฟล์สำรองข้อมูล', 'danger')
        
        elif backup_type == 'uploads':
            # ลบโฟลเดอร์สำรองไฟล์อัปโหลด
            folder_path = os.path.join(backup_dir, 'uploads', filename)
            if os.path.exists(folder_path) and os.path.isdir(folder_path):
                shutil.rmtree(folder_path)
                flash('ลบโฟลเดอร์สำรองไฟล์อัปโหลดเรียบร้อยแล้ว', 'success')
            else:
                flash('ไม่พบโฟลเดอร์สำรองข้อมูล', 'danger')
    except Exception as e:
        flash(f'เกิดข้อผิดพลาดในการลบไฟล์สำรอง: {str(e)}', 'danger')
    
    return redirect(url_for('admin_backups'))

if __name__ == '__main__':
    init_db()
    
    # เริ่มระบบสำรองข้อมูลอัตโนมัติ
    backup_system = init_backup_system()
    
    # ใช้ environment variables สำหรับ host และ port
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5001))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    app.run(host=host, port=port, debug=debug)
