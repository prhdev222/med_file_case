# 🔗 วิธีเชื่อมต่อ Supabase แบบอื่นๆ

## 📋 วิธีที่ 1: ใช้ Supabase Client SDK (แนะนำสำหรับ Frontend)

### ติดตั้ง:
```bash
npm install @supabase/supabase-js
```

### ใช้ใน Frontend:
```javascript
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'https://vmfmoseeunnfwjzunnss.supabase.co'
const supabaseKey = 'your-anon-key' // จาก Supabase Dashboard → Settings → API

const supabase = createClient(supabaseUrl, supabaseKey)

// Query data
const { data, error } = await supabase
  .from('patient_case')
  .select('*')
```

**ข้อดี:**
- ✅ ง่ายต่อการใช้งาน
- ✅ มี TypeScript support
- ✅ มี Realtime features
- ✅ มี Authentication built-in

**ข้อเสีย:**
- ❌ ต้องใช้ใน Frontend (ไม่เหมาะกับ Backend/Serverless)

---

## 📋 วิธีที่ 2: ใช้ Supabase REST API

### ใช้ HTTP Requests:
```python
import requests

SUPABASE_URL = "https://vmfmoseeunnfwjzunnss.supabase.co"
SUPABASE_KEY = "your-anon-key"  # จาก Supabase Dashboard → Settings → API

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# Query data
response = requests.get(
    f"{SUPABASE_URL}/rest/v1/patient_case",
    headers=headers
)
data = response.json()
```

**ข้อดี:**
- ✅ ใช้ได้กับทุกภาษา
- ✅ ไม่ต้องใช้ database driver
- ✅ ง่ายต่อการใช้งาน

**ข้อเสีย:**
- ❌ Performance ช้ากว่า direct connection
- ❌ ต้องใช้ API key

---

## 📋 วิธีที่ 3: ใช้ Connection String แบบอื่น

### 3.1 Session Mode (Port 6543):
```
postgresql://postgres:[PASSWORD]@db.vmfmoseeunnfwjzunnss.supabase.co:6543/postgres?pgbouncer=true&pooler_mode=session
```

### 3.2 Transaction Mode (Port 6543) - แนะนำ:
```
postgresql://postgres:[PASSWORD]@db.vmfmoseeunnfwjzunnss.supabase.co:6543/postgres?pgbouncer=true&pooler_mode=transaction
```

### 3.3 Direct Connection (Port 5432):
```
postgresql://postgres:[PASSWORD]@db.vmfmoseeunnfwjzunnss.supabase.co:5432/postgres
```

---

## 📋 วิธีที่ 4: ใช้ Supabase Python Client

### ติดตั้ง:
```bash
pip install supabase
```

### ใช้ใน Python:
```python
from supabase import create_client, Client

SUPABASE_URL = "https://vmfmoseeunnfwjzunnss.supabase.co"
SUPABASE_KEY = "your-anon-key"  # จาก Supabase Dashboard → Settings → API

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Query data
response = supabase.table("patient_case").select("*").execute()
data = response.data
```

**ข้อดี:**
- ✅ ง่ายต่อการใช้งาน
- ✅ มี Type hints
- ✅ Support Realtime

**ข้อเสีย:**
- ❌ ต้องใช้ API key (anon key หรือ service role key)
- ❌ Performance ช้ากว่า direct database connection

---

## 📋 วิธีที่ 5: ใช้ SQLAlchemy กับ Connection Pooling

### ปรับ app.py:
```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

# Connection Pooling configuration
DATABASE_URL = os.getenv('DATABASE_URL')

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,  # Test connections before using
    pool_recycle=3600,   # Recycle connections after 1 hour
    connect_args={
        "sslmode": "require"
    }
)
```

---

## 📋 วิธีที่ 6: ใช้ Environment Variable แบบแยกส่วน

### แทนที่จะใช้ DATABASE_URL แบบเต็ม:
```env
# แยกเป็นส่วนๆ
SUPABASE_HOST=db.vmfmoseeunnfwjzunnss.supabase.co
SUPABASE_PORT=6543
SUPABASE_DB=postgres
SUPABASE_USER=postgres
SUPABASE_PASSWORD=your-password
SUPABASE_SSL=require
```

### สร้าง Connection String ใน code:
```python
import os

host = os.getenv('SUPABASE_HOST')
port = os.getenv('SUPABASE_PORT', '6543')
db = os.getenv('SUPABASE_DB', 'postgres')
user = os.getenv('SUPABASE_USER', 'postgres')
password = os.getenv('SUPABASE_PASSWORD')

DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{db}?pgbouncer=true"
```

---

## 🎯 แนะนำสำหรับ Vercel

### วิธีที่แนะนำ: Connection Pooling (Port 6543)

**เหตุผล:**
- ✅ เหมาะกับ serverless functions
- ✅ จัดการ connections อัตโนมัติ
- ✅ Performance ดี
- ✅ ไม่ต้องใช้ API key

**Connection String:**
```
postgresql://postgres:[PASSWORD]@db.vmfmoseeunnfwjzunnss.supabase.co:6543/postgres?pgbouncer=true
```

---

## 🔧 Troubleshooting

### ปัญหา: Connection Pooling ไม่ทำงาน

**แก้ไข:**
1. ตรวจสอบว่าใช้ port `6543` (ไม่ใช่ `5432`)
2. เพิ่ม `?pgbouncer=true` parameter
3. ตรวจสอบ Supabase Dashboard → Settings → Database → Connection pooling configuration

### ปัญหา: ต้องการใช้ Supabase Client SDK

**แก้ไข:**
1. ใช้ Supabase Python Client
2. ตั้งค่า `SUPABASE_URL` และ `SUPABASE_KEY` ใน Environment Variables
3. ใช้ `supabase.table()` แทน `db.session.query()`

---

## 📝 Checklist

- [ ] เลือกวิธีที่เหมาะสม (แนะนำ: Connection Pooling)
- [ ] ตั้งค่า Environment Variables
- [ ] ทดสอบ connection
- [ ] Deploy และทดสอบ

---

## 🔗 Links

- **Supabase Dashboard:** https://supabase.com/dashboard/project/vmfmoseeunnfwjzunnss
- **Supabase Python Client:** https://github.com/supabase/supabase-py
- **Supabase JS Client:** https://github.com/supabase/supabase-js

---

**เลือกวิธีที่เหมาะสมกับ use case ของคุณ!**


