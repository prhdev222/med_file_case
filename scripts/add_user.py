#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script สำหรับเพิ่ม User ใหม่ในระบบ
"""

import sqlite3
import os
from werkzeug.security import generate_password_hash
from datetime import datetime

def add_user():
    """เพิ่ม User ใหม่"""
    
    # เชื่อมต่อฐานข้อมูล
    db_path = 'instance/hospital.db'
    if not os.path.exists(db_path):
        print(f"❌ ไม่พบฐานข้อมูลที่: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("🔐 ระบบเพิ่ม User ใหม่")
        print("=" * 40)
        
        # รับข้อมูลจากผู้ใช้
        username = input("ชื่อผู้ใช้ (username): ").strip()
        if not username:
            print("❌ ชื่อผู้ใช้ไม่สามารถเป็นค่าว่างได้")
            return
        
        # ตรวจสอบว่ามี username นี้อยู่แล้วหรือไม่
        cursor.execute("SELECT id FROM admin_user WHERE username = ?", (username,))
        if cursor.fetchone():
            print(f"❌ ชื่อผู้ใช้ '{username}' มีอยู่แล้วในระบบ")
            return
        
        password = input("รหัสผ่าน: ").strip()
        if not password:
            print("❌ รหัสผ่านไม่สามารถเป็นค่าว่างได้")
            return
        
        # ยืนยันรหัสผ่าน
        confirm_password = input("ยืนยันรหัสผ่าน: ").strip()
        if password != confirm_password:
            print("❌ รหัสผ่านไม่ตรงกัน")
            return
        
        # เลือก role
        print("\nเลือก Role:")
        print("1. admin - ผู้ดูแลระบบ")
        print("2. nurse - พยาบาล")
        print("3. doctor - แพทย์")
        print("4. staff - เจ้าหน้าที่")
        
        role_choice = input("เลือก role (1-4): ").strip()
        
        role_map = {
            '1': 'admin',
            '2': 'nurse', 
            '3': 'doctor',
            '4': 'staff'
        }
        
        if role_choice not in role_map:
            print("❌ เลือก role ไม่ถูกต้อง ใช้ค่าเริ่มต้น: staff")
            role = 'staff'
        else:
            role = role_map[role_choice]
        
        # รับ email (ไม่บังคับ)
        email = input("อีเมล (ไม่บังคับ): ").strip()
        if not email:
            email = None
        
        # สร้าง password hash
        password_hash = generate_password_hash(password)
        
        # เพิ่ม user ใหม่
        cursor.execute("""
            INSERT INTO admin_user (username, password_hash, email, role, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (username, password_hash, email, role, 1, datetime.now()))
        
        # Commit การเปลี่ยนแปลง
        conn.commit()
        
        print(f"\n✅ เพิ่ม User สำเร็จ!")
        print(f"   Username: {username}")
        print(f"   Role: {role}")
        print(f"   Email: {email or 'ไม่ระบุ'}")
        print(f"   สถานะ: เปิดใช้งาน")
        
        # แสดงรายการ users ทั้งหมด
        print(f"\n📋 รายการ Users ทั้งหมด:")
        cursor.execute("SELECT username, role, email, is_active FROM admin_user ORDER BY created_at")
        users = cursor.fetchall()
        
        for i, user in enumerate(users, 1):
            status = "✅ เปิดใช้งาน" if user[3] else "❌ ปิดใช้งาน"
            print(f"   {i}. {user[0]} ({user[1]}) - {user[2] or 'ไม่ระบุ'} - {status}")
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        conn.rollback()
        
    finally:
        conn.close()

def list_users():
    """แสดงรายการ Users ทั้งหมด"""
    
    db_path = 'instance/hospital.db'
    if not os.path.exists(db_path):
        print(f"❌ ไม่พบฐานข้อมูลที่: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("📋 รายการ Users ทั้งหมดในระบบ")
        print("=" * 50)
        
        cursor.execute("""
            SELECT username, role, email, is_active, created_at 
            FROM admin_user 
            ORDER BY created_at
        """)
        
        users = cursor.fetchall()
        
        if not users:
            print("❌ ไม่พบ Users ในระบบ")
            return
        
        for i, user in enumerate(users, 1):
            status = "✅ เปิดใช้งาน" if user[3] else "❌ ปิดใช้งาน"
            created_date = user[4][:10] if user[4] else 'ไม่ระบุ'
            
            print(f"{i:2}. {user[0]:<15} | {user[1]:<10} | {user[2] or 'ไม่ระบุ':<20} | {status:<12} | {created_date}")
        
        print(f"\nรวม {len(users)} Users")
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        
    finally:
        conn.close()

def main():
    """ฟังก์ชันหลัก"""
    while True:
        print("\n🔐 ระบบจัดการ Users")
        print("=" * 30)
        print("1. เพิ่ม User ใหม่")
        print("2. แสดงรายการ Users ทั้งหมด")
        print("3. ออกจากโปรแกรม")
        
        choice = input("\nเลือกตัวเลือก (1-3): ").strip()
        
        if choice == "1":
            add_user()
        elif choice == "2":
            list_users()
        elif choice == "3":
            print("👋 ออกจากโปรแกรม")
            break
        else:
            print("❌ เลือกตัวเลือกไม่ถูกต้อง กรุณาลองใหม่")

if __name__ == "__main__":
    main()
