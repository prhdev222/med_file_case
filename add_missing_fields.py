#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script สำหรับเพิ่มฟิลด์ที่ขาดหายไปในตาราง admin_user
"""

import sqlite3
import os

def add_missing_fields():
    """เพิ่มฟิลด์ที่ขาดหายไปในตาราง admin_user"""
    
    # เชื่อมต่อฐานข้อมูล
    db_path = 'instance/hospital.db'
    if not os.path.exists(db_path):
        print(f"❌ ไม่พบฐานข้อมูลที่: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("🔧 เพิ่มฟิลด์ที่ขาดหายไปในตาราง admin_user")
        print("=" * 50)
        
        # ตรวจสอบฟิลด์ที่มีอยู่
        cursor.execute("PRAGMA table_info(admin_user)")
        existing_columns = [col[1] for col in cursor.fetchall()]
        
        print("📋 ฟิลด์ที่มีอยู่:")
        for col in existing_columns:
            print(f"   ✅ {col}")
        
        # เพิ่มฟิลด์ role ถ้ายังไม่มี
        if 'role' not in existing_columns:
            print("\n➕ เพิ่มฟิลด์ 'role'...")
            cursor.execute("ALTER TABLE admin_user ADD COLUMN role VARCHAR(20) DEFAULT 'admin'")
            print("   ✅ เพิ่มฟิลด์ 'role' สำเร็จ")
            
            # อัปเดต role ของ admin ที่มีอยู่
            cursor.execute("UPDATE admin_user SET role = 'admin' WHERE role IS NULL")
            print("   ✅ อัปเดต role ของ admin ที่มีอยู่")
        else:
            print("\n✅ ฟิลด์ 'role' มีอยู่แล้ว")
        
        # เพิ่มฟิลด์ is_active ถ้ายังไม่มี
        if 'is_active' not in existing_columns:
            print("\n➕ เพิ่มฟิลด์ 'is_active'...")
            cursor.execute("ALTER TABLE admin_user ADD COLUMN is_active BOOLEAN DEFAULT 1")
            print("   ✅ เพิ่มฟิลด์ 'is_active' สำเร็จ")
            
            # อัปเดต is_active ของ admin ที่มีอยู่
            cursor.execute("UPDATE admin_user SET is_active = 1 WHERE is_active IS NULL")
            print("   ✅ อัปเดต is_active ของ admin ที่มีอยู่")
        else:
            print("\n✅ ฟิลด์ 'is_active' มีอยู่แล้ว")
        
        # Commit การเปลี่ยนแปลง
        conn.commit()
        
        print("\n" + "=" * 50)
        print("🔍 ตรวจสอบโครงสร้างใหม่:")
        
        # ตรวจสอบโครงสร้างใหม่
        cursor.execute("PRAGMA table_info(admin_user)")
        new_columns = cursor.fetchall()
        
        for col in new_columns:
            col_id, col_name, col_type, not_null, default_val, pk = col
            pk_mark = " 🔑" if pk else ""
            not_null_mark = " NOT NULL" if not_null else ""
            default_mark = f" DEFAULT {default_val}" if default_val else ""
            print(f"   {col_id}. {col_name} ({col_type}){not_null_mark}{default_mark}{pk_mark}")
        
        print(f"\n✅ อัปเดตตาราง admin_user สำเร็จ!")
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        conn.rollback()
        
    finally:
        conn.close()

def verify_admin_user():
    """ตรวจสอบข้อมูลในตาราง admin_user"""
    
    db_path = 'instance/hospital.db'
    if not os.path.exists(db_path):
        print(f"❌ ไม่พบฐานข้อมูลที่: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("\n🔍 ตรวจสอบข้อมูลในตาราง admin_user:")
        print("=" * 50)
        
        cursor.execute("SELECT id, username, email, role, is_active, created_at FROM admin_user")
        users = cursor.fetchall()
        
        if users:
            print("📋 รายการ Users:")
            for user in users:
                user_id, username, email, role, is_active, created_at = user
                status = "✅ เปิดใช้งาน" if is_active else "❌ ปิดใช้งาน"
                role_display = role or "ไม่ระบุ"
                print(f"   ID: {user_id}")
                print(f"   Username: {username}")
                print(f"   Email: {email}")
                print(f"   Role: {role_display}")
                print(f"   สถานะ: {status}")
                print(f"   วันที่สร้าง: {created_at}")
                print("   " + "-" * 30)
        else:
            print("❌ ไม่พบ Users ในระบบ")
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        
    finally:
        conn.close()

def main():
    """ฟังก์ชันหลัก"""
    while True:
        print("\n🔧 ระบบจัดการตาราง admin_user")
        print("=" * 35)
        print("1. เพิ่มฟิลด์ที่ขาดหายไป")
        print("2. ตรวจสอบข้อมูล Users")
        print("3. ออกจากโปรแกรม")
        
        choice = input("\nเลือกตัวเลือก (1-3): ").strip()
        
        if choice == "1":
            add_missing_fields()
        elif choice == "2":
            verify_admin_user()
        elif choice == "3":
            print("👋 ออกจากโปรแกรม")
            break
        else:
            print("❌ เลือกตัวเลือกไม่ถูกต้อง กรุณาลองใหม่")

if __name__ == "__main__":
    main()
