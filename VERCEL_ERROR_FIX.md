# 🔧 แก้ไข 500 Error บน Vercel

## 🐛 ปัญหา

**Error:**
```
500: INTERNAL_SERVER_ERROR
Code: FUNCTION_INVOCATION_FAILED
```

## 🔍 สาเหตุที่เป็นไปได้

### 1. Database Connection Error
- `DATABASE_URL` ไม่ถูกต้องหรือไม่ได้ตั้งค่า
- Password ผิด
- Host ไม่สามารถเข้าถึงได้
- Firewall block

### 2. Missing Environment Variables
- `SECRET_KEY` ไม่ได้ตั้งค่า
- `DATABASE_URL` ไม่ได้ตั้งค่า
- `VERCEL=1` ไม่ได้ตั้งค่า

### 3. Import Errors
- Missing dependencies
- Import paths ไม่ถูกต้อง

### 4. Database Schema Issues
- Tables ยังไม่ได้สร้าง
- Schema ไม่ตรงกับ code

---

## ✅ วิธีแก้ไข

### ขั้นตอนที่ 1: ตรวจสอบ Environment Variables

1. **ไปที่ Vercel Dashboard:**
   - https://vercel.com/prhdev222s-projects/medfiles/settings/environment-variables

2. **ตรวจสอบว่ามีตัวแปรเหล่านี้:**
   ```
   FLASK_ENV=production
   FLASK_DEBUG=False
   SECRET_KEY=aeab9e70eebe445d4f1bb7e2d8e0278f737947f2970faba8f83c2674f1d86af4
   DATABASE_URL=postgresql://postgres:[PASSWORD]@db.vmfmoseeunnfwjzunnss.supabase.co:6543/postgres?pgbouncer=true
   CORS_ORIGINS=https://medfiles.vercel.app
   VERCEL=1
   ```

3. **ตรวจสอบ DATABASE_URL:**
   - ต้องมี password จริง (ไม่ใช่ `[YOUR-PASSWORD]`)
   - ใช้ Connection Pooling (port 6543) สำหรับ Vercel
   - Format ถูกต้อง: `postgresql://postgres:password@host:port/database`

### ขั้นตอนที่ 2: ตรวจสอบ Database Connection

1. **ทดสอบ Connection String:**
   ```python
   import psycopg2
   
   DATABASE_URL = "postgresql://postgres:[PASSWORD]@db.vmfmoseeunnfwjzunnss.supabase.co:6543/postgres?pgbouncer=true"
   
   try:
       conn = psycopg2.connect(DATABASE_URL)
       print("✅ Connection successful!")
       conn.close()
   except Exception as e:
       print(f"❌ Connection failed: {e}")
   ```

2. **ตรวจสอบ Supabase Dashboard:**
   - ไปที่ https://supabase.com/dashboard
   - Settings → Database → Connection string
   - ตรวจสอบ password ถูกต้อง

### ขั้นตอนที่ 3: สร้าง Database Tables

1. **ใช้ Supabase SQL Editor:**
   - ไปที่ Supabase Dashboard
   - SQL Editor → New Query
   - เปิดไฟล์ `supabase_schema.sql`
   - คัดลอกและรัน SQL script ทั้งหมด

2. **หรือใช้ Python Script:**
   ```python
   import os
   from dotenv import load_dotenv
   from app import app, db
   
   load_dotenv()
   
   with app.app_context():
       db.create_all()
       print("✅ Tables created successfully!")
   ```

### ขั้นตอนที่ 4: ตรวจสอบ Logs

1. **ดู Vercel Logs:**
   - ไปที่ Vercel Dashboard → Deployments
   - คลิกที่ deployment ล่าสุด
   - ดู **Logs** tab
   - หา error messages

2. **Common Errors:**
   - `could not connect to server` → Database connection issue
   - `relation "admin_user" does not exist` → Tables ยังไม่ได้สร้าง
   - `password authentication failed` → Password ผิด
   - `ModuleNotFoundError` → Missing dependencies

### ขั้นตอนที่ 5: Redeploy

1. **หลังจากแก้ไข Environment Variables:**
   - ไปที่ Deployments
   - คลิก **"..."** → **"Redeploy"**
   - เลือก **"Use existing Build Cache"** หรือ **"Rebuild"**

2. **หรือ Push Code ใหม่:**
   ```bash
   git add .
   git commit -m "Fix Vercel deployment"
   git push origin main
   ```

---

## 🧪 ทดสอบ Health Check

### 1. ทดสอบ Health Endpoint

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

**ถ้าได้ error:**
```json
{
  "status": "unhealthy",
  "database": "disconnected",
  "error": "..."
}
```

### 2. ตรวจสอบ Error Message

ดู error message ใน response เพื่อหาสาเหตุ:
- `could not connect to server` → Database connection issue
- `relation does not exist` → Tables ยังไม่ได้สร้าง
- `password authentication failed` → Password ผิด

---

## 🔧 Troubleshooting

### ปัญหา: Database Connection Error

**Error:**
```
could not connect to server
```

**แก้ไข:**
1. ตรวจสอบ `DATABASE_URL` format ถูกต้อง
2. ตรวจสอบ password ถูกต้อง
3. ใช้ Connection Pooling (port 6543)
4. ตรวจสอบ Supabase Network restrictions

### ปัญหา: Tables ไม่มี

**Error:**
```
relation "admin_user" does not exist
```

**แก้ไข:**
1. รัน SQL script ใน Supabase SQL Editor
2. หรือใช้ `db.create_all()` ใน Python script

### ปัญหา: Password Authentication Failed

**Error:**
```
password authentication failed
```

**แก้ไข:**
1. Reset database password ใน Supabase Dashboard
2. อัพเดท `DATABASE_URL` ใน Vercel
3. Redeploy

### ปัญหา: Module Not Found

**Error:**
```
ModuleNotFoundError: No module named 'xxx'
```

**แก้ไข:**
1. ตรวจสอบ `requirements.txt` มี dependencies ทั้งหมด
2. Push `requirements.txt` ไปยัง GitHub
3. Redeploy

---

## 📝 Checklist

- [ ] Environment Variables ตั้งค่าแล้ว
- [ ] `DATABASE_URL` ถูกต้องและมี password จริง
- [ ] `VERCEL=1` ตั้งค่าแล้ว
- [ ] Database tables สร้างแล้ว (ใช้ `supabase_schema.sql`)
- [ ] ทดสอบ connection สำเร็จแล้ว
- [ ] Health check ผ่านแล้ว
- [ ] Redeploy แล้ว

---

## 🔗 Links ที่เกี่ยวข้อง

- **Vercel Dashboard:** https://vercel.com/prhdev222s-projects/medfiles
- **Vercel Logs:** https://vercel.com/prhdev222s-projects/medfiles/deployments
- **Supabase Dashboard:** https://supabase.com/dashboard/project/vmfmoseeunnfwjzunnss
- **Supabase SQL Editor:** https://supabase.com/dashboard/project/vmfmoseeunnfwjzunnss/sql

---

**Happy Debugging! 🔧**


