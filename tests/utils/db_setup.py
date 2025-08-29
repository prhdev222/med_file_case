#!/usr/bin/env python3
"""
Database Setup for Testing
การตั้งค่าฐานข้อมูลสำหรับการทดสอบ
"""

import sqlite3
import os
from datetime import datetime
from .test_helpers import create_test_database, populate_test_data, cleanup_test_database

class TestDatabaseManager:
    """จัดการฐานข้อมูลทดสอบ"""
    
    def __init__(self, db_path='test_hospital.db'):
        self.db_path = db_path
        self.original_db_path = 'instance/hospital.db'
    
    def setup_test_database(self):
        """ตั้งค่าฐานข้อมูลทดสอบ"""
        print("🔧 ตั้งค่าฐานข้อมูลทดสอบ...")
        
        # สร้างฐานข้อมูลทดสอบ
        create_test_database()
        
        # เพิ่มข้อมูลทดสอบ
        populate_test_data(self.db_path)
        
        print("✅ ตั้งค่าฐานข้อมูลทดสอบเสร็จสิ้น")
        return self.db_path
    
    def cleanup_test_database(self):
        """ลบฐานข้อมูลทดสอบ"""
        print("🧹 ลบฐานข้อมูลทดสอบ...")
        cleanup_test_database(self.db_path)
        print("✅ ลบฐานข้อมูลทดสอบเสร็จสิ้น")
    
    def backup_original_database(self):
        """สำรองฐานข้อมูลเดิม"""
        if os.path.exists(self.original_db_path):
            backup_path = f"{self.original_db_path}.backup"
            print(f"💾 สำรองฐานข้อมูลเดิมไปที่: {backup_path}")
            
            conn = sqlite3.connect(self.original_db_path)
            backup_conn = sqlite3.connect(backup_path)
            conn.backup(backup_conn)
            
            conn.close()
            backup_conn.close()
            
            return backup_path
        return None
    
    def restore_original_database(self, backup_path):
        """กู้คืนฐานข้อมูลเดิม"""
        if backup_path and os.path.exists(backup_path):
            print(f"🔄 กู้คืนฐานข้อมูลเดิมจาก: {backup_path}")
            
            backup_conn = sqlite3.connect(backup_path)
            conn = sqlite3.connect(self.original_db_path)
            backup_conn.backup(conn)
            
            backup_conn.close()
            conn.close()
            
            # ลบไฟล์สำรอง
            os.remove(backup_path)
            print("✅ กู้คืนฐานข้อมูลเดิมเสร็จสิ้น")
    
    def switch_to_test_database(self):
        """เปลี่ยนไปใช้ฐานข้อมูลทดสอบ"""
        if os.path.exists(self.original_db_path):
            # เปลี่ยนชื่อฐานข้อมูลเดิม
            temp_path = f"{self.original_db_path}.temp"
            os.rename(self.original_db_path, temp_path)
            
            # คัดลอกฐานข้อมูลทดสอบไปยังตำแหน่งเดิม
            import shutil
            shutil.copy2(self.db_path, self.original_db_path)
            
            return temp_path
        return None
    
    def switch_back_to_original(self, temp_path):
        """เปลี่ยนกลับไปใช้ฐานข้อมูลเดิม"""
        if temp_path and os.path.exists(temp_path):
            # ลบฐานข้อมูลทดสอบ
            if os.path.exists(self.original_db_path):
                os.remove(self.original_db_path)
            
            # เปลี่ยนชื่อฐานข้อมูลเดิมกลับ
            os.rename(temp_path, self.original_db_path)
            print("✅ เปลี่ยนกลับไปใช้ฐานข้อมูลเดิมแล้ว")

def setup_test_environment():
    """ตั้งค่าสภาพแวดล้อมการทดสอบ"""
    print("🚀 ตั้งค่าสภาพแวดล้อมการทดสอบ...")
    
    # สร้างโฟลเดอร์ที่จำเป็น
    os.makedirs('instance', exist_ok=True)
    os.makedirs('storage/uploads/cases', exist_ok=True)
    os.makedirs('tests/fixtures/sample_files', exist_ok=True)
    
    # สร้างไฟล์ตัวอย่าง
    sample_files = [
        'tests/fixtures/sample_files/sample_patient.pdf',
        'tests/fixtures/sample_files/sample_image.jpg',
        'tests/fixtures/sample_files/sample_document.docx'
    ]
    
    for file_path in sample_files:
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                f.write(f"Sample file: {file_path}")
    
    print("✅ ตั้งค่าสภาพแวดล้อมการทดสอบเสร็จสิ้น")

def cleanup_test_environment():
    """ลบสภาพแวดล้อมการทดสอบ"""
    print("🧹 ลบสภาพแวดล้อมการทดสอบ...")
    
    # ลบไฟล์ตัวอย่าง
    sample_files = [
        'tests/fixtures/sample_files/sample_patient.pdf',
        'tests/fixtures/sample_files/sample_image.jpg',
        'tests/fixtures/sample_files/sample_document.docx'
    ]
    
    for file_path in sample_files:
        if os.path.exists(file_path):
            os.remove(file_path)
    
    print("✅ ลบสภาพแวดล้อมการทดสอบเสร็จสิ้น")
