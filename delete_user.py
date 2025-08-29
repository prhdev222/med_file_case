#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script สำหรับลบ User ในระบบ
"""

import sqlite3
import os

def list_users():
    """แสดงรายการ Users ทั้งหมด"""
    
    db_path = 'instance/hospital.db'
    if not os.path.exists(db_path):
        print(f"❌ ไม่พบฐานข้อมูลที่: {db_path}")
        return []
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("📋 รายการ Users ทั้งหมดในระบบ")
        print("=" * 60)
        
        # ตรวจสอบว่ามีฟิลด์ role และ is_active หรือไม่
        cursor.execute("PRAGMA table_info(admin_user)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'role' in columns and 'is_active' in columns:
            cursor.execute("""
                SELECT id, username, email, role, is_active, created_at 
                FROM admin_user 
                ORDER BY created_at
            """)
        else:
            # ถ้าไม่มีฟิลด์ใหม่ ใช้โครงสร้างเดิม
            cursor.execute("""
                SELECT id, username, email, created_at 
                FROM admin_user 
                ORDER BY created_at
            """)
        
        users = cursor.fetchall()
        
        if not users:
            print("❌ ไม่พบ Users ในระบบ")
            return []
        
        print(f"{'ID':<4} {'Username':<15} {'Email':<25} {'Role':<10} {'Status':<12} {'Created'}")
        print("-" * 60)
        
        for user in users:
            if len(user) >= 5:  # มีฟิลด์ใหม่
                user_id, username, email, role, is_active, created_at = user
                status = "✅ เปิดใช้งาน" if is_active else "❌ ปิดใช้งาน"
                role_display = role or "ไม่ระบุ"
            else:  # โครงสร้างเดิม
                user_id, username, email, created_at = user
                status = "✅ เปิดใช้งาน"
                role_display = "ไม่ระบุ"
            
            created_date = created_at[:10] if created_at else 'ไม่ระบุ'
            print(f"{user_id:<4} {username:<15} {email:<25} {role_display:<10} {status:<12} {created_date}")
        
        print(f"\nรวม {len(users)} Users")
        return users
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        return []
        
    finally:
        conn.close()

def delete_user():
    """ลบ User"""
    
    # แสดงรายการ Users ก่อน
    users = list_users()
    if not users:
        return
    
    print("\n" + "=" * 60)
    
    # รับ ID ของ User ที่ต้องการลบ
    try:
        user_id = input("กรุณาใส่ ID ของ User ที่ต้องการลบ: ").strip()
        if not user_id:
            print("❌ กรุณาใส่ ID")
            return
        
        user_id = int(user_id)
        
        # ตรวจสอบว่ามี User นี้อยู่หรือไม่
        db_path = 'instance/hospital.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT username, email FROM admin_user WHERE id = ?", (user_id,))
            user = cursor.fetchone()
            
            if not user:
                print(f"❌ ไม่พบ User ที่มี ID: {user_id}")
                return
            
            username, email = user
            
            # ยืนยันการลบ
            print(f"\n⚠️  คุณต้องการลบ User นี้ใช่หรือไม่?")
            print(f"   ID: {user_id}")
            print(f"   Username: {username}")
            print(f"   Email: {email}")
            
            confirm = input("\nพิมพ์ 'YES' เพื่อยืนยันการลบ: ").strip()
            
            if confirm == 'YES':
                # ลบ User
                cursor.execute("DELETE FROM admin_user WHERE id = ?", (user_id,))
                conn.commit()
                
                print(f"\n✅ ลบ User '{username}' สำเร็จ!")
                
                # แสดงรายการ Users ใหม่
                print("\n📋 รายการ Users หลังการลบ:")
                list_users()
                
            else:
                print("❌ ยกเลิกการลบ")
        
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาด: {e}")
            conn.rollback()
            
        finally:
            conn.close()
            
    except ValueError:
        print("❌ ID ต้องเป็นตัวเลข")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")

def main():
    """ฟังก์ชันหลัก"""
    while True:
        print("\n🗑️  ระบบลบ User")
        print("=" * 30)
        print("1. แสดงรายการ Users")
        print("2. ลบ User")
        print("3. ออกจากโปรแกรม")
        
        choice = input("\nเลือกตัวเลือก (1-3): ").strip()
        
        if choice == "1":
            list_users()
        elif choice == "2":
            delete_user()
        elif choice == "3":
            print("👋 ออกจากโปรแกรม")
            break
        else:
            print("❌ เลือกตัวเลือกไม่ถูกต้อง กรุณาลองใหม่")

if __name__ == "__main__":
    main()
