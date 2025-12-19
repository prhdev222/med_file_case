# 🚨 แก้ไข 500 Error อย่างเร่งด่วน

## 🔍 สาเหตุที่เป็นไปได้ (เรียงตามความน่าจะเป็น)

### 1. ❌ Database Tables ยังไม่ได้สร้าง (90% น่าจะเป็น)

**อาการ:** Function crash ทันทีเมื่อพยายาม query database

**แก้ไข:**
1. ไปที่ Supabase Dashboard: https://supabase.com/dashboard/project/vmfmoseeunnfwjzunnss
2. ไปที่ **SQL Editor**
3. เปิดไฟล์ `supabase_schema.sql` จากโปรเจค
4. คัดลอก SQL ทั้งหมดและรันใน SQL Editor
5. รอให้สร้าง tables เสร็จ

### 2. ❌ DATABASE_URL ไม่ถูกต้อง (80% น่าจะเป็น)

**อาการ:** Connection error หรือ authentication failed

**แก้ไข:**
1. ไปที่ Vercel Dashboard: https://vercel.com/prhdev222s-projects/medfiles/settings/environment-variables
2. ตรวจสอบ `DATABASE_URL`:
   ```
   postgresql://postgres:[PASSWORD]@db.vmfmoseeunnfwjzunnss.supabase.co:6543/postgres?pgbouncer=true
   ```
3. **สำคัญ:** แทนที่ `[PASSWORD]` ด้วย password จริงจาก Supabase
4. ตรวจสอบว่าใช้ port `6543` (Connection Pooling) สำหรับ Vercel
5. Redeploy หลังจากแก้ไข

### 3. ❌ Missing Environment Variables (70% น่าจะเป็น)

**แก้ไข:**
ตรวจสอบว่ามีตัวแปรเหล่านี้ทั้งหมด:

```
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=aeab9e70eebe445d4f1bb7e2d8e0278f737947f2970faba8f83c2674f1d86af4
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.vmfmoseeunnfwjzunnss.supabase.co:6543/postgres?pgbouncer=true
CORS_ORIGINS=https://medfiles.vercel.app
VERCEL=1
```

### 4. ❌ Import Errors (50% น่าจะเป็น)

**แก้ไข:**
ตรวจสอบ `requirements.txt` มี dependencies ทั้งหมด

---

## ✅ ขั้นตอนแก้ไขแบบ Step-by-Step

### Step 1: สร้าง Database Tables (สำคัญที่สุด!)

1. **ไปที่ Supabase Dashboard:**
   - https://supabase.com/dashboard/project/vmfmoseeunnfwjzunnss

2. **ไปที่ SQL Editor:**
   - คลิก **SQL Editor** ใน sidebar
   - คลิก **New Query**

3. **รัน SQL Script:**
   - เปิดไฟล์ `supabase_schema.sql` จากโปรเจค
   - คัดลอก SQL ทั้งหมด
   - วางใน SQL Editor
   - คลิก **Run** หรือกด `Ctrl+Enter`

4. **ตรวจสอบว่า Tables สร้างแล้ว:**
   - ไปที่ **Table Editor**
   - ควรเห็น tables: `admin_user`, `department`, `patient_case`, etc.

### Step 2: ตรวจสอบ DATABASE_URL

1. **หา Database Password:**
   - ไปที่ Supabase Dashboard → **Settings** → **Database**
   - ดู **Database password**
   - ถ้าไม่รู้ → คลิก **Reset database password**

2. **สร้าง Connection String:**
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.vmfmoseeunnfwjzunnss.supabase.co:6543/postgres?pgbouncer=true
   ```
   แทนที่ `[YOUR-PASSWORD]` ด้วย password จริง

3. **ตั้งค่าใน Vercel:**
   - ไปที่: https://vercel.com/prhdev222s-projects/medfiles/settings/environment-variables
   - แก้ไข `DATABASE_URL` หรือเพิ่มใหม่
   - **Environment:** เลือก Production, Preview
   - **Save**

### Step 3: ตรวจสอบ Environment Variables อื่นๆ

ตรวจสอบว่ามีตัวแปรเหล่านี้ทั้งหมดใน Vercel:

- `FLASK_ENV=production`
- `FLASK_DEBUG=False`
- `SECRET_KEY=...` (ต้องมีค่า)
- `DATABASE_URL=...` (ต้องมี password จริง)
- `CORS_ORIGINS=https://medfiles.vercel.app`
- `VERCEL=1`

### Step 4: Redeploy

1. **หลังจากแก้ไข Environment Variables:**
   - ไปที่ Vercel Dashboard → **Deployments**
   - คลิก **"..."** → **"Redeploy"**
   - เลือก **"Rebuild"** (ไม่ใช้ cache)

2. **หรือใช้ CLI:**
   ```bash
   vercel --prod --force
   ```

### Step 5: ทดสอบ

```bash
curl https://medfiles.vercel.app/health
```

**ควรได้:**
```json
{
  "status": "healthy",
  "database": "connected"
}
```

---

## 🧪 ทดสอบ Database Connection

### ใช้ Python Script:

สร้างไฟล์ `test_db_connection.py`:

```python
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("❌ DATABASE_URL not found")
    exit(1)

print(f"Testing connection to: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'hidden'}")

try:
    conn = psycopg2.connect(DATABASE_URL)
    print("✅ Connection successful!")
    
    cur = conn.cursor()
    cur.execute("SELECT version();")
    version = cur.fetchone()
    print(f"📊 PostgreSQL version: {version[0]}")
    
    # Test if tables exist
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)
    tables = cur.fetchall()
    print(f"📋 Tables found: {len(tables)}")
    for table in tables:
        print(f"   - {table[0]}")
    
    cur.close()
    conn.close()
except Exception as e:
    print(f"❌ Connection failed: {e}")
    import traceback
    traceback.print_exc()
```

รัน:
```bash
python test_db_connection.py
```

---

## 🔍 ตรวจสอบ Logs ใน Vercel

1. **ไปที่ Vercel Dashboard:**
   - https://vercel.com/prhdev222s-projects/medfiles

2. **ไปที่ Deployments:**
   - คลิก deployment ล่าสุด

3. **ดู Logs:**
   - คลิก **Logs** tab
   - หา error messages

**Common Errors:**
- `relation "admin_user" does not exist` → Tables ยังไม่ได้สร้าง
- `could not connect to server` → Database connection issue
- `password authentication failed` → Password ผิด
- `ModuleNotFoundError` → Missing dependencies

---

## 📝 Checklist ด่วน

- [ ] สร้าง database tables ด้วย `supabase_schema.sql` แล้ว
- [ ] `DATABASE_URL` มี password จริง (ไม่ใช่ `[YOUR-PASSWORD]`)
- [ ] ใช้ Connection Pooling (port 6543) สำหรับ Vercel
- [ ] Environment Variables ทั้งหมดตั้งค่าแล้ว
- [ ] `VERCEL=1` ตั้งค่าแล้ว
- [ ] Redeploy แล้ว
- [ ] Health check ผ่านแล้ว

---

## 🆘 ถ้ายังไม่ได้

1. **ดู Logs ใน Vercel Dashboard:**
   - หา error message ที่ชัดเจน

2. **ทดสอบ Database Connection:**
   - ใช้ Python script ด้านบน

3. **ตรวจสอบ Supabase:**
   - ตรวจสอบว่า Supabase service ทำงานอยู่
   - ตรวจสอบ Network restrictions

---

**แก้ไขตามลำดับ Step 1 → Step 2 → Step 3 → Step 4 → Step 5**


