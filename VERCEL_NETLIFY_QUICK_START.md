# 🚀 Quick Start: Deploy บน Vercel/Netlify (ฟรี) + Supabase

คู่มือเริ่มต้นเร็วสำหรับ deploy ระบบจัดการโรงพยาบาลบน Vercel หรือ Netlify (ฟรี) พร้อมใช้ Supabase จาก Coolify

## 🎯 เลือก Platform

### Vercel (แนะนำ)
- ✅ ง่ายกว่า
- ✅ Python support ดีกว่า
- ✅ Auto-detection ดี

### Netlify
- ✅ ฟรี tier ดี
- ✅ Functions ทำงานได้ดี
- ⚠️ ต้องตั้งค่าเพิ่มเติม

---

## 📋 ขั้นตอนการ Deploy

### 1. เตรียม Supabase Connection

**ใน Coolify:**
1. ไปที่ Supabase service
2. เปิด **Firewall** → เพิ่ม `0.0.0.0/0` (หรือ IP เฉพาะ)
3. คัดลอก **Connection String**

**รูปแบบ:**
```
postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres
```

### 2. Deploy บน Vercel

#### วิธีที่ 1: GitHub (แนะนำ)

1. **Push code ไปยัง GitHub**
   ```bash
   git add .
   git commit -m "Prepare for Vercel"
   git push origin main
   ```

2. **เชื่อมต่อ Vercel**
   - ไปที่ [vercel.com](https://vercel.com)
   - New Project → เลือก repository
   - Vercel จะ detect Flask อัตโนมัติ

3. **ตั้งค่า Environment Variables**
   ```env
   SECRET_KEY=<สร้างด้วย: python -c 'import secrets; print(secrets.token_hex(32))'>
   DATABASE_URL=postgresql://postgres:password@host:5432/postgres
   CORS_ORIGINS=https://your-app.vercel.app
   VERCEL=1
   ```

4. **Deploy!**
   - Vercel จะ deploy อัตโนมัติ

#### วิธีที่ 2: Vercel CLI

```bash
npm i -g vercel
vercel login
vercel
vercel --prod
```

### 3. Deploy บน Netlify

#### วิธีที่ 1: GitHub

1. **Push code ไปยัง GitHub**

2. **เชื่อมต่อ Netlify**
   - ไปที่ [netlify.com](https://netlify.com)
   - New site from Git → เลือก repository

3. **ตั้งค่า Build**
   - Build command: (ไม่ต้องใส่)
   - Functions directory: `netlify/functions`

4. **ตั้งค่า Environment Variables**
   ```env
   SECRET_KEY=<สร้างด้วย: python -c 'import secrets; print(secrets.token_hex(32))'>
   DATABASE_URL=postgresql://postgres:password@host:5432/postgres
   CORS_ORIGINS=https://your-app.netlify.app
   NETLIFY=true
   ```

5. **Deploy!**

---

## ⚙️ การปรับ Code

### สำหรับ Vercel:

ไฟล์ `vercel.json` มีอยู่แล้ว - ไม่ต้องแก้ไขอะไร

### สำหรับ Netlify:

ไฟล์ `netlify.toml` และ `netlify/functions/server.py` มีอยู่แล้ว

### ปรับ `app.py`:

เพิ่มการตรวจสอบ platform:

```python
import os

# ตรวจสอบ platform
IS_VERCEL = os.getenv('VERCEL') == '1'
IS_NETLIFY = os.getenv('NETLIFY') == 'true'
IS_SERVERLESS = IS_VERCEL or IS_NETLIFY

if IS_SERVERLESS:
    # ปรับ settings สำหรับ serverless
    app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB
    # ปิด backup system (ไม่ทำงานใน serverless)
```

---

## 🔐 Environment Variables

### สำหรับ Vercel:

ใน Vercel Dashboard → Settings → Environment Variables:

```env
FLASK_ENV=production
SECRET_KEY=<สร้างด้วย: python -c 'import secrets; print(secrets.token_hex(32))'>
DATABASE_URL=postgresql://postgres:password@supabase-host:5432/postgres
CORS_ORIGINS=https://your-app.vercel.app
VERCEL=1
```

### สำหรับ Netlify:

ใน Netlify Dashboard → Site settings → Environment variables:

```env
FLASK_ENV=production
SECRET_KEY=<สร้างด้วย: python -c 'import secrets; print(secrets.token_hex(32))'>
DATABASE_URL=postgresql://postgres:password@supabase-host:5432/postgres
CORS_ORIGINS=https://your-app.netlify.app
NETLIFY=true
```

---

## ✅ Checklist

- [ ] Supabase firewall เปิดแล้ว
- [ ] ได้ Connection String จาก Supabase
- [ ] ไฟล์ `vercel.json` หรือ `netlify.toml` มีอยู่
- [ ] ตั้งค่า Environment Variables
- [ ] Push code ไปยัง GitHub
- [ ] Deploy บน Vercel/Netlify
- [ ] ทดสอบ database connection

---

## 🆘 Troubleshooting

### Database Connection Error

**แก้ไข:**
1. ตรวจสอบ firewall ใน Coolify
2. ตรวจสอบ connection string
3. ตรวจสอบว่า Supabase service ทำงานอยู่

### Timeout Error

**แก้ไข:**
1. Optimize database queries
2. ใช้ connection pooling
3. Cache responses

---

## 📚 ดูคู่มือฉบับเต็ม

- **Vercel:** [VERCEL_DEPLOY.md](./VERCEL_DEPLOY.md)
- **Netlify:** [NETLIFY_DEPLOY.md](./NETLIFY_DEPLOY.md)

---

**Happy Deploying! 🚀**


