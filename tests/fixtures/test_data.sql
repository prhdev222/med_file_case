-- Test Data for Hospital Management System
-- ข้อมูลทดสอบสำหรับระบบจัดการข้อมูลผู้ป่วย

-- เพิ่มข้อมูลหน่วยงานทดสอบ
INSERT OR REPLACE INTO department (code, name, description, created_at, updated_at) VALUES
('DM', 'หน่วยเบาหวาน', 'หน่วยงานดูแลผู้ป่วยเบาหวาน', datetime('now'), datetime('now')),
('CKD', 'หน่วยไตเรื้อรัง', 'หน่วยงานดูแลผู้ป่วยไตเรื้อรัง', datetime('now'), datetime('now')),
('COPD', 'หน่วยโรคปอดอุดกั้นเรื้อรัง', 'หน่วยงานดูแลผู้ป่วยโรคปอด', datetime('now'), datetime('now')),
('HTN', 'หน่วยความดันโลหิตสูง', 'หน่วยงานดูแลผู้ป่วยความดันโลหิตสูง', datetime('now'), datetime('now')),
('OBESITY', 'หน่วยโรคอ้วน', 'หน่วยงานดูแลผู้ป่วยโรคอ้วน', datetime('now'), datetime('now'));

-- เพิ่มข้อมูลผู้ป่วยทดสอบ
INSERT OR REPLACE INTO patient_case (hn, first_name, last_name, department_id, case_date, notes, created_at, created_by) VALUES
('1234567', 'สมชาย', 'ใจดี', (SELECT id FROM department WHERE code = 'DM'), '2024-01-15', 'ผู้ป่วยใหม่', datetime('now'), 1),
('1234568', 'สมหญิง', 'รักดี', (SELECT id FROM department WHERE code = 'CKD'), '2024-01-16', 'ตรวจติดตาม', datetime('now'), 1),
('1234569', 'สมศักดิ์', 'มั่นคง', (SELECT id FROM department WHERE code = 'COPD'), '2024-01-17', '', datetime('now'), 1),
('1234570', 'สมศรี', 'สุขใจ', (SELECT id FROM department WHERE code = 'HTN'), '2024-01-18', 'ปรับยา', datetime('now'), 1),
('1234571', 'สมชาย', 'ใจเย็น', (SELECT id FROM department WHERE code = 'OBESITY'), '2024-01-19', 'ลดน้ำหนัก', datetime('now'), 1);

-- เพิ่มข้อมูล audit logs ทดสอบ
INSERT OR REPLACE INTO case_audit (case_id, action, user_id, ip_address, created_at) VALUES
(1, 'CREATE', 1, '127.0.0.1', datetime('now')),
(2, 'CREATE', 1, '127.0.0.1', datetime('now')),
(3, 'CREATE', 1, '127.0.0.1', datetime('now')),
(4, 'CREATE', 1, '127.0.0.1', datetime('now')),
(5, 'CREATE', 1, '127.0.0.1', datetime('now'));
