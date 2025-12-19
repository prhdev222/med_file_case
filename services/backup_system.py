import os
import shutil
import sqlite3
from datetime import datetime, timedelta
import logging
import time
import threading
from pathlib import Path
from dotenv import load_dotenv

# ตั้งค่า logging
# ตรวจสอบว่า run บน serverless platform หรือไม่
IS_VERCEL = os.getenv('VERCEL') == '1'
IS_NETLIFY = os.getenv('NETLIFY') == 'true'
IS_SERVERLESS = IS_VERCEL or IS_NETLIFY

# ใน serverless environment ไม่สามารถเขียนไฟล์ได้ ใช้ StreamHandler เท่านั้น
if IS_SERVERLESS:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )
else:
    # ใน local environment ใช้ทั้ง FileHandler และ StreamHandler
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("backup.log", encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

# แก้ไขปัญหา encoding สำหรับ console output บน Windows
import sys
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
logger = logging.getLogger('backup_system')

# โหลด environment variables
load_dotenv()

# ค่าเริ่มต้นสำหรับการสำรองข้อมูล
DEFAULT_BACKUP_DIR = os.getenv('BACKUP_DIR', 'storage/backups')
DEFAULT_DB_PATH = os.getenv('DATABASE_URL', 'sqlite:///hospital.db').replace('sqlite:///', '')
# แก้ไข path ให้ชี้ไปที่ instance/hospital.db ถ้าไฟล์อยู่ที่นั่น
if not os.path.exists(DEFAULT_DB_PATH) and os.path.exists('instance/hospital.db'):
    DEFAULT_DB_PATH = 'instance/hospital.db'
DEFAULT_UPLOAD_DIR = os.getenv('UPLOAD_FOLDER', 'storage/uploads')
DEFAULT_BACKUP_INTERVAL = int(os.getenv('BACKUP_INTERVAL_HOURS', 78))  # ค่าเริ่มต้น 78 ชั่วโมง
DEFAULT_BACKUP_KEEP_DAYS = int(os.getenv('BACKUP_KEEP_DAYS', 30))  # ค่าเริ่มต้น 30 วัน

class BackupSystem:
    """ระบบสำรองข้อมูลสำหรับฐานข้อมูล SQLite และไฟล์ที่อัปโหลด"""
    
    def __init__(self, 
                 backup_dir=DEFAULT_BACKUP_DIR, 
                 db_path=DEFAULT_DB_PATH, 
                 upload_dir=DEFAULT_UPLOAD_DIR,
                 backup_interval=DEFAULT_BACKUP_INTERVAL):
        """กำหนดค่าเริ่มต้นสำหรับระบบสำรองข้อมูล"""
        self.backup_dir = backup_dir
        self.db_path = db_path
        self.upload_dir = upload_dir
        self.backup_interval = backup_interval  # ชั่วโมง
        self.timer = None
        
        # สร้างโฟลเดอร์สำรองข้อมูลถ้ายังไม่มี
        self._create_backup_directories()
    
    def _create_backup_directories(self):
        """สร้างโฟลเดอร์สำหรับเก็บข้อมูลสำรอง"""
        # สร้างโฟลเดอร์หลัก
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # สร้างโฟลเดอร์สำหรับฐานข้อมูล
        os.makedirs(os.path.join(self.backup_dir, 'database'), exist_ok=True)
        
        # สร้างโฟลเดอร์สำหรับไฟล์อัปโหลด
        os.makedirs(os.path.join(self.backup_dir, 'uploads'), exist_ok=True)
    
    def backup_database(self):
        """สำรองฐานข้อมูล SQLite"""
        try:
            # ตรวจสอบว่าไฟล์ฐานข้อมูลมีอยู่จริง
            if not os.path.exists(self.db_path):
                logger.error(f"ไม่พบไฟล์ฐานข้อมูล: {self.db_path}")
                return False
            
            # สร้างชื่อไฟล์สำรองข้อมูลด้วยวันที่และเวลาปัจจุบัน
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"hospital_db_backup_{timestamp}.db"
            backup_path = os.path.join(self.backup_dir, 'database', backup_filename)
            
            # สำรองฐานข้อมูลโดยใช้ sqlite3 backup API
            source = sqlite3.connect(self.db_path)
            destination = sqlite3.connect(backup_path)
            
            with destination:
                source.backup(destination)
            
            source.close()
            destination.close()
            
            logger.info(f"สำรองฐานข้อมูลสำเร็จ: {backup_path}")
            return True
        
        except Exception as e:
            logger.error(f"เกิดข้อผิดพลาดในการสำรองฐานข้อมูล: {str(e)}")
            return False
    
    def backup_uploads(self):
        """สำรองไฟล์ที่อัปโหลดทั้งหมด"""
        try:
            # ตรวจสอบว่าโฟลเดอร์อัปโหลดมีอยู่จริง
            if not os.path.exists(self.upload_dir):
                logger.error(f"ไม่พบโฟลเดอร์อัปโหลด: {self.upload_dir}")
                return False
            
            # สร้างชื่อโฟลเดอร์สำรองข้อมูลด้วยวันที่และเวลาปัจจุบัน
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_folder = f"uploads_backup_{timestamp}"
            backup_path = os.path.join(self.backup_dir, 'uploads', backup_folder)
            
            # สร้างโฟลเดอร์สำรองข้อมูล
            os.makedirs(backup_path, exist_ok=True)
            
            # คัดลอกไฟล์ทั้งหมดจากโฟลเดอร์อัปโหลด
            shutil.copytree(self.upload_dir, backup_path, dirs_exist_ok=True)
            
            logger.info(f"สำรองไฟล์อัปโหลดสำเร็จ: {backup_path}")
            return True
        
        except Exception as e:
            logger.error(f"เกิดข้อผิดพลาดในการสำรองไฟล์อัปโหลด: {str(e)}")
            return False
    
    def run_backup(self):
        """ดำเนินการสำรองข้อมูลทั้งหมด"""
        logger.info("เริ่มการสำรองข้อมูล...")
        db_success = self.backup_database()
        uploads_success = self.backup_uploads()
        
        if db_success and uploads_success:
            logger.info("การสำรองข้อมูลทั้งหมดสำเร็จ")
            return True
        else:
            logger.warning("การสำรองข้อมูลบางส่วนล้มเหลว")
            return False
    
    def cleanup_old_backups(self, keep_days=None):
        """ลบข้อมูลสำรองที่เก่าเกินกว่าจำนวนวันที่กำหนด"""
        if keep_days is None:
            keep_days = DEFAULT_BACKUP_KEEP_DAYS
        try:
            # คำนวณวันที่ตัดออก
            cutoff_date = datetime.now() - timedelta(days=keep_days)
            
            # ลบไฟล์ฐานข้อมูลเก่า
            db_backup_dir = os.path.join(self.backup_dir, 'database')
            if os.path.exists(db_backup_dir):
                for filename in os.listdir(db_backup_dir):
                    file_path = os.path.join(db_backup_dir, filename)
                    if os.path.isfile(file_path):
                        # ตรวจสอบวันที่สร้างไฟล์
                        file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                        if file_time < cutoff_date:
                            os.remove(file_path)
                            logger.info(f"ลบไฟล์สำรองฐานข้อมูลเก่า: {filename}")
            
            # ลบโฟลเดอร์อัปโหลดเก่า
            uploads_backup_dir = os.path.join(self.backup_dir, 'uploads')
            if os.path.exists(uploads_backup_dir):
                for foldername in os.listdir(uploads_backup_dir):
                    folder_path = os.path.join(uploads_backup_dir, foldername)
                    if os.path.isdir(folder_path):
                        # ตรวจสอบวันที่สร้างโฟลเดอร์
                        folder_time = datetime.fromtimestamp(os.path.getctime(folder_path))
                        if folder_time < cutoff_date:
                            shutil.rmtree(folder_path)
                            logger.info(f"ลบโฟลเดอร์สำรองไฟล์อัปโหลดเก่า: {foldername}")
            
            logger.info(f"ลบข้อมูลสำรองที่เก่ากว่า {keep_days} วันเรียบร้อยแล้ว")
            return True
        
        except Exception as e:
            logger.error(f"เกิดข้อผิดพลาดในการลบข้อมูลสำรองเก่า: {str(e)}")
            return False
    
    def start_scheduled_backup(self):
        """เริ่มการสำรองข้อมูลตามกำหนดเวลา"""
        # ตั้งเวลาสำหรับการสำรองข้อมูลครั้งถัดไป
        hours_in_seconds = self.backup_interval * 3600
        self.timer = threading.Timer(hours_in_seconds, self._scheduled_backup_task)
        self.timer.daemon = True
        self.timer.start()
        
        logger.info(f"ตั้งเวลาสำรองข้อมูลครั้งถัดไปในอีก {self.backup_interval} ชั่วโมง")
    
    def _scheduled_backup_task(self):
        """ฟังก์ชันสำหรับทำ backup และตั้งเวลาครั้งถัดไป"""
        self.run_backup()
        
        # ตั้งเวลาสำหรับการสำรองข้อมูลครั้งถัดไป
        hours_in_seconds = self.backup_interval * 3600
        self.timer = threading.Timer(hours_in_seconds, self._scheduled_backup_task)
        self.timer.daemon = True
        self.timer.start()
        
        logger.info(f"ตั้งเวลาสำรองข้อมูลครั้งถัดไปในอีก {self.backup_interval} ชั่วโมง")
    
    def stop_scheduled_backup(self):
        """หยุดการสำรองข้อมูลตามกำหนดเวลา"""
        if self.timer:
            self.timer.cancel()
            logger.info("หยุดการสำรองข้อมูลตามกำหนดเวลาแล้ว")

# ฟังก์ชันสำหรับเรียกใช้งานจากภายนอก
def run_backup_now():
    """ดำเนินการสำรองข้อมูลทันที"""
    backup_system = BackupSystem()
    return backup_system.run_backup()

def start_scheduled_backup(interval_hours=DEFAULT_BACKUP_INTERVAL):
    """เริ่มการสำรองข้อมูลตามกำหนดเวลา"""
    backup_system = BackupSystem(backup_interval=interval_hours)
    backup_system.start_scheduled_backup()
    return backup_system

# ถ้าเรียกใช้ไฟล์นี้โดยตรง
if __name__ == "__main__":
    # ดำเนินการสำรองข้อมูลทันที (เฉพาะเมื่อเรียกใช้ไฟล์โดยตรง)
    backup_system = BackupSystem()
    backup_system.run_backup()
    
    # ลบข้อมูลสำรองที่เก่าเกินกว่าจำนวนวันที่กำหนดใน .env
    backup_system.cleanup_old_backups()