# 🔗 วิธีเชื่อมต่อ Supabase (Web) กับ Vercel

คู่มือการตั้งค่า Supabase จาก web interface เพื่อใช้กับ Vercel deployment

## 📋 สิ่งที่ต้องมี

- ✅ Supabase project (สร้างจาก https://supabase.com)
- ✅ Vercel account และ project
- ✅ Connection String จาก Supabase Dashboard

---

## 🔍 ขั้นตอนที่ 1: หา Connection String จาก Supabase Web

### วิธีที่ 1: ผ่าน Supabase Dashboard (แนะนำ)

1. **เข้า Supabase Dashboard:**
   - ไปที่ https://supabase.com
   - Login เข้าสู่ระบบ
   - เลือก Project ของคุณ

2. **ไปที่ Project Settings:**
   - คลิก **Settings** (ไอคอนฟันเฟือง) ใน sidebar ซ้าย
   - หรือไปที่: `https://supabase.com/dashboard/project/[PROJECT-ID]/settings`

3. **ดู Database Connection String:**
   - ไปที่ **Settings** → **Database**
   - หรือ **Settings** → **Connection string**
   - เลือก **Connection string** tab
   - เลือก **URI** format
   - เลือก **Direct connection** (สำหรับ serverless)

4. **คัดลอก Connection String:**
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
   ```

### วิธีที่ 2: ดูจาก Connection Info

1. **Settings** → **Database** → **Connection string**
2. ดู **Connection pooling** หรือ **Direct connection**
3. คัดลอก Connection String

### วิธีที่ 3: สร้างเองจากข้อมูล

ถ้าไม่มี Connection String ให้ดู:
- **Host:** `db.[PROJECT-REF].supabase.co`
- **Port:** `5432`
- **Database:** `postgres`
- **Username:** `postgres`
- **Password:** (ดูจาก **Settings** → **Database** → **Database password**)

**สร้าง Connection String:**
```
postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
```

---

## 🔐 ขั้นตอนที่ 2: หา Database Password

1. **Settings** → **Database**
2. ดู **Database password**
3. ถ้าไม่รู้ password → คลิก **Reset database password**
4. เก็บ password ไว้ในที่ปลอดภัย

---

## 🚀 ขั้นตอนที่ 3: ตั้งค่าใน Vercel

### วิธีที่ 1: ผ่าน Vercel Dashboard (แนะนำ)

1. **เข้า Vercel Dashboard:**
   - ไปที่ https://vercel.com
   - Login เข้าสู่ระบบ
   - เลือก Project ของคุณ (เช่น `medfiles`)

2. **ไปที่ Environment Variables:**
   - คลิก **Settings** tab
   - คลิก **Environment Variables** ใน sidebar ซ้าย
   - หรือไปที่: `https://vercel.com/[USERNAME]/[PROJECT]/settings/environment-variables`

3. **เพิ่ม DATABASE_URL:**
   - คลิก **Add New**
   - **Key:** `DATABASE_URL`
   - **Value:** `postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres`
   - **Environment:** เลือก:
     - ✅ **Production**
     - ✅ **Preview**
     - ✅ **Development** (optional)
   - คลิก **Save**

4. **เพิ่ม Environment Variables อื่นๆ:**
   ```
   FLASK_ENV=production
   FLASK_DEBUG=False
   SECRET_KEY=[YOUR-SECRET-KEY]
   CORS_ORIGINS=https://your-vercel-app.vercel.app
   VERCEL=1
   ```

5. **Redeploy:**
   - ไปที่ **Deployments** tab
   - คลิก **...** (three dots) → **Redeploy**
   - หรือ push code ใหม่ไปยัง GitHub

### วิธีที่ 2: ใช้ Vercel CLI

```bash
# Install Vercel CLI (ถ้ายังไม่มี)
npm i -g vercel

# Login
vercel login

# Add environment variable
vercel env add DATABASE_URL production
# Paste: postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres

# Redeploy
vercel --prod
```

---

## 🔍 ตัวอย่าง Connection String

### Supabase Standard Format:
```
postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
```

### ตัวอย่างจริง:
```
postgresql://postgres:mySecurePassword123@db.abcdefghijklmnop.supabase.co:5432/postgres
```

### Connection Pooling (สำหรับ serverless - แนะนำ):
```
postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:6543/postgres?pgbouncer=true
```

**หมายเหตุ:** Port `6543` = Connection Pooling (เหมาะกับ serverless)
Port `5432` = Direct Connection (เหมาะกับ long-lived connections)

---

## ⚙️ การตั้งค่า Connection Pooling (แนะนำสำหรับ Vercel)

### ทำไมต้องใช้ Connection Pooling?

- ✅ **เหมาะกับ Serverless** - Vercel เป็น serverless platform
- ✅ **จัดการ connections อัตโนมัติ** - ไม่ต้องกังวลเรื่อง connection limits
- ✅ **Performance ดีกว่า** - รองรับ concurrent requests ได้ดี

### วิธีตั้งค่า:

1. **ใช้ Connection Pooling URL:**
   ```
   postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:6543/postgres?pgbouncer=true
   ```

2. **หรือใช้ Transaction Mode:**
   ```
   postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:6543/postgres?pgbouncer=true&pooler_mode=transaction
   ```

3. **ตั้งค่าใน Vercel:**
   - เพิ่ม `DATABASE_URL` ด้วย Connection Pooling URL
   - Redeploy application

---

## 🧪 ทดสอบ Connection

### ใช้ Python Script:

สร้างไฟล์ `test_supabase_connection.py`:

```python
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

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
python test_supabase_connection.py
```

### ใช้ Vercel Function:

สร้างไฟล์ `api/test-db.js`:

```javascript
export default async function handler(req, res) {
  const { DATABASE_URL } = process.env;
  
  if (!DATABASE_URL) {
    return res.status(500).json({ error: 'DATABASE_URL not set' });
  }
  
  try {
    // Test connection (adjust based on your database library)
    const response = await fetch(DATABASE_URL);
    return res.status(200).json({ 
      status: 'connected',
      message: 'Database connection successful'
    });
  } catch (error) {
    return res.status(500).json({ 
      error: 'Connection failed',
      message: error.message 
    });
  }
}
```

---

## 🔒 Security Best Practices

### 1. อย่า Commit Connection String

- ✅ ใช้ Environment Variables ใน Vercel
- ❌ อย่าใส่ใน code หรือ commit ไปยัง Git

### 2. ใช้ Connection Pooling

- ✅ ใช้ port `6543` สำหรับ serverless
- ✅ เพิ่ม `?pgbouncer=true` parameter

### 3. จำกัด IP Access (Optional)

- ใน Supabase Dashboard → **Settings** → **Database** → **Network restrictions**
- เพิ่ม IP addresses ที่อนุญาต (ถ้าต้องการ)

---

## 📝 Checklist

- [ ] สร้าง Supabase project แล้ว
- [ ] หา Connection String จาก Supabase Dashboard แล้ว
- [ ] หา Database Password แล้ว
- [ ] ตั้งค่า `DATABASE_URL` ใน Vercel แล้ว
- [ ] ตั้งค่า Environment Variables อื่นๆ แล้ว
- [ ] ทดสอบ connection สำเร็จแล้ว
- [ ] Redeploy Vercel application แล้ว

---

## 🔧 Troubleshooting

### ปัญหา: Connection Timeout

**Error:**
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**แก้ไข:**
1. ตรวจสอบ Connection String format
2. ตรวจสอบ password ถูกต้อง
3. ใช้ Connection Pooling (port 6543)
4. ตรวจสอบ Network restrictions ใน Supabase

### ปัญหา: Too Many Connections

**Error:**
```
FATAL: too many connections
```

**แก้ไข:**
1. ใช้ Connection Pooling (port 6543)
2. ตรวจสอบ connection limits ใน Supabase
3. ปิด connections ที่ไม่ใช้

### ปัญหา: Authentication Failed

**Error:**
```
FATAL: password authentication failed
```

**แก้ไข:**
1. ตรวจสอบ password ใน Connection String
2. Reset database password ใน Supabase Dashboard
3. URL encode password ถ้ามีอักขระพิเศษ

---

## 🔗 Links ที่เกี่ยวข้อง

- **Supabase Dashboard:** https://supabase.com/dashboard
- **Vercel Dashboard:** https://vercel.com/dashboard
- **Vercel Environment Variables:** https://vercel.com/[USERNAME]/[PROJECT]/settings/environment-variables
- **Supabase Connection Pooling Docs:** https://supabase.com/docs/guides/database/connecting-to-postgres#connection-pooler

---

## 💡 Tips

1. **ใช้ Connection Pooling** - เหมาะกับ Vercel serverless
2. **เก็บ Password ปลอดภัย** - ใช้ Vercel Environment Variables
3. **ทดสอบก่อน Deploy** - ใช้ Python script ทดสอบ connection
4. **Monitor Connections** - ดู connection usage ใน Supabase Dashboard

---

**Happy Connecting! 🔗**

