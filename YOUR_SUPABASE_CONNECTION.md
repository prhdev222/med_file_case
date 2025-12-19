# 🔗 Connection String สำหรับ Supabase Project ของคุณ

## 📋 ข้อมูลจาก URL

**Supabase URL:** `https://vmfmoseeunnfwjzunnss.supabase.co`

**Project Reference:** `vmfmoseeunnfwjzunnss`

**Database Host:** `db.vmfmoseeunnfwjzunnss.supabase.co`

---

## 🔐 Connection String Formats

### 1. Direct Connection (Port 5432)

```
postgresql://postgres:[YOUR-PASSWORD]@db.vmfmoseeunnfwjzunnss.supabase.co:5432/postgres
```

**ใช้สำหรับ:**
- Long-lived connections
- Virtual machines
- Containers

### 2. Connection Pooling (Port 6543) - **แนะนำสำหรับ Vercel** ⭐

```
postgresql://postgres:[YOUR-PASSWORD]@db.vmfmoseeunnfwjzunnss.supabase.co:6543/postgres?pgbouncer=true
```

**ใช้สำหรับ:**
- Serverless functions (Vercel, Netlify)
- Short-lived connections
- High concurrency

### 3. Transaction Mode (Port 6543)

```
postgresql://postgres:[YOUR-PASSWORD]@db.vmfmoseeunnfwjzunnss.supabase.co:6543/postgres?pgbouncer=true&pooler_mode=transaction
```

---

## 🔑 วิธีหา Database Password

### ขั้นตอนที่ 1: ไปที่ Supabase Dashboard

1. เปิด: https://supabase.com/dashboard
2. Login เข้าสู่ระบบ
3. เลือก Project: `vmfmoseeunnfwjzunnss`

### ขั้นตอนที่ 2: ดู Database Password

1. **Settings** → **Database**
2. ดู **Database password**
3. ถ้าไม่รู้ password → คลิก **"Reset database password"**
4. เก็บ password ไว้ในที่ปลอดภัย

### ขั้นตอนที่ 3: ดู Connection String (ถ้ามี)

1. **Settings** → **Database** → **Connection string**
2. เลือก **URI** format
3. เลือก **Direct connection** หรือ **Connection pooling**
4. คัดลอก Connection String (จะมี password อยู่แล้ว)

---

## 🚀 ตั้งค่าใน Vercel

### ขั้นตอนที่ 1: ไปที่ Vercel Dashboard

URL: https://vercel.com/prhdev222s-projects/medfiles/settings/environment-variables

### ขั้นตอนที่ 2: เพิ่ม DATABASE_URL

**Key:** `DATABASE_URL`

**Value (แนะนำใช้ Connection Pooling):**
```
postgresql://postgres:[YOUR-PASSWORD]@db.vmfmoseeunnfwjzunnss.supabase.co:6543/postgres?pgbouncer=true
```

**Environment:** 
- ✅ Production
- ✅ Preview
- ✅ Development (optional)

**หมายเหตุ:** แทนที่ `[YOUR-PASSWORD]` ด้วย password จริงจาก Supabase Dashboard

### ขั้นตอนที่ 3: เพิ่ม Environment Variables อื่นๆ

```
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=aeab9e70eebe445d4f1bb7e2d8e0278f737947f2970faba8f83c2674f1d86af4
CORS_ORIGINS=https://medfiles.vercel.app
VERCEL=1
```

### ขั้นตอนที่ 4: Redeploy

1. ไปที่ **Deployments** tab
2. คลิก **"..."** → **"Redeploy"**
3. หรือ push code ใหม่ไปยัง GitHub

---

## 🧪 ทดสอบ Connection

### ใช้ Python Script:

สร้างไฟล์ `test_connection.py`:

```python
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# ใช้ Connection Pooling (แนะนำสำหรับ serverless)
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("❌ DATABASE_URL not found")
    exit(1)

try:
    conn = psycopg2.connect(DATABASE_URL)
    print("✅ Connection successful!")
    
    # Test query
    cur = conn.cursor()
    cur.execute("SELECT version();")
    version = cur.fetchone()
    print(f"📊 PostgreSQL version: {version[0]}")
    
    cur.close()
    conn.close()
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

รัน:
```bash
python test_connection.py
```

---

## 📝 สรุป Connection String

### สำหรับ Vercel (แนะนำ):

```
postgresql://postgres:[YOUR-PASSWORD]@db.vmfmoseeunnfwjzunnss.supabase.co:6543/postgres?pgbouncer=true
```

### สำหรับ Coolify หรือ Local:

```
postgresql://postgres:[YOUR-PASSWORD]@db.vmfmoseeunnfwjzunnss.supabase.co:5432/postgres
```

---

## ⚠️ ข้อควรระวัง

1. **Password มีอักขระพิเศษ:**
   - ถ้า password มี `@`, `#`, `%` → ต้อง URL encode
   - เช่น: `my@pass#123` → `my%40pass%23123`

2. **Network Restrictions:**
   - ตรวจสอบว่า Supabase อนุญาต external connections
   - ไปที่ **Settings** → **Database** → **Network restrictions**

3. **Connection Limits:**
   - ใช้ Connection Pooling (port 6543) เพื่อหลีกเลี่ยง connection limits
   - เหมาะกับ serverless environments

---

## 🔗 Links ที่เกี่ยวข้อง

- **Supabase Dashboard:** https://supabase.com/dashboard/project/vmfmoseeunnfwjzunnss
- **Vercel Environment Variables:** https://vercel.com/prhdev222s-projects/medfiles/settings/environment-variables
- **Supabase Connection Docs:** https://supabase.com/docs/guides/database/connecting-to-postgres

---

## ✅ Checklist

- [ ] หา Database Password จาก Supabase Dashboard แล้ว
- [ ] สร้าง Connection String แล้ว
- [ ] ตั้งค่า `DATABASE_URL` ใน Vercel แล้ว
- [ ] ตั้งค่า Environment Variables อื่นๆ แล้ว
- [ ] ทดสอบ connection สำเร็จแล้ว
- [ ] Redeploy Vercel application แล้ว

---

**Happy Connecting! 🔗**

