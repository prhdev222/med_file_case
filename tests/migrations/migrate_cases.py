#!/usr/bin/env python3
"""
Database Migration Script for Patient Cases
ใช้สำหรับสร้างตารางใหม่สำหรับระบบจัดการข้อมูลผู้ป่วย
"""

import sqlite3
import os
from datetime import datetime

def create_tables():
    """สร้างตารางใหม่สำหรับระบบจัดการข้อมูลผู้ป่วย"""
    
    # เชื่อมต่อฐานข้อมูล
    db_path = 'instance/hospital.db'
    if not os.path.exists('instance'):
        os.makedirs('instance')
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🔧 เริ่มต้นการสร้างตารางใหม่...")
    
    try:
        # สร้างตาราง patient_case
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patient_case (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hn VARCHAR(20) NOT NULL,
                first_name VARCHAR(100) NOT NULL,
                last_name VARCHAR(100) NOT NULL,
                department_id INTEGER NOT NULL,
                case_date DATE NOT NULL,
                notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_deleted BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (department_id) REFERENCES department(id),
                FOREIGN KEY (created_by) REFERENCES admin_user(id)
            )
        ''')
        print("✅ สร้างตาราง patient_case สำเร็จ")
        
        # สร้างตาราง case_audit
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS case_audit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id INTEGER NOT NULL,
                action VARCHAR(20) NOT NULL,
                user_id INTEGER,
                ip_address VARCHAR(45),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (case_id) REFERENCES patient_case(id),
                FOREIGN KEY (user_id) REFERENCES admin_user(id)
            )
        ''')
        print("✅ สร้างตาราง case_audit สำเร็จ")
        
        # สร้าง indexes สำหรับประสิทธิภาพ
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_patient_case_dept_date 
            ON patient_case(department_id, case_date)
        ''')
        print("✅ สร้าง index สำหรับ department และ date")
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_patient_case_date 
            ON patient_case(case_date)
        ''')
        print("✅ สร้าง index สำหรับ date")
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_patient_case_hn_date 
            ON patient_case(hn, case_date)
        ''')
        print("✅ สร้าง index สำหรับ HN และ date")
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_case_audit_case_id 
            ON case_audit(case_id)
        ''')
        print("✅ สร้าง index สำหรับ audit case_id")
        
        # สร้าง unique constraint เพื่อป้องกัน HN ซ้ำในวันเดียวกัน
        cursor.execute('''
            CREATE UNIQUE INDEX IF NOT EXISTS idx_patient_case_hn_date_unique 
            ON patient_case(hn, case_date) 
            WHERE is_deleted = FALSE
        ''')
        print("✅ สร้าง unique constraint สำหรับ HN และ date")
        
        # Commit การเปลี่ยนแปลง
        conn.commit()
        print("✅ บันทึกการเปลี่ยนแปลงลงฐานข้อมูลสำเร็จ")
        
        # แสดงข้อมูลตารางที่สร้าง
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%case%'")
        tables = cursor.fetchall()
        print(f"\n📋 ตารางที่สร้างขึ้น:")
        for table in tables:
            print(f"   - {table[0]}")
        
        # แสดงข้อมูล indexes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name LIKE '%case%'")
        indexes = cursor.fetchall()
        print(f"\n🔍 Indexes ที่สร้างขึ้น:")
        for index in indexes:
            print(f"   - {index[0]}")
        
        print(f"\n🎉 การสร้างตารางเสร็จสิ้นแล้ว!")
        print(f"📅 เวลา: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except sqlite3.Error as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        conn.rollback()
    finally:
        conn.close()

def check_existing_data():
    """ตรวจสอบข้อมูลที่มีอยู่ในฐานข้อมูล"""
    
    db_path = 'instance/hospital.db'
    if not os.path.exists(db_path):
        print("❌ ไม่พบฐานข้อมูล")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\n🔍 ตรวจสอบข้อมูลที่มีอยู่...")
    
    try:
        # ตรวจสอบตาราง departments
        cursor.execute("SELECT COUNT(*) FROM department")
        dept_count = cursor.fetchone()[0]
        print(f"   - จำนวนหน่วยงาน: {dept_count}")
        
        # ตรวจสอบตาราง admin_users
        cursor.execute("SELECT COUNT(*) FROM admin_user")
        admin_count = cursor.fetchone()[0]
        print(f"   - จำนวน admin users: {admin_count}")
        
        # ตรวจสอบตาราง patient_case
        cursor.execute("SELECT COUNT(*) FROM patient_case")
        case_count = cursor.fetchone()[0]
        print(f"   - จำนวนผู้ป่วย: {case_count}")
        
        # ตรวจสอบตาราง case_audit
        cursor.execute("SELECT COUNT(*) FROM case_audit")
        audit_count = cursor.fetchone()[0]
        print(f"   - จำนวน audit logs: {audit_count}")
        
        if case_count > 0:
            print(f"\n📊 ข้อมูลผู้ป่วยล่าสุด:")
            cursor.execute('''
                SELECT pc.hn, pc.first_name, pc.last_name, d.name, pc.case_date
                FROM patient_case pc
                JOIN department d ON pc.department_id = d.id
                WHERE pc.is_deleted = FALSE
                ORDER BY pc.created_at DESC
                LIMIT 5
            ''')
            recent_cases = cursor.fetchall()
            for case in recent_cases:
                print(f"   - {case[0]}: {case[1]} {case[2]} ({case[3]}) - {case[4]}")
        
    except sqlite3.Error as e:
        print(f"❌ เกิดข้อผิดพลาดในการตรวจสอบ: {e}")
    finally:
        conn.close()

def main():
    """ฟังก์ชันหลัก"""
    print("🏥 ระบบจัดการข้อมูลผู้ป่วย - Database Migration")
    print("=" * 50)
    
    # สร้างตารางใหม่
    create_tables()
    
    # ตรวจสอบข้อมูล
    check_existing_data()
    
    print("\n" + "=" * 50)
    print("✨ การ migrate เสร็จสิ้นแล้ว!")
    print("💡 คุณสามารถเริ่มต้นใช้งานระบบจัดการข้อมูลผู้ป่วยได้แล้ว")

if __name__ == "__main__":
    main()
