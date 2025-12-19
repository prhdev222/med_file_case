#!/usr/bin/env python3
"""
Content models สำหรับระบบจัดการข้อมูลผู้ป่วย
"""

from . import db
from datetime import datetime, timezone

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