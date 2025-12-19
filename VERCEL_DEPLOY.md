# 🚀 คู่มือการ Deploy บน Vercel (ฟรี) พร้อม Supabase

คู่มือนี้จะแนะนำวิธีการ deploy ระบบจัดการโรงพยาบาลลงบน Vercel (ฟรี tier) และใช้ Supabase database จาก Coolify

## 📋 สารบัญ

1. [ข้อกำหนดและข้อจำกัด](#ข้อกำหนดและข้อจำกัด)
2. [เตรียมความพร้อม](#เตรียมความพร้อม)
3. [การตั้งค่า Supabase Connection](#การตั้งค่า-supabase-connection)
4. [การปรับ Code สำหรับ Vercel](#การปรับ-code-สำหรับ-vercel)
5. [การ Deploy บน Vercel](#การ-deploy-บน-vercel)
6. [การตั้งค่า Environment Variables](#การตั้งค่า-environment-variables)
7. [Troubleshooting](#troubleshooting)

---

## ⚠️ ข้อกำหนดและข้อจำกัด

### Vercel Free Tier:
- ✅ ฟรี 100%
- ✅ Serverless functions
- ✅ Auto HTTPS
- ✅ Global CDN
- ⚠️ 10-second timeout สำหรับ serverless functions
- ⚠️ ไม่รองรับ WebSocket (แต่ Supabase Realtime ใช้ polling)
- ⚠️ ไม่รองรับ file uploads ขนาดใหญ่ (แนะนำใช้ Supabase Storage)

### Supabase จาก Coolify:
- ✅ ใช้เป็น external database ได้
- ✅ Connection string จาก Coolify
- ✅ ต้องเปิด firewall ให้ Vercel เข้าถึงได้

---

## ✅ เตรียมความพร้อม

### 1. สร้างไฟล์สำหรับ Vercel

**สร้าง `vercel.json`:**

```json
{
  "version": 2,
  "builds": [
    {
      "src": "app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app.py"
    }
  ],
  "env": {
    "PYTHON_VERSION": "3.11"
  }
}
```

### 2. สร้าง `api/index.py` สำหรับ Vercel

Vercel ต้องการไฟล์ในโฟลเดอร์ `api/` สำหรับ serverless functions

---

## 🔗 การตั้งค่า Supabase Connection

### ขั้นตอนที่ 1: เปิด Firewall ใน Coolify

1. ไปที่ Supabase service ใน Coolify
2. เปิด **Settings** → **Network** หรือ **Firewall**
3. เพิ่ม IP ranges ของ Vercel:
   - `0.0.0.0/0` (สำหรับ development - เปิดทั้งหมด)
   - หรือ IP เฉพาะของ Vercel (ดูจาก Vercel docs)

### ขั้นตอนที่ 2: ได้ Connection String

1. ใน Coolify → Supabase service
2. คัดลอก **Connection String** หรือ **Database URL**
3. รูปแบบ: `postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres`

**หมายเหตุ:** 
- ถ้า Supabase อยู่ใน private network ต้องใช้ public IP หรือ domain
- หรือตั้งค่า reverse proxy ใน Coolify

---

## 🔧 การปรับ Code สำหรับ Vercel

### 1. สร้าง `api/index.py`

Vercel ต้องการ handler function:

```python
from app import app

# Vercel serverless handler
def handler(request):
    return app(request.environ, request.start_response)

# หรือใช้ WSGI adapter
from vercel import WSGI
handler = WSGI(app)
```

### 2. ปรับ `app.py` สำหรับ Serverless

เพิ่มการตรวจสอบว่า run บน Vercel:

```python
import os

# ตรวจสอบว่า run บน Vercel
IS_VERCEL = os.getenv('VERCEL') == '1'

if IS_VERCEL:
    # ปรับ settings สำหรับ serverless
    app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB (Vercel limit)
```

### 3. ปรับ File Uploads

สำหรับ Vercel ควรใช้ Supabase Storage แทน local storage:

```python
# ใช้ Supabase Storage สำหรับไฟล์
# แทนที่จะเก็บใน local storage
```

---

## 🚀 การ Deploy บน Vercel

### วิธีที่ 1: Deploy จาก GitHub (แนะนำ)

1. **Push code ไปยัง GitHub**
   ```bash
   git add .
   git commit -m "Prepare for Vercel deployment"
   git push origin main
   ```

2. **เชื่อมต่อ Vercel กับ GitHub**
   - ไปที่ [vercel.com](https://vercel.com)
   - สร้าง account (ใช้ GitHub login)
   - คลิก **"New Project"**
   - เลือก repository: `med_file_case`

3. **ตั้งค่า Build Settings**
   - **Framework Preset:** Other
   - **Root Directory:** `./`
   - **Build Command:** (ไม่ต้องใส่ - Vercel จะ detect อัตโนมัติ)
   - **Output Directory:** (ไม่ต้องใส่)

4. **Deploy!**
   - Vercel จะ build และ deploy อัตโนมัติ

### วิธีที่ 2: Deploy ด้วย Vercel CLI

```bash
# ติดตั้ง Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy
vercel

# Deploy to production
vercel --prod
```

---

## 🔐 การตั้งค่า Environment Variables

ใน Vercel Dashboard → **Settings** → **Environment Variables**:

### ตัวแปรที่จำเป็น:

```env
# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False

# Security
SECRET_KEY=your-super-secret-production-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# Database - Supabase จาก Coolify
# แทนที่ [PASSWORD] และ [HOST] ด้วยค่าจริง
DATABASE_URL=postgresql://postgres:[PASSWORD]@[SUPABASE-HOST]:5432/postgres

# CORS
CORS_ORIGINS=https://your-app.vercel.app,https://www.your-domain.com

# Upload Settings (ใช้ Supabase Storage)
UPLOAD_FOLDER=supabase_storage
MAX_CONTENT_LENGTH=10485760

# Vercel
VERCEL=1
```

### วิธีสร้าง SECRET_KEY:

```bash
python -c 'import secrets; print(secrets.token_hex(32))'
```

---

## 📝 สร้างไฟล์ที่จำเป็น

### 1. `vercel.json`

```json
{
  "version": 2,
  "builds": [
    {
      "src": "app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app.py"
    }
  ],
  "env": {
    "PYTHON_VERSION": "3.11"
  },
  "functions": {
    "app.py": {
      "maxDuration": 10
    }
  }
}
```

### 2. `api/index.py` (ถ้าจำเป็น)

```python
from app import app
from vercel import WSGI

handler = WSGI(app)
```

---

## ⚙️ การปรับ Code

### ปรับ `app.py` สำหรับ Vercel:

```python
import os

# ตรวจสอบว่า run บน Vercel
IS_VERCEL = os.getenv('VERCEL') == '1'

if IS_VERCEL:
    # ปรับ settings สำหรับ serverless
    app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB
    # ปิด backup system (ไม่ทำงานใน serverless)
    # backup_system = None
```

---

## 🔧 Troubleshooting

### ปัญหา: Database Connection Error

**สาเหตุ:**
- Supabase อยู่ใน private network
- Firewall block Vercel IPs

**แก้ไข:**
1. เปิด firewall ใน Coolify ให้ Vercel เข้าถึงได้
2. ใช้ public IP หรือ domain สำหรับ Supabase
3. ตั้งค่า reverse proxy ใน Coolify

### ปัญหา: Timeout (10 seconds)

**สาเหตุ:**
- Function ใช้เวลานานเกิน 10 วินาที

**แก้ไข:**
1. Optimize database queries
2. ใช้ background jobs สำหรับงานหนัก
3. แยกงานออกเป็นหลาย functions

### ปัญหา: File Upload ไม่ทำงาน

**สาเหตุ:**
- Vercel ไม่รองรับ local file storage

**แก้ไข:**
1. ใช้ Supabase Storage
2. หรือใช้ external storage (AWS S3, Cloudinary)

---

## 📊 ข้อดีและข้อเสีย

### ข้อดี:
- ✅ ฟรี 100%
- ✅ Auto HTTPS
- ✅ Global CDN
- ✅ Auto scaling
- ✅ Easy deployment

### ข้อเสีย:
- ⚠️ 10-second timeout
- ⚠️ ไม่รองรับ WebSocket
- ⚠️ ไม่รองรับ local file storage
- ⚠️ Cold start delay

---

## 🎯 Checklist

- [ ] สร้าง `vercel.json`
- [ ] ปรับ `app.py` สำหรับ serverless
- [ ] ตั้งค่า Supabase firewall
- [ ] ได้ Connection String จาก Supabase
- [ ] ตั้งค่า Environment Variables ใน Vercel
- [ ] Push code ไปยัง GitHub
- [ ] Deploy บน Vercel
- [ ] ทดสอบ database connection
- [ ] ทดสอบ file uploads (ถ้าใช้)

---

## 📞 การติดต่อ

หากมีปัญหาหรือคำถาม:
- **Vercel Docs:** https://vercel.com/docs
- **GitHub Issues:** https://github.com/prhdev222/med_file_case/issues

---

**Happy Deploying! 🚀**

