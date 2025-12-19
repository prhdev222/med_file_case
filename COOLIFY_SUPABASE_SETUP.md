# 🚀 คู่มือการ Deploy บน Coolify พร้อม Supabase

คู่มือเฉพาะสำหรับการ deploy ระบบจัดการโรงพยาบาลบน Coolify ที่มี Supabase อยู่แล้ว

## 📋 สารบัญ

1. [เตรียมความพร้อม](#เตรียมความพร้อม)
2. [การตั้งค่า Supabase Connection](#การตั้งค่า-supabase-connection)
3. [การสร้าง Tables ใน Supabase](#การสร้าง-tables-ใน-supabase)
4. [การตั้งค่า Environment Variables](#การตั้งค่า-environment-variables)
5. [การ Deploy Application](#การ-deploy-application)
6. [การตรวจสอบ](#การตรวจสอบ)

---

## ✅ เตรียมความพร้อม

### สิ่งที่ต้องมี:

- ✅ Coolify VPS ที่ติดตั้งแล้ว
- ✅ Supabase service ใน Coolify (deploy แล้ว)
- ✅ GitHub repository: `prhdev222/med_file_case`
- ✅ Domain name (optional แต่แนะนำ)

---

## 🔗 การตั้งค่า Supabase Connection

### ขั้นตอนที่ 1: ดู Supabase Connection String

1. ใน Coolify Dashboard → ไปที่ **Supabase service**
2. ดู **Connection String** หรือ **Database URL**
3. มันจะมีรูปแบบประมาณนี้:
   ```
   postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres
   ```

### ขั้นตอนที่ 2: คัดลอก Connection Details

คุณจะต้องมีข้อมูลเหล่านี้:
- **Host:** เช่น `supabase-xxx.coolify.local` หรือ IP address
- **Port:** `5432` (default)
- **Database:** `postgres` (default)
- **Username:** `postgres` (default)
- **Password:** (รหัสผ่านที่ตั้งไว้)

---

## 🗄️ การสร้าง Tables ใน Supabase

### วิธีที่ 1: ใช้ SQL Editor ใน Supabase Dashboard

1. ไปที่ Supabase Dashboard (ใน Coolify)
2. เปิด **SQL Editor**
3. รัน SQL script นี้:

**ใช้ไฟล์ `supabase_schema.sql` ที่มีอยู่ในโปรเจค:**

1. เปิด Supabase Dashboard → **SQL Editor**
2. เปิดไฟล์ `supabase_schema.sql` จากโปรเจค
3. คัดลอกและวาง SQL script ทั้งหมด
4. คลิก **Run** หรือกด `Ctrl+Enter`

**หรือใช้วิธีนี้:**

```sql
-- ดูไฟล์ supabase_schema.sql ในโปรเจค
-- รัน SQL script ทั้งหมดใน Supabase SQL Editor
```

### วิธีที่ 2: ใช้ Migration Script

สร้างไฟล์ `migrate_supabase.py`:

```python
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("❌ DATABASE_URL not found in environment variables")
    exit(1)

engine = create_engine(DATABASE_URL)

# อ่าน SQL script
with open('supabase-web-app/database.sql', 'r') as f:
    sql_script = f.read()

# Execute SQL
with engine.connect() as conn:
    conn.execute(text(sql_script))
    conn.commit()

print("✅ Database migration completed!")
```

รัน:
```bash
python migrate_supabase.py
```

---

## 🔐 การตั้งค่า Environment Variables

ใน Coolify Dashboard → **Application** → **Environment Variables** → เพิ่ม:

### ตัวแปรที่จำเป็น:

```env
# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False

# Security (สำคัญมาก! เปลี่ยนเป็นค่าที่ปลอดภัย)
SECRET_KEY=your-super-secret-production-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# Database - Supabase Connection
# แทนที่ [PASSWORD] และ [HOST] ด้วยค่าจริงจาก Supabase
DATABASE_URL=postgresql://postgres:[YOUR-SUPABASE-PASSWORD]@[SUPABASE-HOST]:5432/postgres

# CORS (ตั้งค่าให้ตรงกับ domain ของคุณ)
CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com

# Upload Settings
UPLOAD_FOLDER=storage/uploads
MAX_CONTENT_LENGTH=52428800

# Server Settings
PORT=5000
HOST=0.0.0.0

# Backup Settings (Optional)
BACKUP_DIR=storage/backups
BACKUP_INTERVAL_HOURS=24
BACKUP_KEEP_DAYS=30
```

### ตัวอย่าง DATABASE_URL สำหรับ Supabase:

```env
# ถ้า Supabase host เป็น: supabase-abc123.coolify.local
DATABASE_URL=postgresql://postgres:your-password@supabase-abc123.coolify.local:5432/postgres

# หรือถ้าใช้ IP address
DATABASE_URL=postgresql://postgres:your-password@192.168.1.100:5432/postgres
```

### วิธีสร้าง SECRET_KEY:

```bash
# ใช้ Python
python -c 'import secrets; print(secrets.token_hex(32))'

# หรือใช้ OpenSSL
openssl rand -hex 32
```

---

## 🚀 การ Deploy Application

### ขั้นตอนที่ 1: สร้าง Application ใน Coolify

1. ใน Coolify Dashboard → **"New Resource"** → **"Application"**
2. เลือก **"Git Repository"**
3. เชื่อมต่อ GitHub และเลือก repository: `med_file_case`
4. เลือก branch: `main`

### ขั้นตอนที่ 2: ตั้งค่า Build

- **Build Pack:** `Dockerfile` (Coolify จะ detect อัตโนมัติ)
- **Port:** `5000`

### ขั้นตอนที่ 3: ตั้งค่า Environment Variables

เพิ่ม Environment Variables ตามที่ระบุด้านบน

**สำคัญ:** ตรวจสอบว่า `DATABASE_URL` ชี้ไปที่ Supabase service ของคุณ

### ขั้นตอนที่ 4: เพิ่ม Domain (Optional)

1. **Domains** → เพิ่ม domain ของคุณ
2. Enable **SSL** (Coolify จะขอ Let's Encrypt อัตโนมัติ)
3. ตั้งค่า DNS ชี้มาที่ VPS IP

### ขั้นตอนที่ 5: Deploy

1. คลิก **"Deploy"**
2. รอให้ build เสร็จ (ประมาณ 3-5 นาที)
3. ตรวจสอบ logs ว่าเชื่อมต่อ database สำเร็จ

---

## ✅ การตรวจสอบ

### 1. ตรวจสอบ Health Check

```bash
curl https://your-domain.com/health
```

ควรได้ response:
```json
{
  "status": "healthy",
  "database": "connected"
}
```

### 2. ตรวจสอบ Database Connection

ดู logs ใน Coolify Dashboard:
- ควรเห็น: `เริ่มต้นฐานข้อมูลเรียบร้อยแล้ว`
- ไม่ควรมี error เกี่ยวกับ database connection

### 3. ทดสอบ Login

1. เปิด `https://your-domain.com`
2. Login ด้วย: `admin` / `admin123`
3. ควรเข้าสู่ระบบได้

### 4. ตรวจสอบใน Supabase Dashboard

1. ไปที่ Supabase Dashboard
2. ดู **Table Editor**
3. ควรเห็น tables ทั้งหมดที่สร้างไว้
4. ตรวจสอบว่า `admin_user` มี admin user อยู่

---

## 🔧 Troubleshooting

### ปัญหา: Database Connection Error

**Error:**
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**แก้ไข:**
1. ตรวจสอบ `DATABASE_URL` format:
   ```
   postgresql://postgres:password@host:5432/postgres
   ```
2. ตรวจสอบว่า Supabase service ทำงานอยู่
3. ตรวจสอบ network connection ระหว่าง services
4. ตรวจสอบ password ใน connection string

### ปัญหา: Table ไม่พบ

**Error:**
```
relation "departments" does not exist
```

**แก้ไข:**
1. รัน SQL script เพื่อสร้าง tables (ดูด้านบน)
2. หรือใช้ migration script
3. ตรวจสอบใน Supabase Dashboard ว่า tables ถูกสร้างแล้ว

### ปัญหา: Authentication Failed

**Error:**
```
password authentication failed for user "postgres"
```

**แก้ไข:**
1. ตรวจสอบ password ใน `DATABASE_URL`
2. ตรวจสอบ username (ควรเป็น `postgres`)
3. ตรวจสอบใน Supabase service settings

---

## 📊 ข้อดีของการใช้ Supabase

1. **Dashboard ที่ดี** - จัดการข้อมูลได้ง่าย
2. **API อัตโนมัติ** - มี REST API และ GraphQL
3. **Realtime** - รองรับ realtime subscriptions
4. **Storage** - จัดเก็บไฟล์ได้
5. **Authentication** - มีระบบ auth built-in
6. **Backup** - มีระบบ backup อัตโนมัติ

---

## 🔄 การอัปเดต Database Schema

### ใช้ Supabase SQL Editor

1. ไปที่ Supabase Dashboard → **SQL Editor**
2. เขียน SQL migration
3. รัน SQL script
4. ตรวจสอบว่า schema ถูกอัปเดต

### ใช้ Flask-Migrate (Optional)

```bash
# ติดตั้ง Flask-Migrate
pip install flask-migrate

# Initialize
flask db init

# Create migration
flask db migrate -m "Add new column"

# Apply migration
flask db upgrade
```

---

## 📝 Checklist

- [ ] Supabase service deploy แล้วใน Coolify
- [ ] ได้ Connection String จาก Supabase
- [ ] สร้าง tables ใน Supabase แล้ว
- [ ] ตั้งค่า `DATABASE_URL` ใน Environment Variables
- [ ] ตั้งค่า `SECRET_KEY` และตัวแปรอื่นๆ
- [ ] Application deploy แล้ว
- [ ] Health check ผ่าน (`/health`)
- [ ] Login ได้สำเร็จ
- [ ] ตรวจสอบ tables ใน Supabase Dashboard

---

## 🎉 เสร็จสิ้น!

หลังจาก deploy สำเร็จ คุณจะสามารถ:

- ✅ เข้าถึงระบบที่ `https://your-domain.com`
- ✅ จัดการข้อมูลผ่าน Supabase Dashboard
- ✅ ใช้ Supabase API สำหรับ integration อื่นๆ
- ✅ ใช้ Supabase Storage สำหรับไฟล์ (optional)

**Happy Deploying! 🚀**

