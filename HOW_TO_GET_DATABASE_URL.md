# 🔗 วิธีหา DATABASE_URL จาก Supabase ใน Coolify

คู่มือการหา Connection String จาก Supabase service ใน Coolify

## 📋 วิธีที่ 1: ผ่าน Coolify Dashboard (แนะนำ)

### ขั้นตอนที่ 1: เข้า Coolify Dashboard

1. เปิดเว็บเบราว์เซอร์ไปที่ Coolify ของคุณ
   - เช่น: `https://coolify.yourdomain.com`
   - หรือ IP address ของ VPS

### ขั้นตอนที่ 2: ไปที่ Supabase Service

1. ใน Coolify Dashboard → ดู **Resources** หรือ **Services**
2. คลิกที่ **Supabase service** ของคุณ
3. ดูหน้า **Overview** หรือ **Settings**

### ขั้นตอนที่ 3: หา Connection String

ในหน้า Supabase service คุณจะเห็น:

#### ตัวเลือกที่ 1: Connection String
- ดูส่วน **"Connection String"** หรือ **"Database URL"**
- คัดลอกค่าที่แสดง
- รูปแบบ: `postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres`

#### ตัวเลือกที่ 2: แยกส่วน
ถ้าไม่มี Connection String ให้ดู:
- **Host:** เช่น `supabase-abc123.coolify.local` หรือ IP address
- **Port:** `5432` (default)
- **Database:** `postgres` (default)
- **Username:** `postgres` (default)
- **Password:** (รหัสผ่านที่ตั้งไว้ตอนสร้าง Supabase)

### ขั้นตอนที่ 4: สร้าง Connection String

ถ้าได้ข้อมูลแยกส่วน ให้สร้าง Connection String:

```
postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres
```

**ตัวอย่าง:**
```
postgresql://postgres:mypassword123@supabase-abc123.coolify.local:5432/postgres
```

หรือถ้าใช้ IP:
```
postgresql://postgres:mypassword123@192.168.1.100:5432/postgres
```

---

## 📋 วิธีที่ 2: ผ่าน Coolify CLI (ถ้ามี)

```bash
# ดู Supabase service details
coolify services list
coolify services show supabase-service-name
```

---

## 📋 วิธีที่ 3: ตรวจสอบใน Environment Variables

1. ใน Coolify Dashboard → Supabase service
2. ไปที่ **Settings** → **Environment Variables**
3. ดู `POSTGRES_PASSWORD` หรือ `DATABASE_URL`
4. ถ้ามี `DATABASE_URL` อยู่แล้ว → คัดลอกมาใช้ได้เลย

---

## 🔍 ตัวอย่าง Connection String

### รูปแบบมาตรฐาน:
```
postgresql://[USERNAME]:[PASSWORD]@[HOST]:[PORT]/[DATABASE]
```

### ตัวอย่างจริง:
```
postgresql://postgres:mySecurePassword123@supabase-xyz.coolify.local:5432/postgres
```

### ถ้าใช้ Public IP:
```
postgresql://postgres:mySecurePassword123@203.0.113.50:5432/postgres
```

### ถ้าใช้ Domain:
```
postgresql://postgres:mySecurePassword123@supabase.yourdomain.com:5432/postgres
```

---

## 🔄 แปลง Local Connection String เป็น Public

### ถ้าเห็น Connection String เป็น `127.0.0.1` (Local)

**Connection String ที่เห็น:**
```
postgresql://postgres:[YOUR-PASSWORD]@127.0.0.1:5432/postgres
```

**ปัญหาที่เกิดขึ้น:**
- `127.0.0.1` = localhost (ใช้ได้เฉพาะใน Coolify network)
- Vercel อยู่คนละ network → **เชื่อมต่อไม่ได้!**

**วิธีแก้ไข:**

#### ขั้นตอนที่ 1: หา Public Host/IP

1. **ดูจาก Coolify Dashboard:**
   - ไปที่ Supabase service → **Settings** → **Network** หรือ **Domains**
   - ดู **Public IP** หรือ **Domain** ของ Supabase
   - เช่น: `sb.prhmedicine.cloud` หรือ IP address

2. **ดูจาก Supabase Studio URL:**
   - จากภาพที่เห็น: `sb.prhmedicine.cloud`
   - นี่คือ public domain ของ Supabase

#### ขั้นตอนที่ 2: แทนที่ Host

**เปลี่ยนจาก:**
```
postgresql://postgres:[YOUR-PASSWORD]@127.0.0.1:5432/postgres
```

**เป็น:**
```
postgresql://postgres:[YOUR-PASSWORD]@sb.prhmedicine.cloud:5432/postgres
```

**หรือถ้าใช้ IP:**
```
postgresql://postgres:[YOUR-PASSWORD]@[PUBLIC-IP]:5432/postgres
```

#### ขั้นตอนที่ 3: เปิด Firewall

1. ใน Coolify → Supabase service → **Settings** → **Firewall** หรือ **Network**
2. เพิ่ม **Allowed IPs:**
   - `0.0.0.0/0` (สำหรับ development - อนุญาตทุก IP)
   - หรือ IP เฉพาะของ Vercel (ถ้ารู้)

---

## ⚠️ ข้อควรระวัง

### 1. Password มีอักขระพิเศษ
ถ้า password มีอักขระพิเศษ (เช่น `@`, `#`, `%`) ต้อง URL encode:

**ตัวอย่าง:**
- Password: `my@pass#123`
- URL encoded: `my%40pass%23123`
- Connection String: `postgresql://postgres:my%40pass%23123@host:5432/postgres`

### 2. Host เป็น Private Network
ถ้า Supabase อยู่ใน private network:
- ต้องเปิด firewall ให้ Vercel เข้าถึงได้
- หรือใช้ public IP/domain
- หรือตั้งค่า reverse proxy

### 3. Firewall Settings
1. ไปที่ Supabase service → **Settings** → **Network** หรือ **Firewall**
2. เพิ่ม IP range: `0.0.0.0/0` (สำหรับ development)
3. หรือ IP เฉพาะของ Vercel

---

## 🧪 ทดสอบ Connection String

### ใช้ Python:
```python
import psycopg2

DATABASE_URL = "postgresql://postgres:password@host:5432/postgres"

try:
    conn = psycopg2.connect(DATABASE_URL)
    print("✅ Connection successful!")
    conn.close()
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

### ใช้ psql:
```bash
psql "postgresql://postgres:password@host:5432/postgres"
```

---

## 📝 Checklist

- [ ] เข้า Coolify Dashboard แล้ว
- [ ] ไปที่ Supabase service แล้ว
- [ ] หา Connection String หรือข้อมูลแยกส่วนแล้ว
- [ ] สร้าง Connection String แล้ว
- [ ] ทดสอบ connection สำเร็จแล้ว
- [ ] เปิด firewall แล้ว (ถ้าจำเป็น)
- [ ] ตั้งค่าใน Vercel แล้ว

---

## 🔗 Links ที่เกี่ยวข้อง

- **Coolify Dashboard:** (URL ของ Coolify ของคุณ)
- **Vercel Environment Variables:** https://vercel.com/prhdev222s-projects/medfiles/settings/environment-variables

---

## 💡 Tips

1. **เก็บ Connection String ไว้ในที่ปลอดภัย** - อย่า commit ไปยัง Git
2. **ใช้ Environment Variables** - ตั้งค่าใน Vercel Dashboard
3. **ทดสอบก่อนใช้** - ใช้ Python หรือ psql ทดสอบ connection
4. **เปิด Firewall** - ต้องเปิดให้ Vercel เข้าถึงได้

---

**Happy Connecting! 🔗**

