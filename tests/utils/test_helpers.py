#!/usr/bin/env python3
"""
Test Helper Functions
ฟังก์ชันช่วยการทดสอบระบบจัดการข้อมูลผู้ป่วย
"""

import sqlite3
import os
from datetime import datetime, timedelta
import random

def create_test_database():
    """สร้างฐานข้อมูลทดสอบ"""
    db_path = 'test_hospital.db'
    
    # ลบฐานข้อมูลเก่าถ้ามี
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # สร้างตารางทดสอบ
    cursor.execute('''
        CREATE TABLE department (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code VARCHAR(10) NOT NULL UNIQUE,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE admin_user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(50) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            email VARCHAR(100),
            created_at DATETIME NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE patient_case (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hn VARCHAR(20) NOT NULL,
            first_name VARCHAR(100) NOT NULL,
            last_name VARCHAR(100) NOT NULL,
            department_id INTEGER NOT NULL,
            case_date DATE NOT NULL,
            notes TEXT,
            file_path VARCHAR(500),
            file_size INTEGER,
            external_link VARCHAR(500),
            link_type VARCHAR(50),
            created_at DATETIME NOT NULL,
            created_by INTEGER,
            updated_at DATETIME NOT NULL,
            is_deleted BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (department_id) REFERENCES department(id),
            FOREIGN KEY (created_by) REFERENCES admin_user(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE case_audit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id INTEGER NOT NULL,
            action VARCHAR(20) NOT NULL,
            user_id INTEGER,
            ip_address VARCHAR(45),
            created_at DATETIME NOT NULL,
            FOREIGN KEY (case_id) REFERENCES patient_case(id),
            FOREIGN KEY (user_id) REFERENCES admin_user(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    
    return db_path

def populate_test_data(db_path):
    """เพิ่มข้อมูลทดสอบ"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # เพิ่ม admin user
    cursor.execute('''
        INSERT INTO admin_user (username, password_hash, email, created_at)
        VALUES (?, ?, ?, ?)
    ''', ('admin', 'test_hash', 'admin@test.com', datetime.now()))
    
    # เพิ่มหน่วยงาน
    departments = [
        ('DM', 'หน่วยเบาหวาน', 'หน่วยงานดูแลผู้ป่วยเบาหวาน'),
        ('CKD', 'หน่วยไตเรื้อรัง', 'หน่วยงานดูแลผู้ป่วยไตเรื้อรัง'),
        ('COPD', 'หน่วยโรคปอดอุดกั้นเรื้อรัง', 'หน่วยงานดูแลผู้ป่วยโรคปอด'),
        ('HTN', 'หน่วยความดันโลหิตสูง', 'หน่วยงานดูแลผู้ป่วยความดันโลหิตสูง'),
        ('OBESITY', 'หน่วยโรคอ้วน', 'หน่วยงานดูแลผู้ป่วยโรคอ้วน')
    ]
    
    for dept in departments:
        cursor.execute('''
            INSERT INTO department (code, name, description, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (dept[0], dept[1], dept[2], datetime.now(), datetime.now()))
    
    # เพิ่มผู้ป่วยทดสอบ
    test_cases = [
        ('1234567', 'สมชาย', 'ใจดี', 'DM', '2024-01-15', 'ผู้ป่วยใหม่'),
        ('1234568', 'สมหญิง', 'รักดี', 'CKD', '2024-01-16', 'ตรวจติดตาม'),
        ('1234569', 'สมศักดิ์', 'มั่นคง', 'COPD', '2024-01-17', ''),
        ('1234570', 'สมศรี', 'สุขใจ', 'HTN', '2024-01-18', 'ปรับยา'),
        ('1234571', 'สมชาย', 'ใจเย็น', 'OBESITY', '2024-01-19', 'ลดน้ำหนัก')
    ]
    
    for case in test_cases:
        cursor.execute('''
            INSERT INTO patient_case (hn, first_name, last_name, department_id, case_date, notes, created_at, created_by, updated_at)
            VALUES (?, ?, ?, (SELECT id FROM department WHERE code = ?), ?, ?, ?, 1, ?)
        ''', (case[0], case[1], case[2], case[3], case[4], case[5], datetime.now(), datetime.now()))
    
    conn.commit()
    conn.close()

def cleanup_test_database(db_path):
    """ลบฐานข้อมูลทดสอบ"""
    if os.path.exists(db_path):
        os.remove(db_path)

def get_random_hn():
    """สร้าง HN สุ่ม"""
    return str(random.randint(1000000, 9999999))

def get_random_name():
    """สร้างชื่อสุ่ม"""
    first_names = ['สมชาย', 'สมหญิง', 'สมศักดิ์', 'สมศรี', 'สมปอง', 'สมใจ', 'สมบูรณ์', 'สมควร']
    last_names = ['ใจดี', 'รักดี', 'มั่นคง', 'สุขใจ', 'ใจเย็น', 'ใจกว้าง', 'ใจเย็น', 'ใจดี']
    
    return random.choice(first_names), random.choice(last_names)

def get_random_department():
    """สร้างหน่วยงานสุ่ม"""
    departments = ['DM', 'CKD', 'COPD', 'HTN', 'OBESITY']
    return random.choice(departments)

def create_test_case_data(count=10):
    """สร้างข้อมูลผู้ป่วยทดสอบ"""
    test_data = []
    
    for i in range(count):
        hn = get_random_hn()
        first_name, last_name = get_random_name()
        department = get_random_department()
        case_date = datetime.now() - timedelta(days=random.randint(0, 30))
        
        test_data.append({
            'hn': hn,
            'first_name': first_name,
            'last_name': last_name,
            'department': department,
            'case_date': case_date.strftime('%Y-%m-%d'),
            'notes': f'ข้อมูลทดสอบ #{i+1}'
        })
    
    return test_data
