# 🔗 สร้าง Connection String เอง (ถ้าไม่มีใน Dashboard)

## 📋 สถานการณ์

ถ้า Supabase Dashboard ไม่มี "Connection string" tab → **สร้างเองได้!**

---

## 🔍 ข้อมูลที่ต้องมี

### 1. Database Password
- ไปที่ **Settings** → **Database** → **Database password**
- ดู password หรือคลิก "Reset database password"

### 2. Project Reference
- จาก URL: `vmfmoseeunnfwjzunnss`
- หรือดูจาก URL: `https://supabase.com/dashboard/project/vmfmoseeunnfwjzunnss`

### 3. Database Host
- `db.vmfmoseeunnfwjzunnss.supabase.co`

---

## 🔐 สร้าง Connection String

### Connection Pooling (แนะนำสำหรับ Vercel):

```
postgresql://postgres:[YOUR-PASSWORD]@db.vmfmoseeunnfwjzunnss.supabase.co:6543/postgres?pgbouncer=true
```

### Direct Connection (ไม่แนะนำสำหรับ Vercel):

```
postgresql://postgres:[YOUR-PASSWORD]@db.vmfmoseeunnfwjzunnss.supabase.co:5432/postgres
```

---

## 📝 ขั้นตอนละเอียด

### Step 1: หา Database Password

1. ไปที่ Supabase Dashboard
2. **Settings** → **Database**
3. ดู **Database password**
4. ถ้าไม่รู้ → คลิก **"Reset database password"**
5. เก็บ password ไว้ในที่ปลอดภัย

### Step 2: สร้าง Connection String

**รูปแบบ:**
```
postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:6543/postgres?pgbouncer=true
```

**สำหรับ Project ของคุณ:**
```
postgresql://postgres:[YOUR-PASSWORD]@db.vmfmoseeunnfwjzunnss.supabase.co:6543/postgres?pgbouncer=true
```

**ตัวอย่าง (ถ้า password คือ `mypassword123`):**
```
postgresql://postgres:mypassword123@db.vmfmoseeunnfwjzunnss.supabase.co:6543/postgres?pgbouncer=true
```

### Step 3: ตั้งค่าใน Vercel

1. **ไปที่ Vercel Dashboard:**
   - https://vercel.com/prhdev222s-projects/medfiles/settings/environment-variables

2. **เพิ่ม DATABASE_URL:**
   - Key: `DATABASE_URL`
   - Value: Connection String ที่สร้างไว้
   - Environment: Production, Preview, Development

3. **Save**

### Step 4: Redeploy

```bash
vercel --prod --force
```

---

## ⚠️ ข้อควรระวัง

### 1. Password มีอักขระพิเศษ

ถ้า password มีอักขระพิเศษ (เช่น `@`, `#`, `%`) → ต้อง URL encode:

**ตัวอย่าง:**
- Password: `my@pass#123`
- URL encoded: `my%40pass%23123`
- Connection String: `postgresql://postgres:my%40pass%23123@db.vmfmoseeunnfwjzunnss.supabase.co:6543/postgres?pgbouncer=true`

### 2. ใช้ Port ที่ถูกต้อง

- **Port 6543** = Connection Pooling (แนะนำสำหรับ Vercel) ✅
- **Port 5432** = Direct Connection (ไม่แนะนำสำหรับ serverless) ❌

### 3. เพิ่ม Parameter

- `?pgbouncer=true` (สำหรับ Connection Pooling)
- หรือ `?pgbouncer=true&pooler_mode=transaction` (Transaction Mode)

---

## 🧪 ทดสอบ Connection String

### ใช้ Python Script:

สร้างไฟล์ `test_connection.py`:

```python
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# ใช้ Connection String ที่สร้างไว้
DATABASE_URL = "postgresql://postgres:[YOUR-PASSWORD]@db.vmfmoseeunnfwjzunnss.supabase.co:6543/postgres?pgbouncer=true"

# แทนที่ [YOUR-PASSWORD] ด้วย password จริง
# DATABASE_URL = "postgresql://postgres:mypassword123@db.vmfmoseeunnfwjzunnss.supabase.co:6543/postgres?pgbouncer=true"

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
python test_connection.py
```

---

## 📋 Checklist

- [ ] หา Database Password จาก Supabase Settings
- [ ] สร้าง Connection String (port 6543)
- [ ] ทดสอบ Connection String สำเร็จแล้ว
- [ ] ตั้งค่าใน Vercel → Environment Variables
- [ ] แทนที่ `[YOUR-PASSWORD]` ด้วย password จริง
- [ ] Redeploy Vercel

---

## 🔗 Links

- **Supabase Dashboard:** https://supabase.com/dashboard/project/vmfmoseeunnfwjzunnss
- **Database Settings:** https://supabase.com/dashboard/project/vmfmoseeunnfwjzunnss/settings/database
- **Vercel Environment Variables:** https://vercel.com/prhdev222s-projects/medfiles/settings/environment-variables

---

## 💡 Tips

1. **เก็บ Password ปลอดภัย** - อย่า commit ไปยัง Git
2. **ใช้ Environment Variables** - ตั้งค่าใน Vercel Dashboard
3. **ทดสอบก่อนใช้** - ใช้ Python script ทดสอบ connection
4. **ใช้ Connection Pooling** - port 6543 สำหรับ Vercel

---

**สรุป:** ไม่มี Connection string tab ก็ไม่เป็นไร → สร้างเองได้จาก Database password และ Project reference!


