# ✅ ตรวจสอบ Environment Variables ใน Vercel

## 🔍 ตรวจสอบว่าตั้งค่าครบหรือยัง

### ไปที่ Vercel Dashboard:
https://vercel.com/prhdev222s-projects/medfiles/settings/environment-variables

### ตรวจสอบว่ามีตัวแปรเหล่านี้ทั้งหมด:

#### 1. FLASK_ENV
```
Key: FLASK_ENV
Value: production
Environment: Production, Preview, Development
```

#### 2. FLASK_DEBUG
```
Key: FLASK_DEBUG
Value: False
Environment: Production, Preview, Development
```

#### 3. SECRET_KEY
```
Key: SECRET_KEY
Value: aeab9e70eebe445d4f1bb7e2d8e0278f737947f2970faba8f83c2674f1d86af4
Environment: Production, Preview, Development
```

#### 4. DATABASE_URL (สำคัญที่สุด!)
```
Key: DATABASE_URL
Value: postgresql://postgres:[YOUR-PASSWORD]@db.vmfmoseeunnfwjzunnss.supabase.co:6543/postgres?pgbouncer=true
Environment: Production, Preview, Development
```

**⚠️ ตรวจสอบ:**
- แทนที่ `[YOUR-PASSWORD]` ด้วย password จริงจาก Supabase
- ใช้ port `6543` (Connection Pooling)
- มี `?pgbouncer=true` parameter

**วิธีหา Password:**
1. ไปที่ Supabase Dashboard: https://supabase.com/dashboard/project/vmfmoseeunnfwjzunnss
2. Settings → Database
3. ดู Database password
4. ถ้าไม่รู้ → Reset database password

#### 5. CORS_ORIGINS
```
Key: CORS_ORIGINS
Value: https://medfiles.vercel.app
Environment: Production, Preview, Development
```

#### 6. VERCEL
```
Key: VERCEL
Value: 1
Environment: Production, Preview, Development
```

---

## 🧪 ทดสอบ Connection String

### ใช้ Python Script:

```python
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("❌ DATABASE_URL not found")
    exit(1)

# Mask password for display
display_url = DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'hidden'
print(f"Testing connection to: {display_url}")

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

---

## 📝 Checklist

- [ ] `FLASK_ENV=production` ตั้งค่าแล้ว
- [ ] `FLASK_DEBUG=False` ตั้งค่าแล้ว
- [ ] `SECRET_KEY` ตั้งค่าแล้ว
- [ ] `DATABASE_URL` ตั้งค่าแล้วและมี password จริง
- [ ] `DATABASE_URL` ใช้ port 6543 (Connection Pooling)
- [ ] `CORS_ORIGINS` ตั้งค่าแล้ว
- [ ] `VERCEL=1` ตั้งค่าแล้ว
- [ ] ทดสอบ connection สำเร็จแล้ว
- [ ] Database tables สร้างแล้ว
- [ ] Redeploy แล้ว

---

## 🔧 หลังจากแก้ไข Environment Variables

**ต้อง Redeploy:**

```bash
vercel --prod --force
```

หรือใน Dashboard:
1. Deployments → ... → Redeploy
2. เลือก "Rebuild" (ไม่ใช้ cache)

---

## 🆘 ถ้ายังมีปัญหา

1. **ดู Logs ใน Vercel Dashboard:**
   - Deployments → คลิก deployment ล่าสุด → Logs tab
   - หา error messages

2. **ทดสอบ Health Check:**
   ```bash
   curl https://medfiles.vercel.app/health
   ```

3. **ตรวจสอบ Database:**
   - ไปที่ Supabase Dashboard
   - ตรวจสอบว่า tables สร้างแล้ว
   - ตรวจสอบ Network restrictions


