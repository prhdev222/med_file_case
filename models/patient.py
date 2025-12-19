#!/usr/bin/env python3
"""
Patient models สำหรับระบบจัดการข้อมูลผู้ป่วย
"""

from . import db
from datetime import datetime, timezone

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