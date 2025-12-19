#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utility functions และ helper functions สำหรับระบบ
"""

import os
import re
from datetime import datetime
from werkzeug.utils import secure_filename

def allowed_file(filename, allowed_extensions=None):
    """
    ตรวจสอบว่าไฟล์ที่อัปโหลดเป็นประเภทที่อนุญาตหรือไม่
    
    Args:
        filename (str): ชื่อไฟล์
        allowed_extensions (set): ประเภทไฟล์ที่อนุญาต
    
    Returns:
        bool: True ถ้าอนุญาต, False ถ้าไม่อนุญาต
    """
    if allowed_extensions is None:
        allowed_extensions = {'pdf', 'doc', 'docx', 'txt', 'jpg', 'jpeg', 'png', 'gif'}
    
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def format_file_size(size_bytes):
    """
    แปลงขนาดไฟล์จาก bytes เป็นรูปแบบที่อ่านง่าย
    
    Args:
        size_bytes (int): ขนาดไฟล์ในหน่วย bytes
    
    Returns:
        str: ขนาดไฟล์ในรูปแบบที่อ่านง่าย
    """
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024.0 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"

def sanitize_filename(filename):
    """
    ทำความสะอาดชื่อไฟล์เพื่อความปลอดภัย
    
    Args:
        filename (str): ชื่อไฟล์เดิม
    
    Returns:
        str: ชื่อไฟล์ที่ปลอดภัย
    """
    # ใช้ secure_filename ของ Werkzeug
    safe_filename = secure_filename(filename)
    
    # ถ้าชื่อไฟล์เป็นภาษาไทยหรือตัวอักษรพิเศษ อาจจะหายไป
    # ให้สร้างชื่อไฟล์ใหม่ด้วย timestamp
    if not safe_filename or safe_filename == '':
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        extension = filename.rsplit('.', 1)[1] if '.' in filename else 'txt'
        safe_filename = f"file_{timestamp}.{extension}"
    
    return safe_filename

def validate_hn(hn):
    """
    ตรวจสอบรูปแบบ HN (Hospital Number)
    
    Args:
        hn (str): หมายเลข HN
    
    Returns:
        bool: True ถ้ารูปแบบถูกต้อง, False ถ้าไม่ถูกต้อง
    """
    if not hn:
        return False
    
    # HN ควรเป็นตัวเลข 6-10 หลัก
    pattern = r'^\d{6,10}$'
    return bool(re.match(pattern, str(hn)))

def format_thai_date(date_obj):
    """
    แปลงวันที่เป็นรูปแบบภาษาไทย
    
    Args:
        date_obj (datetime): วันที่
    
    Returns:
        str: วันที่ในรูปแบบภาษาไทย
    """
    if not date_obj:
        return ""
    
    thai_months = [
        "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน",
        "พฤษภาคม", "มิถุนายน", "กรกฎาคม", "สิงหาคม",
        "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
    ]
    
    day = date_obj.day
    month = thai_months[date_obj.month - 1]
    year = date_obj.year + 543  # แปลงเป็นปี พ.ศ.
    
    return f"{day} {month} {year}"

def create_directory_if_not_exists(directory_path):
    """
    สร้างโฟลเดอร์ถ้ายังไม่มี
    
    Args:
        directory_path (str): path ของโฟลเดอร์
    
    Returns:
        bool: True ถ้าสร้างสำเร็จหรือมีอยู่แล้ว, False ถ้าเกิดข้อผิดพลาด
    """
    try:
        os.makedirs(directory_path, exist_ok=True)
        return True
    except Exception as e:
        print(f"Error creating directory {directory_path}: {e}")
        return False

def get_file_extension(filename):
    """
    ดึงนามสกุลไฟล์
    
    Args:
        filename (str): ชื่อไฟล์
    
    Returns:
        str: นามสกุลไฟล์ (ไม่รวมจุด)
    """
    if '.' in filename:
        return filename.rsplit('.', 1)[1].lower()
    return ''

def truncate_text(text, max_length=50):
    """
    ตัดข้อความให้สั้นลงถ้ายาวเกินไป
    
    Args:
        text (str): ข้อความ
        max_length (int): ความยาวสูงสุด
    
    Returns:
        str: ข้อความที่ตัดแล้ว
    """
    if not text:
        return ""
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length-3] + "..."