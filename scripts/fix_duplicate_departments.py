#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script สำหรับตรวจสอบและลบหน่วยงานซ้ำ
"""

import sqlite3
import os

def fix_duplicate_departments():
    """ตรวจสอบและลบหน่วยงานซ้ำ"""
    
    # เชื่อมต่อฐานข้อมูล
    db_path = 'instance/hospital.db'
    if not os.path.exists(db_path):
        print(f"ไม่พบฐานข้อมูลที่: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # ตรวจสอบหน่วยงานซ้ำ
        print("=== ตรวจสอบหน่วยงานซ้ำ ===")
        cursor.execute("""
            SELECT name, COUNT(*) as count, GROUP_CONCAT(id) as ids
            FROM department 
            GROUP BY name 
            HAVING COUNT(*) > 1
        """)
        
        duplicates = cursor.fetchall()
        
        if not duplicates:
            print("ไม่พบหน่วยงานซ้ำ")
            return
        
        print(f"พบหน่วยงานซ้ำ {len(duplicates)} รายการ:")
        for name, count, ids in duplicates:
            print(f"  - {name}: {count} รายการ (IDs: {ids})")
        
        # แสดงรายละเอียดหน่วยงานซ้ำ
        print("\n=== รายละเอียดหน่วยงานซ้ำ ===")
        for name, count, ids in duplicates:
            id_list = [int(x) for x in ids.split(',')]
            print(f"\n{name}:")
            
            for dept_id in id_list:
                cursor.execute("""
                    SELECT id, name, code, description, created_at
                    FROM department 
                    WHERE id = ?
                """, (dept_id,))
                
                dept = cursor.fetchone()
                if dept:
                    print(f"  ID {dept[0]}: {dept[1]} ({dept[2]}) - {dept[3]}")
                    
                    # ตรวจสอบข้อมูลที่เกี่ยวข้อง
                    cursor.execute("SELECT COUNT(*) FROM patient_case WHERE department_id = ?", (dept_id,))
                    case_count = cursor.fetchone()[0]
                    
                    cursor.execute("SELECT COUNT(*) FROM guideline WHERE department_id = ?", (dept_id,))
                    guideline_count = cursor.fetchone()[0]
                    
                    print(f"    - Patient Cases: {case_count}")
                    print(f"    - Guidelines: {guideline_count}")
        
        # ถามผู้ใช้ว่าต้องการลบหน่วยงานซ้ำหรือไม่
        print("\n=== ตัวเลือกการแก้ไข ===")
        print("1. ลบหน่วยงานซ้ำทั้งหมด (เก็บ ID ที่น้อยที่สุด)")
        print("2. ดูรายละเอียดเพิ่มเติม")
        print("3. ออกจากโปรแกรม")
        
        choice = input("\nเลือกตัวเลือก (1-3): ").strip()
        
        if choice == "1":
            # ลบหน่วยงานซ้ำ
            print("\n=== เริ่มลบหน่วยงานซ้ำ ===")
            
            for name, count, ids in duplicates:
                id_list = [int(x) for x in ids.split(',')]
                keep_id = min(id_list)  # เก็บ ID ที่น้อยที่สุด
                delete_ids = [x for x in id_list if x != keep_id]
                
                print(f"\nลบหน่วยงานซ้ำ: {name}")
                print(f"  เก็บ ID: {keep_id}")
                print(f"  ลบ IDs: {delete_ids}")
                
                for delete_id in delete_ids:
                    # ย้ายข้อมูลที่เกี่ยวข้องไปยังหน่วยงานที่เก็บไว้
                    print(f"    ย้ายข้อมูลจาก ID {delete_id} ไปยัง ID {keep_id}")
                    
                    # ย้าย PatientCase
                    cursor.execute("""
                        UPDATE patient_case 
                        SET department_id = ?, updated_at = datetime('now')
                        WHERE department_id = ?
                    """, (keep_id, delete_id))
                    
                    # ย้าย Guideline
                    cursor.execute("""
                        UPDATE guideline 
                        SET department_id = ?
                        WHERE department_id = ?
                    """, (keep_id, delete_id))
                    
                    # ย้าย Knowledge
                    cursor.execute("""
                        UPDATE knowledge 
                        SET department_id = ?
                        WHERE department_id = ?
                    """, (keep_id, delete_id))
                    
                    # ย้าย Activity
                    cursor.execute("""
                        UPDATE activity 
                        SET department_id = ?
                        WHERE department_id = ?
                    """, (keep_id, delete_id))
                    
                    # ย้าย Contact
                    cursor.execute("""
                        UPDATE contact 
                        SET department_id = ?
                        WHERE department_id = ?
                    """, (keep_id, delete_id))
                    
                    # ลบหน่วยงานซ้ำ
                    cursor.execute("DELETE FROM department WHERE id = ?", (delete_id,))
                    print(f"    ลบหน่วยงาน ID {delete_id} สำเร็จ")
                
                print(f"  เสร็จสิ้นการลบหน่วยงานซ้ำ: {name}")
            
            # Commit การเปลี่ยนแปลง
            conn.commit()
            print("\n✅ ลบหน่วยงานซ้ำเสร็จสิ้น")
            
        elif choice == "2":
            print("\n=== รายละเอียดเพิ่มเติม ===")
            print("ใช้คำสั่ง SQL เพื่อตรวจสอบข้อมูลเพิ่มเติม:")
            print("  SELECT * FROM department ORDER BY name, id;")
            print("  SELECT d.name, COUNT(pc.id) as case_count FROM department d LEFT JOIN patient_case pc ON d.id = pc.department_id GROUP BY d.id, d.name;")
            
        else:
            print("ออกจากโปรแกรม")
            
    except Exception as e:
        print(f"เกิดข้อผิดพลาด: {e}")
        conn.rollback()
        
    finally:
        conn.close()

if __name__ == "__main__":
    fix_duplicate_departments()
