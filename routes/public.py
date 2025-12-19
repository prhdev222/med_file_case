from flask import Blueprint, render_template, abort, redirect, url_for, send_file, flash, jsonify
import os
from models import db, Department, Guideline, PatientCase

public_bp = Blueprint('public', __name__)

@public_bp.route('/health')
def health_check():
    """Health check endpoint for Docker and load balancers"""
    try:
        # Test database connection
        db.session.execute(db.text('SELECT 1'))
        return jsonify({
            'status': 'healthy',
            'database': 'connected'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e)
        }), 503

@public_bp.route('/')
def home():
    departments = db.session.query(Department).all()
    return render_template('home.html', departments=departments)

@public_bp.route('/department/<int:dept_id>')
def department(dept_id):
    dept = db.session.get(Department, dept_id)
    if dept is None:
        abort(404)
    return render_template('department.html', department=dept)

@public_bp.route('/download/<int:guideline_id>')
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
    return redirect(url_for('public.department', dept_id=guideline.department_id))

@public_bp.route('/stats')
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
            case_count = db.session.query(PatientCase).filter_by(
                department_id=dept.id, 
                is_deleted=False
            ).count()
            
            if case_count > 0:  # แสดงเฉพาะหน่วยงานที่มี case
                dept_stats.append({
                    'name': dept.name,
                    'count': case_count
                })
        
        # เรียงตามจำนวน case จากมากไปน้อย
        dept_stats.sort(key=lambda x: x['count'], reverse=True)
        
        # จำนวน guidelines ทั้งหมด
        total_guidelines = db.session.query(Guideline).count()
        
        # สร้าง stats object สำหรับ template
        stats = {
            'total_cases': total_cases,
            'dept_stats': dept_stats,
            'total_guidelines': total_guidelines,
            'cases_with_files': 0,  # placeholder
            'cases_with_links': 0,  # placeholder
            'monthly_stats': []     # placeholder
        }
        
        return render_template('stats.html', stats=stats)
    
    except Exception as e:
        print(f"Error in stats route: {e}")
        # สร้าง stats object สำหรับ template (error case)
        stats = {
            'total_cases': 0,
            'dept_stats': [],
            'total_guidelines': 0,
            'cases_with_files': 0,
            'cases_with_links': 0,
            'monthly_stats': []
        }
        
        return render_template('stats.html', stats=stats)

@public_bp.route('/storage/<path:filename>')
def storage(filename):
    """Serve files from storage directory"""
    storage_path = os.path.join(os.getcwd(), 'storage')
    file_path = os.path.join(storage_path, filename)
    
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return send_file(file_path)
    else:
        abort(404)