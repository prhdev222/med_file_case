-- Supabase Database Schema สำหรับระบบจัดการโรงพยาบาล
-- รันคำสั่งนี้ใน Supabase SQL Editor

-- Table: departments (หน่วยงาน)
CREATE TABLE IF NOT EXISTS departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    code VARCHAR(50) UNIQUE,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table: admin_user (ผู้ใช้ระบบ)
CREATE TABLE IF NOT EXISTS admin_user (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'admin',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table: patient_case (ข้อมูลผู้ป่วย)
CREATE TABLE IF NOT EXISTS patient_case (
    id SERIAL PRIMARY KEY,
    hn VARCHAR(50) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    department_id INTEGER REFERENCES departments(id) ON DELETE SET NULL,
    file_path VARCHAR(500),
    external_link TEXT,
    note TEXT,
    custom_filename VARCHAR(255),
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by INTEGER REFERENCES admin_user(id) ON DELETE SET NULL
);

-- Table: guideline (คู่มือ)
CREATE TABLE IF NOT EXISTS guideline (
    id SERIAL PRIMARY KEY,
    department_id INTEGER REFERENCES departments(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    file_path VARCHAR(500),
    external_link TEXT,
    custom_filename VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by INTEGER REFERENCES admin_user(id) ON DELETE SET NULL
);

-- Table: knowledge (ความรู้)
CREATE TABLE IF NOT EXISTS knowledge (
    id SERIAL PRIMARY KEY,
    department_id INTEGER REFERENCES departments(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    image_path VARCHAR(500),
    external_link TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by INTEGER REFERENCES admin_user(id) ON DELETE SET NULL
);

-- Table: activity (กิจกรรม)
CREATE TABLE IF NOT EXISTS activity (
    id SERIAL PRIMARY KEY,
    department_id INTEGER REFERENCES departments(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    image_path VARCHAR(500),
    external_link TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by INTEGER REFERENCES admin_user(id) ON DELETE SET NULL
);

-- Table: contact (ข้อมูลติดต่อ)
CREATE TABLE IF NOT EXISTS contact (
    id SERIAL PRIMARY KEY,
    department_id INTEGER REFERENCES departments(id) ON DELETE CASCADE,
    line_id VARCHAR(100),
    email VARCHAR(120),
    phone VARCHAR(20),
    other_info TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- สร้าง indexes สำหรับ performance
CREATE INDEX IF NOT EXISTS idx_patient_case_department ON patient_case(department_id);
CREATE INDEX IF NOT EXISTS idx_patient_case_hn ON patient_case(hn);
CREATE INDEX IF NOT EXISTS idx_patient_case_created_by ON patient_case(created_by);
CREATE INDEX IF NOT EXISTS idx_patient_case_is_deleted ON patient_case(is_deleted);

CREATE INDEX IF NOT EXISTS idx_guideline_department ON guideline(department_id);
CREATE INDEX IF NOT EXISTS idx_guideline_created_by ON guideline(created_by);

CREATE INDEX IF NOT EXISTS idx_knowledge_department ON knowledge(department_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_created_by ON knowledge(created_by);

CREATE INDEX IF NOT EXISTS idx_activity_department ON activity(department_id);
CREATE INDEX IF NOT EXISTS idx_activity_created_by ON activity(created_by);

CREATE INDEX IF NOT EXISTS idx_contact_department ON contact(department_id);

-- Function สำหรับอัปเดต updated_at อัตโนมัติ
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers สำหรับอัปเดต updated_at
CREATE TRIGGER update_departments_updated_at 
    BEFORE UPDATE ON departments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_admin_user_updated_at 
    BEFORE UPDATE ON admin_user
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_patient_case_updated_at 
    BEFORE UPDATE ON patient_case
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_guideline_updated_at 
    BEFORE UPDATE ON guideline
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_knowledge_updated_at 
    BEFORE UPDATE ON knowledge
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_activity_updated_at 
    BEFORE UPDATE ON activity
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_contact_updated_at 
    BEFORE UPDATE ON contact
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- เพิ่มข้อมูลหน่วยงานเริ่มต้น
INSERT INTO departments (name, code) VALUES
('DM', 'DM'),
('COPD', 'COPD'),
('UGIB', 'UGIB'),
('CKD', 'CKD'),
('STEMI/NSTEMI', 'STEMI_NSTEMI'),
('STROKE', 'STROKE'),
('TB', 'TB'),
('CHEMO', 'CHEMO'),
('HTN', 'HTN'),
('SEPSIS', 'SEPSIS'),
('RHEUMATO', 'RHEUMATO'),
('OBESITY', 'OBESITY')
ON CONFLICT (code) DO NOTHING;

-- หมายเหตุ: Admin user จะถูกสร้างโดย Flask app เมื่อ init_db()
-- ใช้ password hash จาก Flask's generate_password_hash

-- ตรวจสอบว่าตารางถูกสร้างสำเร็จ
SELECT 
    table_name, 
    column_name, 
    data_type
FROM information_schema.columns 
WHERE table_schema = 'public'
    AND table_name IN ('departments', 'admin_user', 'patient_case', 'guideline', 'knowledge', 'activity', 'contact')
ORDER BY table_name, ordinal_position;

