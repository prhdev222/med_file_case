from flask import Blueprint, jsonify, request, g
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timezone, timedelta
import os
import json
from models import db, Department, Guideline, Knowledge, Activity, Contact, PatientCase, CaseAudit, AdminUser
from services.backup_system import BackupSystem
from utils.jwt_utils import JWTManager, jwt_required, admin_required, get_current_user

admin_api_bp = Blueprint('admin_api', __name__, url_prefix='/api/admin')

# Authentication API endpoints
@admin_api_bp.route('/auth/login', methods=['POST'])
def api_admin_login():
    """API endpoint for admin login"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'ไม่พบข้อมูลการเข้าสู่ระบบ'}), 400
        
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'success': False, 'message': 'กรุณากรอกชื่อผู้ใช้และรหัสผ่าน'}), 400
        
        user = db.session.query(AdminUser).filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            user.last_login = datetime.now(timezone.utc)
            db.session.commit()
            
            # Generate JWT token
            token = JWTManager.generate_token(
                user.id,
                user.username,
                user.role
            )
            
            return jsonify({
                'success': True,
                'message': 'เข้าสู่ระบบสำเร็จ',
                'token': token,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role,
                    'last_login': user.last_login.isoformat() if user.last_login else None
                }
            })
        else:
            return jsonify({'success': False, 'message': 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง'}), 401
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'เกิดข้อผิดพลาด: {str(e)}'}), 500

# Contacts API endpoints
@admin_api_bp.route('/contacts', methods=['GET'])
@jwt_required
def api_get_contacts():
    """API endpoint to get all contacts"""
    try:
        search = request.args.get('search', '')
        department_id = request.args.get('department_id', type=int)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        query = db.session.query(Contact).filter_by(is_deleted=False)
        
        if search:
            query = query.filter(
                db.or_(
                    Contact.first_name.contains(search),
                    Contact.last_name.contains(search),
                    Contact.email.contains(search),
                    Contact.phone.contains(search)
                )
            )
        
        if department_id:
            query = query.filter_by(department_id=department_id)
        
        contacts = query.order_by(Contact.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        contacts_data = []
        for contact in contacts.items:
            contacts_data.append({
                'id': contact.id,
                'first_name': contact.first_name,
                'last_name': contact.last_name,
                'email': contact.email,
                'phone': contact.phone,
                'position': contact.position,
                'department_id': contact.department_id,
                'department_name': contact.department.name if contact.department else None,
                'created_at': contact.created_at.isoformat() if contact.created_at else None
            })
        
        return jsonify({
            'success': True,
            'contacts': contacts_data,
            'pagination': {
                'page': contacts.page,
                'pages': contacts.pages,
                'per_page': contacts.per_page,
                'total': contacts.total
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'เกิดข้อผิดพลาด: {str(e)}'}), 500

@admin_api_bp.route('/contacts', methods=['POST'])
@jwt_required
def api_create_contact():
    """API endpoint to create a new contact"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'ไม่พบข้อมูลรายชื่อติดต่อ'}), 400
        
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        phone = data.get('phone')
        position = data.get('position', '')
        department_id = data.get('department_id')
        
        if not first_name or not last_name:
            return jsonify({'success': False, 'message': 'กรุณากรอกชื่อและนามสกุล'}), 400
        
        if not department_id:
            return jsonify({'success': False, 'message': 'กรุณาเลือกแผนก'}), 400
        
        # Check if department exists
        dept = db.session.query(Department).get(department_id)
        if not dept:
            return jsonify({'success': False, 'message': 'ไม่พบแผนกที่เลือก'}), 400
        
        new_contact = Contact(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            position=position,
            department_id=department_id,
            created_at=datetime.now(timezone.utc),
            is_deleted=False
        )
        
        db.session.add(new_contact)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'เพิ่มรายชื่อติดต่อสำเร็จ',
            'contact': {
                'id': new_contact.id,
                'first_name': new_contact.first_name,
                'last_name': new_contact.last_name,
                'email': new_contact.email,
                'phone': new_contact.phone,
                'position': new_contact.position,
                'department_id': new_contact.department_id,
                'department_name': dept.name,
                'created_at': new_contact.created_at.isoformat()
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'เกิดข้อผิดพลาด: {str(e)}'}), 500

@admin_api_bp.route('/contacts/<int:contact_id>', methods=['PUT'])
@jwt_required
def api_update_contact(contact_id):
    """API endpoint to update a contact"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'ไม่พบข้อมูลรายชื่อติดต่อ'}), 400
        
        contact = db.session.query(Contact).filter_by(id=contact_id, is_deleted=False).first()
        if not contact:
            return jsonify({'success': False, 'message': 'ไม่พบรายชื่อติดต่อที่ต้องการแก้ไข'}), 404
        
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        phone = data.get('phone')
        position = data.get('position', '')
        department_id = data.get('department_id')
        
        if not first_name or not last_name:
            return jsonify({'success': False, 'message': 'กรุณากรอกชื่อและนามสกุล'}), 400
        
        if not department_id:
            return jsonify({'success': False, 'message': 'กรุณาเลือกแผนก'}), 400
        
        # Check if department exists
        dept = db.session.query(Department).get(department_id)
        if not dept:
            return jsonify({'success': False, 'message': 'ไม่พบแผนกที่เลือก'}), 400
        
        contact.first_name = first_name
        contact.last_name = last_name
        contact.email = email
        contact.phone = phone
        contact.position = position
        contact.department_id = department_id
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'แก้ไขรายชื่อติดต่อสำเร็จ',
            'contact': {
                'id': contact.id,
                'first_name': contact.first_name,
                'last_name': contact.last_name,
                'email': contact.email,
                'phone': contact.phone,
                'position': contact.position,
                'department_id': contact.department_id,
                'department_name': dept.name,
                'created_at': contact.created_at.isoformat() if contact.created_at else None
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'เกิดข้อผิดพลาด: {str(e)}'}), 500

@admin_api_bp.route('/contacts/<int:contact_id>', methods=['DELETE'])
@jwt_required
def api_delete_contact(contact_id):
    """API endpoint to delete a contact"""
    try:
        contact = db.session.query(Contact).filter_by(id=contact_id, is_deleted=False).first()
        if not contact:
            return jsonify({'success': False, 'message': 'ไม่พบรายชื่อติดต่อที่ต้องการลบ'}), 404
        
        contact.is_deleted = True
        contact.deleted_at = datetime.now(timezone.utc)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'ลบรายชื่อติดต่อสำเร็จ'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'เกิดข้อผิดพลาด: {str(e)}'}), 500

# Cases API endpoints
@admin_api_bp.route('/cases', methods=['GET'])
@jwt_required
def api_get_cases():
    """API endpoint to get all cases"""
    try:
        search = request.args.get('search', '')
        department_id = request.args.get('department_id', type=int)
        status = request.args.get('status')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        query = db.session.query(PatientCase).filter_by(is_deleted=False)
        
        if search:
            query = query.filter(
                db.or_(
                    PatientCase.hn.contains(search),
                    PatientCase.first_name.contains(search),
                    PatientCase.last_name.contains(search)
                )
            )
        
        if department_id:
            query = query.filter_by(department_id=department_id)
        
        if status:
            query = query.filter_by(status=status)
        
        cases = query.order_by(PatientCase.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        cases_data = []
        for case in cases.items:
            cases_data.append({
                'id': case.id,
                'hn': case.hn,
                'first_name': case.first_name,
                'last_name': case.last_name,
                'age': case.age,
                'gender': case.gender,
                'diagnosis': case.diagnosis,
                'treatment': case.treatment,
                'status': case.status,
                'case_date': case.case_date.isoformat() if case.case_date else None,
                'department_id': case.department_id,
                'department_name': case.department.name if case.department else None,
                'created_at': case.created_at.isoformat() if case.created_at else None
            })
        
        return jsonify({
            'success': True,
            'cases': cases_data,
            'pagination': {
                'page': cases.page,
                'pages': cases.pages,
                'per_page': cases.per_page,
                'total': cases.total
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'เกิดข้อผิดพลาด: {str(e)}'}), 500

@admin_api_bp.route('/cases', methods=['POST'])
@jwt_required
def api_create_case():
    """API endpoint to create a new case"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'ไม่พบข้อมูลเคส'}), 400
        
        hn = data.get('hn')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        age = data.get('age')
        gender = data.get('gender')
        diagnosis = data.get('diagnosis')
        treatment = data.get('treatment')
        department_id = data.get('department_id')
        case_date = data.get('case_date')
        
        if not hn or not first_name or not last_name:
            return jsonify({'success': False, 'message': 'กรุณากรอกข้อมูลที่จำเป็น'}), 400
        
        if not department_id:
            return jsonify({'success': False, 'message': 'กรุณาเลือกแผนก'}), 400
        
        # Check if department exists
        dept = db.session.query(Department).get(department_id)
        if not dept:
            return jsonify({'success': False, 'message': 'ไม่พบแผนกที่เลือก'}), 400
        
        # Parse case_date if provided
        parsed_case_date = None
        if case_date:
            try:
                parsed_case_date = datetime.fromisoformat(case_date.replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'success': False, 'message': 'รูปแบบวันที่ไม่ถูกต้อง'}), 400
        
        new_case = PatientCase(
            hn=hn,
            first_name=first_name,
            last_name=last_name,
            age=age,
            gender=gender,
            diagnosis=diagnosis,
            treatment=treatment,
            department_id=department_id,
            case_date=parsed_case_date,
            status='active',
            created_at=datetime.now(timezone.utc),
            is_deleted=False
        )
        
        db.session.add(new_case)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'เพิ่มเคสสำเร็จ',
            'case': {
                'id': new_case.id,
                'hn': new_case.hn,
                'first_name': new_case.first_name,
                'last_name': new_case.last_name,
                'age': new_case.age,
                'gender': new_case.gender,
                'diagnosis': new_case.diagnosis,
                'treatment': new_case.treatment,
                'status': new_case.status,
                'case_date': new_case.case_date.isoformat() if new_case.case_date else None,
                'department_id': new_case.department_id,
                'department_name': dept.name,
                'created_at': new_case.created_at.isoformat()
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'เกิดข้อผิดพลาด: {str(e)}'}), 500

@admin_api_bp.route('/cases/<int:case_id>', methods=['PUT'])
@jwt_required
def api_update_case(case_id):
    """API endpoint to update a case"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'ไม่พบข้อมูลเคส'}), 400
        
        case = db.session.query(PatientCase).filter_by(id=case_id, is_deleted=False).first()
        if not case:
            return jsonify({'success': False, 'message': 'ไม่พบเคสที่ต้องการแก้ไข'}), 404
        
        hn = data.get('hn')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        age = data.get('age')
        gender = data.get('gender')
        diagnosis = data.get('diagnosis')
        treatment = data.get('treatment')
        department_id = data.get('department_id')
        case_date = data.get('case_date')
        status = data.get('status')
        
        if not hn or not first_name or not last_name:
            return jsonify({'success': False, 'message': 'กรุณากรอกข้อมูลที่จำเป็น'}), 400
        
        if not department_id:
            return jsonify({'success': False, 'message': 'กรุณาเลือกแผนก'}), 400
        
        # Check if department exists
        dept = db.session.query(Department).get(department_id)
        if not dept:
            return jsonify({'success': False, 'message': 'ไม่พบแผนกที่เลือก'}), 400
        
        # Parse case_date if provided
        parsed_case_date = None
        if case_date:
            try:
                parsed_case_date = datetime.fromisoformat(case_date.replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'success': False, 'message': 'รูปแบบวันที่ไม่ถูกต้อง'}), 400
        
        case.hn = hn
        case.first_name = first_name
        case.last_name = last_name
        case.age = age
        case.gender = gender
        case.diagnosis = diagnosis
        case.treatment = treatment
        case.department_id = department_id
        case.case_date = parsed_case_date
        if status:
            case.status = status
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'แก้ไขเคสสำเร็จ',
            'case': {
                'id': case.id,
                'hn': case.hn,
                'first_name': case.first_name,
                'last_name': case.last_name,
                'age': case.age,
                'gender': case.gender,
                'diagnosis': case.diagnosis,
                'treatment': case.treatment,
                'status': case.status,
                'case_date': case.case_date.isoformat() if case.case_date else None,
                'department_id': case.department_id,
                'department_name': dept.name,
                'created_at': case.created_at.isoformat() if case.created_at else None
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'เกิดข้อผิดพลาด: {str(e)}'}), 500

@admin_api_bp.route('/cases/<int:case_id>', methods=['DELETE'])
@jwt_required
def api_delete_case(case_id):
    """API endpoint to delete a case"""
    try:
        case = db.session.query(PatientCase).filter_by(id=case_id, is_deleted=False).first()
        if not case:
            return jsonify({'success': False, 'message': 'ไม่พบเคสที่ต้องการลบ'}), 404
        
        case.is_deleted = True
        case.deleted_at = datetime.now(timezone.utc)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'ลบเคสสำเร็จ'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'เกิดข้อผิดพลาด: {str(e)}'}), 500

# Backups API endpoints
@admin_api_bp.route('/backups', methods=['GET'])
@jwt_required
def api_get_backups():
    """API endpoint to get all backups"""
    try:
        backup_system = BackupSystem()
        backups = backup_system.list_backups()
        
        backups_data = []
        for backup in backups:
            backups_data.append({
                'filename': backup['filename'],
                'size': backup['size'],
                'created_at': backup['created_at'],
                'type': backup.get('type', 'manual')
            })
        
        return jsonify({
            'success': True,
            'backups': backups_data
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'เกิดข้อผิดพลาด: {str(e)}'}), 500

@admin_api_bp.route('/backups/create', methods=['POST'])
@jwt_required
def api_create_backup():
    """API endpoint to create a new backup"""
    try:
        backup_system = BackupSystem()
        result = backup_system.create_backup()
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'สร้างไฟล์สำรองข้อมูลสำเร็จ',
                'backup': {
                    'filename': result['filename'],
                    'size': result['size']
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': f'เกิดข้อผิดพลาดในการสร้างไฟล์สำรองข้อมูล: {result["error"]}'
            }), 500
    except Exception as e:
        return jsonify({'success': False, 'message': f'เกิดข้อผิดพลาด: {str(e)}'}), 500

@admin_api_bp.route('/backups/<filename>/download', methods=['GET'])
@jwt_required
def api_download_backup(filename):
    """API endpoint to download a backup file"""
    try:
        backup_system = BackupSystem()
        backup_path = backup_system.get_backup_path(filename)
        
        if not os.path.exists(backup_path):
            return jsonify({'success': False, 'message': 'ไม่พบไฟล์สำรองข้อมูล'}), 404
        
        return send_file(
            backup_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/octet-stream'
        )
    except Exception as e:
        return jsonify({'success': False, 'message': f'เกิดข้อผิดพลาด: {str(e)}'}), 500

@admin_api_bp.route('/backups/<filename>/restore', methods=['POST'])
@jwt_required
def api_restore_backup(filename):
    """API endpoint to restore from a backup file"""
    try:
        backup_system = BackupSystem()
        result = backup_system.restore_backup(filename)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'กู้คืนข้อมูลสำเร็จ'
            })
        else:
            return jsonify({
                'success': False,
                'message': f'เกิดข้อผิดพลาดในการกู้คืนข้อมูล: {result["error"]}'
            }), 500
    except Exception as e:
        return jsonify({'success': False, 'message': f'เกิดข้อผิดพลาด: {str(e)}'}), 500

@admin_api_bp.route('/backups/<filename>', methods=['DELETE'])
@jwt_required
def api_delete_backup(filename):
    """API endpoint to delete a backup file"""
    try:
        backup_system = BackupSystem()
        result = backup_system.delete_backup(filename)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'ลบไฟล์สำรองข้อมูลสำเร็จ'
            })
        else:
            return jsonify({
                'success': False,
                'message': f'เกิดข้อผิดพลาดในการลบไฟล์สำรองข้อมูล: {result["error"]}'
            }), 500
    except Exception as e:
        return jsonify({'success': False, 'message': f'เกิดข้อผิดพลาด: {str(e)}'}), 500

@admin_api_bp.route('/auth/logout', methods=['POST'])
@jwt_required
def api_admin_logout():
    """API endpoint for admin logout"""
    try:
        # With JWT, logout is handled client-side by removing the token
        return jsonify({'success': True, 'message': 'ออกจากระบบสำเร็จ'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'เกิดข้อผิดพลาด: {str(e)}'}), 500

@admin_api_bp.route('/auth/user', methods=['GET'])
@jwt_required
def api_get_current_user():
    """API endpoint to get current user info"""
    try:
        current_user = get_current_user()
        return jsonify({
            'success': True,
            'user': {
                'id': current_user.id,
                'username': current_user.username,
                'email': current_user.email,
                'role': current_user.role,
                'last_login': current_user.last_login.isoformat() if current_user.last_login else None
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'เกิดข้อผิดพลาด: {str(e)}'}), 500

# Dashboard API endpoints
@admin_api_bp.route('/dashboard/stats', methods=['GET'])
@jwt_required
def api_dashboard_stats():
    """API endpoint for dashboard statistics"""
    try:
        # Get statistics
        total_patients = db.session.query(PatientCase).filter_by(is_deleted=False).count()
        total_doctors = db.session.query(Contact).filter_by(is_deleted=False).count()
        total_cases = db.session.query(PatientCase).filter_by(is_deleted=False).count()
        pending_cases = db.session.query(PatientCase).filter(
            PatientCase.is_deleted == False,
            PatientCase.status == 'pending'
        ).count()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_patients': total_patients,
                'total_doctors': total_doctors,
                'total_cases': total_cases,
                'pending_cases': pending_cases
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'เกิดข้อผิดพลาด: {str(e)}'}), 500

@admin_api_bp.route('/dashboard/activities', methods=['GET'])
@jwt_required
def api_dashboard_activities():
    """API endpoint for recent activities"""
    try:
        # Get recent activities (last 10)
        activities = db.session.query(Activity).order_by(
            Activity.created_at.desc()
        ).limit(10).all()
        
        activities_data = []
        for activity in activities:
            activities_data.append({
                'id': activity.id,
                'title': activity.title,
                'description': activity.description,
                'type': activity.activity_type,
                'created_at': activity.created_at.isoformat(),
                'created_by': activity.created_by
            })
        
        return jsonify({
            'success': True,
            'activities': activities_data
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'เกิดข้อผิดพลาด: {str(e)}'}), 500

# Departments API endpoints
@admin_api_bp.route('/departments', methods=['GET'])
@jwt_required
def api_get_departments():
    """API endpoint to get all departments"""
    try:
        departments = db.session.query(Department).all()
        departments_data = []
        
        for dept in departments:
            departments_data.append({
                'id': dept.id,
                'name': dept.name,
                'code': dept.code,
                'description': dept.description,
                'created_at': dept.created_at.isoformat() if dept.created_at else None
            })
        
        return jsonify({
            'success': True,
            'departments': departments_data
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'เกิดข้อผิดพลาด: {str(e)}'}), 500

@admin_api_bp.route('/departments', methods=['POST'])
@jwt_required
def api_create_department():
    """API endpoint to create a new department"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'ไม่พบข้อมูลแผนก'}), 400
        
        name = data.get('name')
        code = data.get('code')
        description = data.get('description', '')
        
        if not name or not code:
            return jsonify({'success': False, 'message': 'กรุณากรอกชื่อแผนกและรหัสแผนก'}), 400
        
        # Check if department code already exists
        existing_dept = db.session.query(Department).filter_by(code=code).first()
        if existing_dept:
            return jsonify({'success': False, 'message': 'รหัสแผนกนี้มีอยู่แล้ว'}), 400
        
        new_dept = Department(
            name=name,
            code=code,
            description=description,
            created_at=datetime.now(timezone.utc)
        )
        
        db.session.add(new_dept)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'เพิ่มแผนกสำเร็จ',
            'department': {
                'id': new_dept.id,
                'name': new_dept.name,
                'code': new_dept.code,
                'description': new_dept.description,
                'created_at': new_dept.created_at.isoformat()
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'เกิดข้อผิดพลาด: {str(e)}'}), 500

@admin_api_bp.route('/departments/<int:dept_id>', methods=['PUT'])
@jwt_required
def api_update_department(dept_id):
    """API endpoint to update a department"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'ไม่พบข้อมูลแผนก'}), 400
        
        dept = db.session.query(Department).get(dept_id)
        if not dept:
            return jsonify({'success': False, 'message': 'ไม่พบแผนกที่ต้องการแก้ไข'}), 404
        
        name = data.get('name')
        code = data.get('code')
        description = data.get('description', '')
        
        if not name or not code:
            return jsonify({'success': False, 'message': 'กรุณากรอกชื่อแผนกและรหัสแผนก'}), 400
        
        # Check if department code already exists (excluding current department)
        existing_dept = db.session.query(Department).filter(
            Department.code == code,
            Department.id != dept_id
        ).first()
        if existing_dept:
            return jsonify({'success': False, 'message': 'รหัสแผนกนี้มีอยู่แล้ว'}), 400
        
        dept.name = name
        dept.code = code
        dept.description = description
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'แก้ไขแผนกสำเร็จ',
            'department': {
                'id': dept.id,
                'name': dept.name,
                'code': dept.code,
                'description': dept.description,
                'created_at': dept.created_at.isoformat() if dept.created_at else None
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'เกิดข้อผิดพลาด: {str(e)}'}), 500

@admin_api_bp.route('/departments/<int:dept_id>', methods=['DELETE'])
@jwt_required
def api_delete_department(dept_id):
    """API endpoint to delete a department"""
    try:
        dept = db.session.query(Department).get(dept_id)
        if not dept:
            return jsonify({'success': False, 'message': 'ไม่พบแผนกที่ต้องการลบ'}), 404
        
        # Check if department has associated cases
        case_count = db.session.query(PatientCase).filter_by(
            department_id=dept_id,
            is_deleted=False
        ).count()
        
        if case_count > 0:
            return jsonify({
                'success': False,
                'message': f'ไม่สามารถลบแผนกได้ เนื่องจากมีข้อมูลผู้ป่วย {case_count} รายการ'
            }), 400
        
        db.session.delete(dept)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'ลบแผนกสำเร็จ'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'เกิดข้อผิดพลาด: {str(e)}'}), 500