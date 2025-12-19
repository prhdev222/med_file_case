# 🚀 คู่มือการ Deploy บน Netlify (ฟรี) พร้อม Supabase

คู่มือนี้จะแนะนำวิธีการ deploy ระบบจัดการโรงพยาบาลลงบน Netlify (ฟรี tier) และใช้ Supabase database จาก Coolify

## 📋 สารบัญ

1. [ข้อกำหนดและข้อจำกัด](#ข้อกำหนดและข้อจำกัด)
2. [เตรียมความพร้อม](#เตรียมความพร้อม)
3. [การตั้งค่า Supabase Connection](#การตั้งค่า-supabase-connection)
4. [การปรับ Code สำหรับ Netlify](#การปรับ-code-สำหรับ-netlify)
5. [การ Deploy บน Netlify](#การ-deploy-บน-netlify)
6. [การตั้งค่า Environment Variables](#การตั้งค่า-environment-variables)
7. [Troubleshooting](#troubleshooting)

---

## ⚠️ ข้อกำหนดและข้อจำกัด

### Netlify Free Tier:
- ✅ ฟรี 100%
- ✅ Serverless functions
- ✅ Auto HTTPS
- ✅ Global CDN
- ⚠️ 10-second timeout สำหรับ serverless functions
- ⚠️ 100GB bandwidth/month
- ⚠️ ไม่รองรับ WebSocket
- ⚠️ ไม่รองรับ file uploads ขนาดใหญ่

### Supabase จาก Coolify:
- ✅ ใช้เป็น external database ได้
- ✅ Connection string จาก Coolify
- ✅ ต้องเปิด firewall ให้ Netlify เข้าถึงได้

---

## ✅ เตรียมความพร้อม

### 1. สร้างไฟล์สำหรับ Netlify

**สร้าง `netlify.toml`:**

```toml
[build]
  command = "echo 'No build needed'"
  functions = "netlify/functions"

[[plugins]]
  package = "@netlify/plugin-python"

[functions]
  node_bundler = "esbuild"
```

### 2. สร้าง Netlify Function

Netlify ต้องการ serverless function ในโฟลเดอร์ `netlify/functions/`

---

## 🔗 การตั้งค่า Supabase Connection

### ขั้นตอนที่ 1: เปิด Firewall ใน Coolify

1. ไปที่ Supabase service ใน Coolify
2. เปิด **Settings** → **Network** หรือ **Firewall**
3. เพิ่ม IP ranges ของ Netlify:
   - `0.0.0.0/0` (สำหรับ development)
   - หรือ IP เฉพาะของ Netlify

### ขั้นตอนที่ 2: ได้ Connection String

1. ใน Coolify → Supabase service
2. คัดลอก **Connection String**
3. รูปแบบ: `postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres`

---

## 🔧 การปรับ Code สำหรับ Netlify

### 1. สร้าง `netlify/functions/server.py`

```python
from app import app
import json

def handler(event, context):
    """Netlify serverless function handler"""
    # Convert Netlify event to WSGI environ
    environ = {
        'REQUEST_METHOD': event.get('httpMethod', 'GET'),
        'PATH_INFO': event.get('path', '/'),
        'QUERY_STRING': event.get('queryStringParameters', {}),
        'SERVER_NAME': 'localhost',
        'SERVER_PORT': '80',
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'https',
        'wsgi.input': event.get('body', ''),
        'wsgi.errors': None,
        'wsgi.multithread': False,
        'wsgi.multiprocess': False,
        'wsgi.run_once': False,
    }
    
    # Add headers
    for key, value in event.get('headers', {}).items():
        environ[f'HTTP_{key.upper().replace("-", "_")}'] = value
    
    # Call Flask app
    with app.app_context():
        response = app(environ, lambda status, headers: None)
        body = b''.join(response).decode('utf-8')
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'text/html'},
            'body': body
        }
```

### 2. ปรับ `app.py` สำหรับ Serverless

```python
import os

# ตรวจสอบว่า run บน Netlify
IS_NETLIFY = os.getenv('NETLIFY') == 'true'

if IS_NETLIFY:
    # ปรับ settings สำหรับ serverless
    app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB
```

---

## 🚀 การ Deploy บน Netlify

### วิธีที่ 1: Deploy จาก GitHub (แนะนำ)

1. **Push code ไปยัง GitHub**
   ```bash
   git add .
   git commit -m "Prepare for Netlify deployment"
   git push origin main
   ```

2. **เชื่อมต่อ Netlify กับ GitHub**
   - ไปที่ [netlify.com](https://netlify.com)
   - สร้าง account (ใช้ GitHub login)
   - คลิก **"New site from Git"**
   - เลือก repository: `med_file_case`

3. **ตั้งค่า Build Settings**
   - **Build command:** (ไม่ต้องใส่)
   - **Publish directory:** (ไม่ต้องใส่)
   - **Functions directory:** `netlify/functions`

4. **Deploy!**
   - Netlify จะ build และ deploy อัตโนมัติ

### วิธีที่ 2: Deploy ด้วย Netlify CLI

```bash
# ติดตั้ง Netlify CLI
npm install -g netlify-cli

# Login
netlify login

# Deploy
netlify deploy

# Deploy to production
netlify deploy --prod
```

---

## 🔐 การตั้งค่า Environment Variables

ใน Netlify Dashboard → **Site settings** → **Environment variables**:

### ตัวแปรที่จำเป็น:

```env
# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False

# Security
SECRET_KEY=your-super-secret-production-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# Database - Supabase จาก Coolify
DATABASE_URL=postgresql://postgres:[PASSWORD]@[SUPABASE-HOST]:5432/postgres

# CORS
CORS_ORIGINS=https://your-app.netlify.app,https://www.your-domain.com

# Upload Settings
UPLOAD_FOLDER=supabase_storage
MAX_CONTENT_LENGTH=10485760

# Netlify
NETLIFY=true
```

---

## 📝 สร้างไฟล์ที่จำเป็น

### 1. `netlify.toml`

```toml
[build]
  command = "echo 'No build needed'"
  functions = "netlify/functions"
  publish = "."

[[plugins]]
  package = "@netlify/plugin-python"

[functions]
  node_bundler = "esbuild"
  included_files = ["app.py", "models/**", "routes/**", "services/**"]

[[redirects]]
  from = "/*"
  to = "/.netlify/functions/server"
  status = 200
```

### 2. `netlify/functions/server.py`

ดูโค้ดด้านบน

---

## 🔧 Troubleshooting

### ปัญหา: Database Connection Error

**แก้ไข:**
1. เปิด firewall ใน Coolify
2. ใช้ public IP หรือ domain
3. ตรวจสอบ connection string

### ปัญหา: Function Not Found

**แก้ไข:**
1. ตรวจสอบว่าไฟล์อยู่ใน `netlify/functions/`
2. ตรวจสอบ `netlify.toml` configuration
3. ตรวจสอบ build logs

---

## 📊 ข้อดีและข้อเสีย

### ข้อดี:
- ✅ ฟรี 100%
- ✅ Auto HTTPS
- ✅ Global CDN
- ✅ Easy deployment

### ข้อเสีย:
- ⚠️ 10-second timeout
- ⚠️ ไม่รองรับ WebSocket
- ⚠️ 100GB bandwidth limit

---

## 🎯 Checklist

- [ ] สร้าง `netlify.toml`
- [ ] สร้าง `netlify/functions/server.py`
- [ ] ปรับ `app.py` สำหรับ serverless
- [ ] ตั้งค่า Supabase firewall
- [ ] ตั้งค่า Environment Variables
- [ ] Deploy บน Netlify

---

**Happy Deploying! 🚀**

