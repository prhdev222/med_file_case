# 🧪 Test Suite - ระบบจัดการข้อมูลผู้ป่วย

## 📋 สารบัญ
1. [ภาพรวม](#ภาพรวม)
2. [โครงสร้างโฟลเดอร์](#โครงสร้างโฟลเดอร์)
3. [การใช้งาน](#การใช้งาน)
4. [การรัน Tests](#การรัน-tests)
5. [การเพิ่ม Tests ใหม่](#การเพิ่ม-tests-ใหม่)

---

## 🎯 ภาพรวม

โฟลเดอร์ `tests/` ประกอบด้วยชุดการทดสอบที่ครอบคลุมสำหรับระบบจัดการข้อมูลผู้ป่วย ประกอบด้วย:

- **Unit Tests**: ทดสอบฟังก์ชันแต่ละส่วน
- **Integration Tests**: ทดสอบการทำงานร่วมกันของระบบ
- **Database Tests**: ทดสอบการทำงานกับฐานข้อมูล
- **API Tests**: ทดสอบ API endpoints
- **Migration Scripts**: Scripts สำหรับการอัปเดตฐานข้อมูล

---

## 📁 โครงสร้างโฟลเดอร์

```
tests/
├── __init__.py                 # ทำให้เป็น Python package
├── README.md                   # ไฟล์นี้
├── test_cases.py              # การทดสอบระบบหลัก
├── unit/                      # การทดสอบหน่วยย่อย
│   ├── __init__.py
│   ├── test_models.py         # ทดสอบ Models
│   ├── test_routes.py         # ทดสอบ Routes
│   └── test_utils.py          # ทดสอบ Utility functions
├── integration/               # การทดสอบการทำงานร่วมกัน
│   ├── __init__.py
│   ├── test_api.py            # ทดสอบ API endpoints
│   └── test_database.py       # ทดสอบการทำงานกับฐานข้อมูล
├── fixtures/                  # ข้อมูลทดสอบ
│   ├── test_data.sql          # SQL สำหรับสร้างข้อมูลทดสอบ
│   └── sample_files/          # ไฟล์ตัวอย่างสำหรับอัปโหลด
├── migrations/                # Scripts สำหรับ Migration
│   ├── __init__.py
│   ├── migrate_cases.py       # Migration หลัก
│   └── migrate_cases_documents.py
└── utils/                     # เครื่องมือช่วยการทดสอบ
    ├── __init__.py
    ├── test_helpers.py        # ฟังก์ชันช่วยการทดสอบ
    └── db_setup.py            # การตั้งค่าฐานข้อมูลทดสอบ
```

---

## 🚀 การใช้งาน

### 1. ติดตั้ง Dependencies
```bash
# ติดตั้ง dependencies สำหรับการทดสอบ
pip install -r requirements-test.txt
```

### 2. ตั้งค่าสภาพแวดล้อมการทดสอบ
```bash
# ตั้งค่าสภาพแวดล้อมการทดสอบ
python -c "
from tests.utils.db_setup import setup_test_environment
setup_test_environment()
"
```

### 3. รัน Migration Scripts
```bash
# สร้างตารางใหม่
python tests/migrations/migrate_cases.py

# เพิ่มฟิลด์เอกสาร (ถ้าจำเป็น)
python tests/migrations/migrate_cases_documents.py
```

### 4. รัน Tests
```bash
# รัน tests ทั้งหมด
pytest

# รัน tests พร้อม coverage
pytest --cov=app --cov-report=html

# รัน tests เฉพาะโฟลเดอร์
pytest tests/unit/
pytest tests/integration/
```

---

## 🧪 การรัน Tests

### รัน Tests แบบพื้นฐาน
```bash
# รัน tests ทั้งหมด
pytest

# รัน tests พร้อม verbose output
pytest -v

# รัน tests พร้อมแสดง print statements
pytest -s
```

### รัน Tests พร้อม Coverage
```bash
# รัน tests พร้อม coverage report
pytest --cov=app --cov-report=term-missing

# สร้าง HTML coverage report
pytest --cov=app --cov-report=html

# ดู coverage report ใน browser
# เปิดไฟล์ htmlcov/index.html
```

### รัน Tests เฉพาะส่วน
```bash
# รัน tests เฉพาะไฟล์
pytest tests/unit/test_models.py

# รัน tests เฉพาะฟังก์ชัน
pytest tests/unit/test_models.py::test_patient_case_creation

# รัน tests ที่มีชื่อตรงกับ pattern
pytest -k "patient" tests/
```

---

## ➕ การเพิ่ม Tests ใหม่

### 1. สร้าง Unit Test
```python
# tests/unit/test_models.py
import pytest
from app import db, PatientCase

def test_patient_case_creation():
    """ทดสอบการสร้าง PatientCase"""
    case = PatientCase(
        hn="1234567",
        first_name="สมชาย",
        last_name="ใจดี",
        department_id=1,
        case_date="2024-01-15"
    )
    
    assert case.hn == "1234567"
    assert case.first_name == "สมชาย"
    assert case.last_name == "ใจดี"
```

### 2. สร้าง Integration Test
```python
# tests/integration/test_api.py
import pytest
from app import app

@pytest.fixture
def client():
    """สร้าง test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_public_stats_api(client):
    """ทดสอบ Public Stats API"""
    response = client.get('/api/public/stats?period=month&department=all')
    assert response.status_code == 200
    
    data = response.get_json()
    assert 'total_cases' in data
    assert 'departments' in data
```

### 3. สร้าง Database Test
```python
# tests/integration/test_database.py
import pytest
from tests.utils.db_setup import TestDatabaseManager

@pytest.fixture
def db_manager():
    """สร้าง database manager สำหรับการทดสอบ"""
    manager = TestDatabaseManager()
    manager.setup_test_database()
    yield manager
    manager.cleanup_test_database()

def test_patient_case_crud(db_manager):
    """ทดสอบ CRUD operations ของ PatientCase"""
    # ทดสอบการสร้าง
    # ทดสอบการอ่าน
    # ทดสอบการอัปเดต
    # ทดสอบการลบ
    pass
```

---

## 🔧 การตั้งค่า Test Environment

### Environment Variables
```bash
# สร้างไฟล์ .env.test
FLASK_ENV=testing
FLASK_DEBUG=False
DATABASE_URL=sqlite:///test_hospital.db
SECRET_KEY=test-secret-key
```

### Pytest Configuration
```ini
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
```

---

## 📊 การดูผลลัพธ์

### Coverage Report
```bash
# สร้าง coverage report
pytest --cov=app --cov-report=html

# ดู report ใน browser
# เปิดไฟล์ htmlcov/index.html
```

### Test Results
```bash
# สร้าง HTML test report
pytest --html=test_report.html --self-contained-html

# ดู report ใน browser
# เปิดไฟล์ test_report.html
```

---

## 🚨 การแก้ไขปัญหา

### ปัญหาที่พบบ่อย

#### 1. Import Error
**ปัญหา**: `ModuleNotFoundError: No module named 'app'`
**วิธีแก้**: ตรวจสอบ PYTHONPATH หรือรันจากโฟลเดอร์หลัก

#### 2. Database Connection Error
**ปัญหา**: ไม่สามารถเชื่อมต่อฐานข้อมูลได้
**วิธีแก้**: ตรวจสอบการตั้งค่าฐานข้อมูลและรัน migration scripts

#### 3. Test Dependencies Missing
**ปัญหา**: `ModuleNotFoundError` สำหรับ test libraries
**วิธีแก้**: ติดตั้ง dependencies จาก `requirements-test.txt`

### การ Debug Tests
```bash
# รัน tests พร้อม debug output
pytest -s -v --tb=long

# รัน tests เฉพาะที่ล้มเหลว
pytest --lf

# รัน tests พร้อม stop on first failure
pytest -x
```

---

## 📝 หมายเหตุสำคัญ

1. **ไม่ควรรัน tests ใน production environment**
2. **สำรองฐานข้อมูลก่อนรัน tests ที่เกี่ยวข้องกับฐานข้อมูล**
3. **ใช้ test database แยกจาก production database**
4. **ลบ test data หลังเสร็จสิ้นการทดสอบ**

---

## 📞 การติดต่อ

หากมีปัญหาหรือคำถามเกี่ยวกับการทดสอบ กรุณาติดต่อทีมพัฒนา หรือสร้าง issue ในระบบ version control
