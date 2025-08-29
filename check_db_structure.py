#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script สำหรับตรวจสอบโครงสร้างฐานข้อมูล
"""

import sqlite3
import os

def check_database_structure():
    """ตรวจสอบโครงสร้างฐานข้อมูล"""
    
    # เชื่อมต่อฐานข้อมูล
    db_path = 'instance/hospital.db'
    if not os.path.exists(db_path):
        print(f"❌ ไม่พบฐานข้อมูลที่: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("🔍 ตรวจสอบโครงสร้างฐานข้อมูล")
        print("=" * 50)
        
        # ดูตารางทั้งหมด
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"📋 ตารางทั้งหมดในฐานข้อมูล: {len(tables)} ตาราง")
        for table in tables:
            print(f"   - {table[0]}")
        
        print("\n" + "=" * 50)
        
        # ตรวจสอบตาราง user และ admin_user
        user_tables = [table[0] for table in tables if 'user' in table[0].lower()]
        
        if user_tables:
            print("🔐 ตารางที่เกี่ยวข้องกับ Users:")
            for table in user_tables:
                print(f"\n📊 ตาราง: {table}")
                
                # ดูโครงสร้างตาราง
                cursor.execute(f"PRAGMA table_info({table})")
                columns = cursor.fetchall()
                
                print("   โครงสร้าง:")
                for col in columns:
                    col_id, col_name, col_type, not_null, default_val, pk = col
                    pk_mark = " 🔑" if pk else ""
                    not_null_mark = " NOT NULL" if not_null else ""
                    print(f"     {col_id}. {col_name} ({col_type}){not_null_mark}{pk_mark}")
                
                # ดูจำนวนข้อมูล
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"   จำนวนข้อมูล: {count} รายการ")
                
                if count > 0:
                    # แสดงข้อมูลตัวอย่าง
                    cursor.execute(f"SELECT * FROM {table} LIMIT 3")
                    sample_data = cursor.fetchall()
                    print("   ข้อมูลตัวอย่าง:")
                    for i, row in enumerate(sample_data, 1):
                        print(f"     {i}. {row}")
        else:
            print("❌ ไม่พบตารางที่เกี่ยวข้องกับ Users")
        
        print("\n" + "=" * 50)
        
        # ตรวจสอบตารางอื่นๆ ที่สำคัญ
        important_tables = ['department', 'patient_case', 'guideline']
        for table in important_tables:
            if table in [t[0] for t in tables]:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"📊 {table}: {count} รายการ")
            else:
                print(f"❌ {table}: ไม่พบตาราง")
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        
    finally:
        conn.close()

def create_user_table():
    """สร้างตาราง user ถ้ายังไม่มี"""
    
    db_path = 'instance/hospital.db'
    if not os.path.exists(db_path):
        print(f"❌ ไม่พบฐานข้อมูลที่: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("\n🔧 สร้างตาราง user...")
        
        # สร้างตาราง user
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(80) UNIQUE NOT NULL,
                password_hash VARCHAR(120) NOT NULL,
                email VARCHAR(120),
                role VARCHAR(20) DEFAULT 'staff',
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # สร้าง index
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_username ON user(username)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_role ON user(role)")
        
        conn.commit()
        print("✅ สร้างตาราง user สำเร็จ")
        
        # ตรวจสอบว่าสร้างสำเร็จหรือไม่
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user'")
        if cursor.fetchone():
            print("✅ ตาราง user พร้อมใช้งาน")
        else:
            print("❌ ไม่สามารถสร้างตาราง user ได้")
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        conn.rollback()
        
    finally:
        conn.close()

def main():
    """ฟังก์ชันหลัก"""
    while True:
        print("\n🔍 ระบบตรวจสอบฐานข้อมูล")
        print("=" * 30)
        print("1. ตรวจสอบโครงสร้างฐานข้อมูล")
        print("2. สร้างตาราง user")
        print("3. ออกจากโปรแกรม")
        
        choice = input("\nเลือกตัวเลือก (1-3): ").strip()
        
        if choice == "1":
            check_database_structure()
        elif choice == "2":
            create_user_table()
        elif choice == "3":
            print("👋 ออกจากโปรแกรม")
            break
        else:
            print("❌ เลือกตัวเลือกไม่ถูกต้อง กรุณาลองใหม่")

if __name__ == "__main__":
    main()
