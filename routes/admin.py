from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timezone, timedelta
import os
import json
from models import db, Department, Guideline, Knowledge, Activity, Contact, PatientCase, CaseAudit, AdminUser

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Authentication routes
@admin_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = db.session.query(AdminUser).filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            user.last_login = datetime.now(timezone.utc)
            db.session.commit()
            return redirect(url_for('admin.admin_dashboard'))
        else:
            flash('ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง', 'error')
    
    return render_template('admin/login.html')

@admin_bp.route('/cases/login', methods=['GET', 'POST'])
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
            return redirect(url_for('admin.admin_cases'))
        else:
            flash('ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง', 'error')
    
    return render_template('admin/cases_login.html')

@admin_bp.route('/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('public.home'))

@admin_bp.route('/dashboard')
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

# Department management
@admin_bp.route('/departments')
@login_required
def admin_departments():
    departments = db.session.query(Department).all()
    return render_template('admin/departments.html', departments=departments)

@admin_bp.route('/departments/edit/<int:dept_id>', methods=['GET', 'POST'])
@login_required
def edit_department(dept_id):
    dept = db.session.get(Department, dept_id)
    if dept is None:
        abort(404)
    
    if request.method == 'POST':
        dept.name = request.form['name']
        dept.code = request.form['code']
        dept.description = request.form.get('description', '')
        db.session.commit()
        flash('แก้ไขข้อมูลหน่วยงานเรียบร้อยแล้ว', 'success')
        return redirect(url_for('admin.admin_departments'))

# Cases management
@admin_bp.route('/cases')
@login_required
def admin_cases():
    """หน้าจัดการข้อมูลผู้ป่วย"""
    cases = db.session.query(PatientCase).filter_by(is_deleted=False).order_by(PatientCase.created_at.desc()).all()
    return render_template('admin/cases.html', cases=cases)

# Guidelines management
@admin_bp.route('/guidelines')
@login_required
def admin_guidelines():
    """หน้าจัดการ Guidelines"""
    guidelines = db.session.query(Guideline).order_by(Guideline.upload_date.desc()).all()
    return render_template('admin/guidelines.html', guidelines=guidelines)

# Knowledge management
@admin_bp.route('/knowledge')
@login_required
def admin_knowledge():
    """หน้าจัดการความรู้"""
    knowledge = db.session.query(Knowledge).order_by(Knowledge.created_at.desc()).all()
    return render_template('admin/knowledge.html', knowledge=knowledge)

@admin_bp.route('/add_knowledge')
@login_required
def admin_add_knowledge():
    """หน้าเพิ่มความรู้ใหม่"""
    return render_template('admin/add_knowledge.html')

# Activities management
@admin_bp.route('/activities')
@login_required
def admin_activities():
    """หน้าจัดการกิจกรรม"""
    activities = db.session.query(Activity).order_by(Activity.created_at.desc()).all()
    return render_template('admin/activities.html', activities=activities)

@admin_bp.route('/add_activity')
@login_required
def admin_add_activity():
    """หน้าเพิ่มกิจกรรมใหม่"""
    return render_template('admin/add_activity.html')

# Backups management
@admin_bp.route('/backups')
@login_required
def admin_backups():
    """หน้าจัดการการสำรองข้อมูล"""
    return render_template('admin/backups.html')

# Upload guideline
@admin_bp.route('/upload_guideline')
@login_required
def upload_guideline():
    """หน้าอัปโหลด Guidelines"""
    return render_template('admin/upload_guideline.html')

# Add case
@admin_bp.route('/add_case')
@login_required
def admin_add_case():
    """หน้าเพิ่มผู้ป่วยใหม่"""
    return render_template('admin/add_case.html')

# Contacts management
@admin_bp.route('/contacts')
@login_required
def admin_contacts():
    """หน้าจัดการข้อมูลการติดต่อ"""
    contacts = db.session.query(Contact).order_by(Contact.id.desc()).all()
    return render_template('admin/contacts.html', contacts=contacts)
    
    return render_template('admin/edit_department.html', department=dept)

@admin_bp.route('/departments/delete/<int:dept_id>', methods=['POST'])
@login_required
def delete_department(dept_id):
    dept = db.session.get(Department, dept_id)
    if dept is None:
        abort(404)
    
    # ตรวจสอบว่ามี guidelines หรือ cases ที่เชื่อมโยงอยู่หรือไม่
    guidelines_count = db.session.query(Guideline).filter_by(department_id=dept_id).count()
    cases_count = db.session.query(PatientCase).filter_by(department_id=dept_id, is_deleted=False).count()
    
    if guidelines_count > 0 or cases_count > 0:
        flash(f'ไม่สามารถลบหน่วยงานได้ เนื่องจากมี Guidelines ({guidelines_count}) หรือ Cases ({cases_count}) ที่เชื่อมโยงอยู่', 'error')
    else:
        db.session.delete(dept)
        db.session.commit()
        flash('ลบหน่วยงานเรียบร้อยแล้ว', 'success')
    
    return redirect(url_for('admin.admin_departments'))