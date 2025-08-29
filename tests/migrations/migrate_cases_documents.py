#!/usr/bin/env python3
"""
Migration script สำหรับเพิ่มฟิลด์เอกสารในตาราง patient_case
"""

import sqlite3
import os

def migrate_cases_documents():
    """เพิ่มฟิลด์เอกสารในตาราง patient_case"""
    
    # เชื่อมต่อฐานข้อมูล - แก้ไขพาธให้ถูกต้อง
    db_path = 'instance/hospital.db'
    if not os.path.exists(db_path):
        print(f"ไม่พบฐานข้อมูล: {db_path}")
        print("💡 ตรวจสอบว่าฐานข้อมูลอยู่ใน instance/hospital.db หรือไม่")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # ตรวจสอบว่าฟิลด์มีอยู่แล้วหรือไม่
        cursor.execute("PRAGMA table_info(patient_case)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # เพิ่มฟิลด์ file_path ถ้ายังไม่มี
        if 'file_path' not in columns:
            cursor.execute("ALTER TABLE patient_case ADD COLUMN file_path VARCHAR(500)")
            print("✅ เพิ่มฟิลด์ file_path สำเร็จ")
        else:
            print("ℹ️  ฟิลด์ file_path มีอยู่แล้ว")
        
        # เพิ่มฟิลด์ file_size ถ้ายังไม่มี
        if 'file_size' not in columns:
            cursor.execute("ALTER TABLE patient_case ADD COLUMN file_size INTEGER")
            print("✅ เพิ่มฟิลด์ file_size สำเร็จ")
        else:
            print("ℹ️  ฟิลด์ file_size มีอยู่แล้ว")
        
        # เพิ่มฟิลด์ external_link ถ้ายังไม่มี
        if 'external_link' not in columns:
            cursor.execute("ALTER TABLE patient_case ADD COLUMN external_link VARCHAR(500)")
            print("✅ เพิ่มฟิลด์ external_link สำเร็จ")
        else:
            print("ℹ️  ฟิลด์ external_link มีอยู่แล้ว")
        
        # เพิ่มฟิลด์ link_type ถ้ายังไม่มี
        if 'link_type' not in columns:
            cursor.execute("ALTER TABLE patient_case ADD COLUMN link_type VARCHAR(50)")
            print("✅ เพิ่มฟิลด์ link_type สำเร็จ")
        else:
            print("ℹ️  ฟิลด์ link_type มีอยู่แล้ว")
        
        # Commit การเปลี่ยนแปลง
        conn.commit()
        print("\n🎉 Migration เสร็จสิ้น!")
        
        # แสดงโครงสร้างตารางปัจจุบัน
        print("\n📋 โครงสร้างตาราง patient_case ปัจจุบัน:")
        cursor.execute("PRAGMA table_info(patient_case)")
        for column in cursor.fetchall():
            print(f"  - {column[1]} ({column[2]})")
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        conn.rollback()
    
    finally:
        conn.close()

if __name__ == "__main__":
    print("🚀 เริ่มต้น Migration สำหรับฟิลด์เอกสาร...")
    migrate_cases_documents()
    print("\n✨ เสร็จสิ้น!")
