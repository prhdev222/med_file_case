from flask import Blueprint, jsonify, request
from flask_login import login_required
from datetime import datetime, timezone, timedelta
from models import db, Department, PatientCase

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/notifications/recent-patients')
@login_required
def get_recent_patients():
    """API สำหรับดึงข้อมูลผู้ป่วยใหม่ในช่วง 3 วันก่อน"""
    try:
        # คำนวณวันที่ 3 วันก่อน
        three_days_ago = datetime.now(timezone.utc) - timedelta(days=3)
        
        # ดึงข้อมูลผู้ป่วยที่สร้างในช่วง 3 วันก่อน
        recent_patients = db.session.query(PatientCase).join(Department).filter(
            PatientCase.created_at >= three_days_ago,
            PatientCase.is_deleted == False
        ).order_by(PatientCase.created_at.desc()).all()
        
        # แปลงข้อมูลเป็น JSON
        patients_data = []
        for patient in recent_patients:
            patients_data.append({
                'id': patient.id,
                'hn': patient.hn,
                'first_name': patient.first_name,
                'last_name': patient.last_name,
                'department_name': patient.department.name,
                'department_code': patient.department.code,
                'created_at': patient.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'case_date': patient.case_date.strftime('%Y-%m-%d') if patient.case_date else None
            })
        
        return jsonify({
            'success': True,
            'data': patients_data,
            'count': len(patients_data)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/notifications/recent-patients-public')
def get_recent_patients_public():
    """API สาธารณะสำหรับดึงข้อมูลผู้ป่วยใหม่ (ไม่แสดงข้อมูลส่วนตัว)"""
    try:
        # คำนวณวันที่ 7 วันก่อน
        seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
        
        # ดึงข้อมูลผู้ป่วยที่สร้างในช่วง 7 วันก่อน (เฉพาะข้อมูลที่ไม่ระบุตัวตน)
        recent_patients = db.session.query(PatientCase).join(Department).filter(
            PatientCase.created_at >= seven_days_ago,
            PatientCase.is_deleted == False
        ).order_by(PatientCase.created_at.desc()).all()
        
        # แปลงข้อมูลเป็น JSON (ไม่แสดงข้อมูลส่วนตัว)
        patients_data = []
        for patient in recent_patients:
            patients_data.append({
                'department_name': patient.department.name,
                'department_code': patient.department.code,
                'created_date': patient.created_at.strftime('%Y-%m-%d'),
                'case_date': patient.case_date.strftime('%Y-%m-%d') if patient.case_date else None
            })
        
        return jsonify({
            'success': True,
            'data': patients_data,
            'count': len(patients_data)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'เกิดข้อผิดพลาดในการดึงข้อมูล'
        }), 500

@api_bp.route('/public/stats')
def get_public_stats():
    """API สำหรับดึงสถิติสาธารณะ"""
    try:
        # จำนวน cases ทั้งหมด
        total_cases = db.session.query(PatientCase).filter_by(is_deleted=False).count()
        
        # จำนวน cases ตามหน่วยงาน
        dept_stats = []
        departments = db.session.query(Department).all()
        
        for dept in departments:
            case_count = db.session.query(PatientCase).filter_by(
                department_id=dept.id, 
                is_deleted=False
            ).count()
            
            if case_count > 0:
                dept_stats.append({
                    'department_name': dept.name,
                    'department_code': dept.code,
                    'case_count': case_count
                })
        
        # เรียงตามจำนวน case จากมากไปน้อย
        dept_stats.sort(key=lambda x: x['case_count'], reverse=True)
        
        return jsonify({
            'success': True,
            'data': {
                'total_cases': total_cases,
                'department_stats': dept_stats
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'เกิดข้อผิดพลาดในการดึงข้อมูลสถิติ'
        }), 500