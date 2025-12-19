#!/usr/bin/env python3
"""
Models package สำหรับระบบจัดการข้อมูลผู้ป่วย
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timezone

db = SQLAlchemy()

# Import all models
from .base import Department
from .content import Guideline, Knowledge, Activity, Contact
from .patient import PatientCase, CaseAudit
from .user import AdminUser

__all__ = [
    'db',
    'Department',
    'Guideline',
    'Knowledge', 
    'Activity',
    'Contact',
    'PatientCase',
    'CaseAudit',
    'AdminUser'
]