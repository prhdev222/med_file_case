#!/usr/bin/env python3
"""
สร้างข้อมูลตัวอย่างสำหรับระบบจัดการข้อมูลผู้ป่วย
ใช้สำหรับทดสอบระบบโดยไม่ต้องใช้ข้อมูลจริง
"""

import os
import sys
from datetime import datetime, timedelta
import random

# เพิ่ม path ของโปรเจค
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Department, PatientCase, AdminUser
from werkzeug.security import generate_password_hash

def create_sample_departments():
    """สร้างข้อมูลหน่วยงานตัวอย่าง"""
    print("🏥 สร้างข้อมูลหน่วยงานตัวอย่าง...")
    
    departments_data = [
        {
            'name': 'หน่วยเบาหวาน',
            'code': 'DM',
            'description': 'หน่วยดูแลผู้ป่วยเบาหวาน'
        },
        {
            'name': 'หน่วยปอดอุดกั้นเรื้อรัง',
            'code': 'COPD',
            'description': 'หน่วยดูแลผู้ป่วยโรคปอดอุดกั้นเรื้อรัง'
        },
        {
            'name': 'หน่วยหัวใจขาดเลือด',
            'code': 'STEMI',
            'description': 'หน่วยดูแลผู้ป่วยหัวใจขาดเลือด'
        },
        {
            'name': 'หน่วยโรคหลอดเลือดสมอง',
            'code': 'STROKE',
            'description': 'หน่วยดูแลผู้ป่วยโรคหลอดเลือดสมอง'
        },
        {
            'name': 'หน่วยเคมีบำบัด',
            'code': 'CHEMO',
            'description': 'หน่วยดูแลผู้ป่วยที่ได้รับเคมีบำบัด'
        }
    ]
    
    for dept_data in departments_data:
        # ตรวจสอบว่ามีอยู่แล้วหรือไม่
        existing = Department.query.filter_by(code=dept_data['code']).first()
        if not existing:
            dept = Department(**dept_data)
            db.session.add(dept)
            print(f"   ✅ สร้างหน่วยงาน: {dept_data['name']}")
        else:
            print(f"   ⚠️ หน่วยงานมีอยู่แล้ว: {dept_data['name']}")
    
    db.session.commit()
    print("   🎯 สร้างหน่วยงานเสร็จสิ้น")

def create_sample_patient_cases():
    """สร้างข้อมูลผู้ป่วยตัวอย่าง"""
    print("\n👥 สร้างข้อมูลผู้ป่วยตัวอย่าง...")
    
    # ดึงข้อมูลหน่วยงาน
    departments = Department.query.all()
    if not departments:
        print("   ❌ ไม่พบข้อมูลหน่วยงาน กรุณาสร้างหน่วยงานก่อน")
        return
    
    # ข้อมูลผู้ป่วยตัวอย่าง
    sample_patients = [
        {
            'hn': '123456',
            'first_name': 'สมชาย',
            'last_name': 'แมนเมือง',
            'department_code': 'DM',
            'case_date': datetime.now().date() - timedelta(days=1),
            'notes': 'ผู้ป่วยเบาหวานรายใหม่ ต้องการติดตามผล'
        },
        {
            'hn': '234567',
            'first_name': 'สมหญิง',
            'last_name': 'ใจดี',
            'department_code': 'COPD',
            'case_date': datetime.now().date() - timedelta(days=2),
            'notes': 'อาการหายใจลำบาก ต้องใช้เครื่องช่วยหายใจ'
        },
        {
            'hn': '345678',
            'first_name': 'สมศักดิ์',
            'last_name': 'รักสุขภาพ',
            'department_code': 'STEMI',
            'case_date': datetime.now().date() - timedelta(days=3),
            'notes': 'เจ็บหน้าอกเฉียบพลัน ต้องทำการรักษาทันที'
        },
        {
            'hn': '456789',
            'first_name': 'สมปอง',
            'last_name': 'ใจเย็น',
            'department_code': 'STROKE',
            'case_date': datetime.now().date() - timedelta(days=4),
            'notes': 'อัมพาตครึ่งซีก ต้องทำกายภาพบำบัด'
        },
        {
            'hn': '567890',
            'first_name': 'สมศรี',
            'last_name': 'สวยงาม',
            'department_code': 'CHEMO',
            'case_date': datetime.now().date() - timedelta(days=5),
            'notes': 'ได้รับเคมีบำบัดครั้งที่ 3 ต้องติดตามผลข้างเคียง'
        }
    ]
    
    for patient_data in sample_patients:
        # ตรวจสอบว่ามีอยู่แล้วหรือไม่
        existing = PatientCase.query.filter_by(hn=patient_data['hn']).first()
        if not existing:
            # หาหน่วยงาน
            dept = Department.query.filter_by(code=patient_data['department_code']).first()
            if dept:
                # สร้างข้อมูลผู้ป่วย
                case = PatientCase(
                    hn=patient_data['hn'],
                    first_name=patient_data['first_name'],
                    last_name=patient_data['last_name'],
                    department_id=dept.id,
                    case_date=patient_data['case_date'],
                    notes=patient_data['notes'],
                    created_by=1,  # admin user ID
                    is_deleted=False
                )
                db.session.add(case)
                print(f"   ✅ สร้างผู้ป่วย: {patient_data['first_name']} {patient_data['last_name']} (HN: {patient_data['hn']})")
            else:
                print(f"   ❌ ไม่พบหน่วยงาน: {patient_data['department_code']}")
        else:
            print(f"   ⚠️ ผู้ป่วยมีอยู่แล้ว: HN {patient_data['hn']}")
    
    db.session.commit()
    print("   🎯 สร้างข้อมูลผู้ป่วยเสร็จสิ้น")

def create_sample_admin_user():
    """สร้าง admin user ตัวอย่าง"""
    print("\n👤 สร้าง Admin User ตัวอย่าง...")
    
    # ตรวจสอบว่ามี admin user อยู่แล้วหรือไม่
    existing_admin = AdminUser.query.filter_by(username='admin').first()
    if not existing_admin:
        admin = AdminUser(
            username='admin',
            password_hash=generate_password_hash('admin123'),
            email='admin@hospital.local'
        )
        db.session.add(admin)
        db.session.commit()
        print("   ✅ สร้าง Admin User: admin (รหัสผ่าน: admin123)")
    else:
        print("   ⚠️ Admin User มีอยู่แล้ว: admin")

def create_sample_data():
    """สร้างข้อมูลตัวอย่างทั้งหมด"""
    print("🚀 เริ่มสร้างข้อมูลตัวอย่าง...")
    print("=" * 50)
    
    with app.app_context():
        try:
            # สร้าง admin user
            create_sample_admin_user()
            
            # สร้างหน่วยงาน
            create_sample_departments()
            
            # สร้างข้อมูลผู้ป่วย
            create_sample_patient_cases()
            
            print("\n" + "=" * 50)
            print("🎉 สร้างข้อมูลตัวอย่างเสร็จสิ้น!")
            print("\n📋 ข้อมูลที่สร้างขึ้น:")
            print("   👤 Admin User: admin / admin123")
            print("   🏥 หน่วยงาน: 5 แห่ง")
            print("   👥 ผู้ป่วย: 5 ราย")
            
            print("\n🔗 ลิงก์สำหรับทดสอบ:")
            print("   🌐 หน้าแรก: http://localhost:5001")
            print("   📊 สถิติ: http://localhost:5001/stats")
            print("   🔐 Admin Login: http://localhost:5001/admin/login")
            print("   👥 จัดการผู้ป่วย: http://localhost:5001/admin/cases")
            
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาด: {e}")
            db.session.rollback()

def clear_sample_data():
    """ลบข้อมูลตัวอย่างทั้งหมด"""
    print("🗑️ ลบข้อมูลตัวอย่างทั้งหมด...")
    
    with app.app_context():
        try:
            # ลบข้อมูลผู้ป่วย
            PatientCase.query.delete()
            print("   ✅ ลบข้อมูลผู้ป่วย")
            
            # ลบข้อมูลหน่วยงาน
            Department.query.delete()
            print("   ✅ ลบข้อมูลหน่วยงาน")
            
            # ลบ admin user (ยกเว้น admin หลัก)
            AdminUser.query.filter(AdminUser.username != 'admin').delete()
            print("   ✅ ลบ admin user ตัวอย่าง")
            
            db.session.commit()
            print("   🎯 ลบข้อมูลตัวอย่างเสร็จสิ้น")
            
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาด: {e}")
            db.session.rollback()

if __name__ == "__main__":
    print("🧪 ระบบสร้างข้อมูลตัวอย่าง")
    print("เลือกตัวเลือก:")
    print("1. สร้างข้อมูลตัวอย่าง")
    print("2. ลบข้อมูลตัวอย่าง")
    print("3. ออกจากโปรแกรม")
    
    while True:
        choice = input("\nกรุณาเลือก (1-3): ").strip()
        
        if choice == '1':
            create_sample_data()
            break
        elif choice == '2':
            confirm = input("คุณแน่ใจหรือไม่ที่จะลบข้อมูลตัวอย่างทั้งหมด? (y/N): ").strip().lower()
            if confirm == 'y':
                clear_sample_data()
            break
        elif choice == '3':
            print("👋 ออกจากโปรแกรม")
            break
        else:
            print("❌ กรุณาเลือก 1, 2, หรือ 3")
