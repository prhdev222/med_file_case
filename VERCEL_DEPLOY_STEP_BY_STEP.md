# 🚀 คู่มือ Deploy บน Vercel แบบ Step-by-Step

คู่มือนี้จะพาคุณ deploy ระบบจัดการโรงพยาบาลลงบน Vercel ทีละขั้นตอน

## ✅ สิ่งที่เตรียมไว้แล้ว

- ✅ Code ถูก push ไป GitHub แล้ว
- ✅ ไฟล์ `vercel.json` มีอยู่แล้ว
- ✅ ไฟล์ `api/index.py` มีอยู่แล้ว
- ✅ `app.py` ปรับให้รองรับ serverless แล้ว

---

## 📋 ขั้นตอนการ Deploy

### ขั้นตอนที่ 1: สร้าง Account Vercel

1. ไปที่ [vercel.com](https://vercel.com)
2. คลิก **"Sign Up"**
3. เลือก **"Continue with GitHub"** (แนะนำ)
4. อนุญาต Vercel เข้าถึง GitHub repositories

### ขั้นตอนที่ 2: สร้าง Project ใหม่

1. หลังจาก login แล้ว คลิก **"Add New..."** → **"Project"**
2. ในหน้า **"Import Git Repository"**:
   - ค้นหา repository: `prhdev222/med_file_case`
   - หรือพิมพ์ `med_file_case` ในช่องค้นหา
   - คลิก **"Import"**

### ขั้นตอนที่ 3: ตั้งค่า Project

Vercel จะ auto-detect Flask ให้อัตโนมัติ แต่ให้ตรวจสอบ:

**Project Settings:**
- **Framework Preset:** Other (หรือ Flask ถ้ามี)
- **Root Directory:** `./` (default)
- **Build Command:** (ไม่ต้องใส่ - Vercel จะ detect อัตโนมัติ)
- **Output Directory:** (ไม่ต้องใส่)

**Environment Variables:**
คลิก **"Environment Variables"** และเพิ่ม:

```env
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=<สร้างด้วย: python -c 'import secrets; print(secrets.token_hex(32))'>
DATABASE_URL=postgresql://postgres:password@host:5432/postgres
CORS_ORIGINS=https://your-app.vercel.app
VERCEL=1
```

**วิธีสร้าง SECRET_KEY:**
```bash
python -c 'import secrets; print(secrets.token_hex(32))'
```

### ขั้นตอนที่ 4: Deploy!

1. คลิก **"Deploy"** ที่มุมล่างขวา
2. รอให้ Vercel build และ deploy (ประมาณ 2-5 นาที)
3. เมื่อเสร็จแล้ว Vercel จะแสดง URL ของคุณ:
   - เช่น: `https://med-file-case.vercel.app`

### ขั้นตอนที่ 5: ตรวจสอบ Deployment

1. เปิด URL ที่ Vercel ให้มา
2. ตรวจสอบว่า:
   - ✅ หน้าแรกแสดงได้
   - ✅ Health check: `https://your-app.vercel.app/health`
   - ✅ Login page: `https://your-app.vercel.app/admin/login`

---

## 🔐 การตั้งค่า Environment Variables

### ตัวแปรที่จำเป็น:

1. **FLASK_ENV**
   ```
   production
   ```

2. **SECRET_KEY** (สำคัญมาก!)
   ```bash
   # สร้างด้วย:
   python -c 'import secrets; print(secrets.token_hex(32))'
   ```
   คัดลอกผลลัพธ์มาใส่

3. **DATABASE_URL** (Supabase จาก Coolify)
   ```
   postgresql://postgres:[PASSWORD]@[SUPABASE-HOST]:5432/postgres
   ```
   แทนที่ `[PASSWORD]` และ `[SUPABASE-HOST]` ด้วยค่าจริง

4. **CORS_ORIGINS**
   ```
   https://your-app.vercel.app
   ```
   ใช้ URL ที่ Vercel ให้มา

5. **VERCEL**
   ```
   1
   ```

### วิธีเพิ่ม Environment Variables:

1. ใน Vercel Dashboard → **Settings** → **Environment Variables**
2. คลิก **"Add New"**
3. ใส่ **Name** และ **Value**
4. เลือก **Environment:** Production, Preview, Development (เลือกทั้งหมด)
5. คลิก **"Save"**

---

## 🔗 การตั้งค่า Supabase Connection

### 1. เปิด Firewall ใน Coolify

1. ไปที่ Coolify Dashboard → Supabase service
2. เปิด **Settings** → **Network** หรือ **Firewall**
3. เพิ่ม IP range: `0.0.0.0/0` (หรือ IP เฉพาะของ Vercel)

### 2. ได้ Connection String

1. ใน Coolify → Supabase service
2. คัดลอก **Connection String**
3. ใช้ใน `DATABASE_URL` environment variable

---

## ⚠️ ข้อจำกัดที่ต้องรู้

### 1. File Storage
- ❌ Vercel ไม่รองรับ local file storage
- ✅ ต้องใช้ Supabase Storage หรือ S3 แทน
- ⚠️ File uploads ขนาดใหญ่ (>10MB) อาจมีปัญหา

### 2. Backup System
- ❌ Backup system ไม่ทำงานใน serverless
- ✅ ใช้ Supabase backup แทน

### 3. Timeout
- ⚠️ Function timeout: 10 seconds
- ✅ Optimize database queries
- ✅ ใช้ connection pooling

---

## 🆘 Troubleshooting

### ปัญหา: Build Failed

**Error:** `ModuleNotFoundError` หรือ `ImportError`

**แก้ไข:**
1. ตรวจสอบ `requirements.txt` มี dependencies ครบ
2. ตรวจสอบว่าไฟล์ `vercel.json` ถูกต้อง
3. ดู Build Logs ใน Vercel Dashboard

### ปัญหา: Database Connection Error

**Error:** `could not connect to server`

**แก้ไข:**
1. ตรวจสอบ firewall ใน Coolify เปิดแล้ว
2. ตรวจสอบ `DATABASE_URL` format ถูกต้อง
3. ตรวจสอบว่า Supabase service ทำงานอยู่

### ปัญหา: Template Not Found

**Error:** `TemplateNotFound: home.html`

**แก้ไข:**
1. ตรวจสอบว่าไฟล์ templates ถูก push ไป GitHub แล้ว
2. ตรวจสอบ path ของ templates ใน `app.py`

### ปัญหา: Function Timeout

**Error:** `Function execution exceeded timeout`

**แก้ไข:**
1. Optimize database queries
2. ใช้ connection pooling
3. Cache responses
4. แยกงานหนักออกเป็น background jobs

---

## 📊 ตรวจสอบ Deployment

### 1. ดู Logs

1. ใน Vercel Dashboard → **Deployments**
2. คลิก deployment ล่าสุด
3. ดู **"Function Logs"** หรือ **"Build Logs"**

### 2. ทดสอบ Endpoints

```bash
# Health check
curl https://your-app.vercel.app/health

# หน้าแรก
curl https://your-app.vercel.app/

# Stats
curl https://your-app.vercel.app/stats
```

### 3. ตรวจสอบ Database

1. Login เข้าระบบ
2. ทดสอบ CRUD operations
3. ตรวจสอบ logs ใน Vercel

---

## 🔄 การอัปเดต

### Auto Deploy (แนะนำ)

Vercel จะ auto-deploy เมื่อคุณ push code ไปยัง GitHub:

```bash
git add .
git commit -m "Update code"
git push origin main
```

Vercel จะ deploy อัตโนมัติ!

### Manual Deploy

1. ใน Vercel Dashboard → **Deployments**
2. คลิก **"Redeploy"** → **"Use existing Build Cache"** หรือ **"Rebuild"**

---

## 📝 Checklist

- [ ] สร้าง Vercel account แล้ว
- [ ] เชื่อมต่อ GitHub repository แล้ว
- [ ] ตั้งค่า Environment Variables แล้ว
- [ ] เปิด Supabase firewall แล้ว
- [ ] ได้ Connection String จาก Supabase แล้ว
- [ ] Deploy สำเร็จแล้ว
- [ ] ทดสอบ health check ผ่านแล้ว
- [ ] ทดสอบ login ผ่านแล้ว
- [ ] ทดสอบ database connection ผ่านแล้ว

---

## 🎉 เสร็จสิ้น!

หลังจาก deploy สำเร็จ คุณจะได้:

- ✅ URL: `https://your-app.vercel.app`
- ✅ Auto HTTPS
- ✅ Global CDN
- ✅ Auto scaling

**Happy Deploying! 🚀**

---

## 📞 การติดต่อ

หากมีปัญหา:
- **Vercel Docs:** https://vercel.com/docs
- **GitHub Issues:** https://github.com/prhdev222/med_file_case/issues


