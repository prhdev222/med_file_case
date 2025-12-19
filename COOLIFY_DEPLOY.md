# 🚀 คู่มือการ Deploy บน Coolify VPS

คู่มือนี้จะแนะนำวิธีการ deploy ระบบจัดการโรงพยาบาลลงบน Coolify VPS ของคุณ

## 📋 สารบัญ

1. [เตรียมความพร้อม](#เตรียมความพร้อม)
2. [การตั้งค่าใน Coolify](#การตั้งค่าใน-coolify)
3. [การตั้งค่า Database](#การตั้งค่า-database)
4. [การตั้งค่า Environment Variables](#การตั้งค่า-environment-variables)
5. [การตั้งค่า Domain และ SSL](#การตั้งค่า-domain-และ-ssl)
6. [การ Deploy](#การ-deploy)
7. [การอัปเดต](#การอัปเดต)
8. [Troubleshooting](#troubleshooting)

---

## ✅ เตรียมความพร้อม

### 1. ตรวจสอบไฟล์ที่จำเป็น

ตรวจสอบว่าโปรเจคมีไฟล์เหล่านี้:
- ✅ `Dockerfile` - สำหรับ build Docker image
- ✅ `.dockerignore` - สำหรับ exclude files ที่ไม่จำเป็น
- ✅ `requirements.txt` - Python dependencies
- ✅ `frontend/package.json` - Frontend dependencies

### 2. Build และทดสอบ Docker Image (Optional)

```bash
# Build Docker image
docker build -t hospital-admin:latest .

# ทดสอบ run locally
docker run -p 5000:5000 \
  -e SECRET_KEY=test-secret-key \
  -e DATABASE_URL=sqlite:///hospital.db \
  hospital-admin:latest
```

---

## 🎯 การตั้งค่าใน Coolify

### ขั้นตอนที่ 1: เข้าสู่ Coolify Dashboard

1. เปิดเว็บเบราว์เซอร์ไปที่ Coolify ของคุณ (เช่น `https://coolify.yourdomain.com`)
2. Login เข้าสู่ระบบ

### ขั้นตอนที่ 2: สร้าง Resource ใหม่

1. คลิก **"New Resource"** หรือ **"+"**
2. เลือก **"Application"** หรือ **"Web Application"**

### ขั้นตอนที่ 3: เชื่อมต่อ Git Repository

1. เลือก **"Git Repository"**
2. เชื่อมต่อ GitHub/GitLab/Bitbucket ของคุณ
3. เลือก repository: `prhdev222/med_file_case`
4. เลือก branch: `main` (หรือ `master`)

### ขั้นตอนที่ 4: ตั้งค่า Build

**Build Pack:** เลือก **"Dockerfile"** (Coolify จะ detect Dockerfile อัตโนมัติ)

**Build Command:** (ไม่จำเป็นถ้าใช้ Dockerfile)
```
# Coolify จะใช้ Dockerfile อัตโนมัติ
```

**Start Command:** (ไม่จำเป็นถ้าใช้ Dockerfile)
```
# กำหนดใน Dockerfile แล้ว
```

### ขั้นตอนที่ 5: ตั้งค่า Port

- **Port:** `5000` (หรือ port ที่กำหนดใน Dockerfile)

---

## 💾 การตั้งค่า Database

### ตัวเลือกที่ 1: ใช้ Supabase จาก Coolify (แนะนำ - ถ้ามีอยู่แล้ว) ⭐

ถ้าคุณมี Supabase อยู่ใน Coolify แล้ว:

1. ใน Coolify Dashboard → ไปที่ **Supabase service** ของคุณ
2. คัดลอก **Connection String** หรือ **Database URL**
3. ใช้ Connection String ในรูปแบบ:
   ```
   postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres
   ```
4. ตั้งค่า `DATABASE_URL` ใน Environment Variables (ดูด้านล่าง)

**ข้อดีของ Supabase:**
- ✅ มี Dashboard สำหรับจัดการข้อมูล
- ✅ มี API อัตโนมัติ
- ✅ มี Authentication built-in
- ✅ มี Realtime features
- ✅ มี Storage สำหรับไฟล์

### ตัวเลือกที่ 2: ใช้ PostgreSQL จาก Coolify

1. ใน Coolify Dashboard → **"New Resource"** → **"Database"**
2. เลือก **"PostgreSQL"**
3. ตั้งค่า:
   - **Name:** `hospital-admin-db`
   - **Database Name:** `hospital_admin`
   - **Username:** `hospital_user`
   - **Password:** (ตั้งรหัสผ่านที่ปลอดภัย)
4. คลิก **"Deploy"**

### ตัวเลือกที่ 3: ใช้ SQLite (สำหรับทดสอบ)

ใช้ SQLite สำหรับ development/testing:
- ไม่ต้องสร้าง database แยก
- ตั้งค่า `DATABASE_URL=sqlite:///hospital.db` ใน Environment Variables

### ตัวเลือกที่ 4: ใช้ External Database

ถ้ามี PostgreSQL server อยู่แล้ว:
- ตั้งค่า `DATABASE_URL=postgresql://user:password@host:port/dbname`

---

## 🔐 การตั้งค่า Environment Variables

ใน Coolify Dashboard → **Environment Variables** → เพิ่ม:

### ตัวแปรที่จำเป็น:

```env
# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False

# Security (สำคัญมาก! เปลี่ยนเป็นค่าที่ปลอดภัย)
SECRET_KEY=your-super-secret-production-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# Database
# ถ้าใช้ Supabase จาก Coolify (แนะนำ):
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@[SUPABASE-HOST]:5432/postgres
# หรือถ้าใช้ PostgreSQL จาก Coolify:
DATABASE_URL=postgresql://hospital_user:your-password@hospital-admin-db:5432/hospital_admin
# หรือถ้าใช้ SQLite:
DATABASE_URL=sqlite:///hospital.db

# CORS (ตั้งค่าให้ตรงกับ domain ของคุณ)
CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com

# Upload Settings
UPLOAD_FOLDER=storage/uploads
MAX_CONTENT_LENGTH=52428800

# Server Settings
PORT=5000
HOST=0.0.0.0

# Backup Settings (Optional)
BACKUP_DIR=storage/backups
BACKUP_INTERVAL_HOURS=24
BACKUP_KEEP_DAYS=30
```

### วิธีสร้าง SECRET_KEY:

```bash
# ใช้ Python
python -c 'import secrets; print(secrets.token_hex(32))'

# หรือใช้ OpenSSL
openssl rand -hex 32
```

---

## 🌐 การตั้งค่า Domain และ SSL

### ขั้นตอนที่ 1: เพิ่ม Domain

1. ใน Coolify Dashboard → **"Domains"** หรือ **"FQDN"**
2. เพิ่ม domain ของคุณ:
   - **Domain:** `hospital.yourdomain.com`
   - **SSL:** Enable (Coolify จะขอ Let's Encrypt certificate อัตโนมัติ)

### ขั้นตอนที่ 2: ตั้งค่า DNS

ไปที่ DNS provider ของคุณ (เช่น Cloudflare, Namecheap) และเพิ่ม:

**Type A Record:**
```
Name: hospital (หรือ @ สำหรับ root domain)
Value: IP address ของ Coolify VPS
TTL: Auto หรือ 300
```

**หรือ CNAME Record:**
```
Name: hospital
Value: coolify.yourdomain.com
TTL: Auto
```

### ขั้นตอนที่ 3: รอ SSL Certificate

Coolify จะขอ SSL certificate จาก Let's Encrypt อัตโนมัติ (ใช้เวลา 1-5 นาที)

---

## 🚀 การ Deploy

### วิธีที่ 1: Deploy จาก Git (แนะนำ)

1. ใน Coolify Dashboard → **"Deploy"**
2. Coolify จะ:
   - Clone code จาก Git repository
   - Build Docker image จาก Dockerfile
   - Deploy container
   - ตั้งค่า networking และ SSL

3. รอให้ build เสร็จ (ประมาณ 3-5 นาที)

### วิธีที่ 2: Manual Deploy

1. **Build:**
   ```bash
   # ใน Coolify จะทำอัตโนมัติ
   docker build -t hospital-admin:latest .
   ```

2. **Run:**
   ```bash
   # Coolify จะจัดการให้
   docker run -d \
     --name hospital-admin \
     -p 5000:5000 \
     -e SECRET_KEY=... \
     -e DATABASE_URL=... \
     hospital-admin:latest
   ```

---

## 🔄 การอัปเดต

### Auto Deploy (แนะนำ)

1. ใน Coolify Dashboard → **"Settings"** → **"Auto Deploy"**
2. Enable **"Auto Deploy on Push"**
3. เมื่อคุณ push code ไปยัง GitHub, Coolify จะ deploy อัตโนมัติ

### Manual Deploy

1. ใน Coolify Dashboard → **"Deploy"** → **"Redeploy"**
2. หรือคลิก **"Force Redeploy"** เพื่อ rebuild จาก scratch

---

## 📊 การตรวจสอบ Logs

### ดู Logs ใน Coolify

1. ใน Coolify Dashboard → **"Logs"**
2. จะแสดง:
   - Build logs
   - Application logs
   - Error logs

### ดู Logs ผ่าน Docker (ถ้าจำเป็น)

```bash
# SSH เข้า VPS
ssh user@your-vps-ip

# ดู logs
docker logs hospital-admin -f
```

---

## 🛠️ Troubleshooting

### ปัญหา: Build Failed

**สาเหตุ:**
- Dependencies ติดตั้งไม่สำเร็จ
- Dockerfile มีปัญหา

**แก้ไข:**
1. ตรวจสอบ Build Logs ใน Coolify
2. ทดสอบ build local:
   ```bash
   docker build -t hospital-admin:latest .
   ```
3. ตรวจสอบ `requirements.txt` และ `frontend/package.json`

### ปัญหา: Application ไม่ทำงาน

**สาเหตุ:**
- Environment variables ไม่ครบ
- Database connection error
- Port conflict

**แก้ไข:**
1. ตรวจสอบ Environment Variables
2. ตรวจสอบ Database connection string
3. ตรวจสอบ Logs ใน Coolify Dashboard

### ปัญหา: Database Connection Error

**สาเหตุ:**
- `DATABASE_URL` ไม่ถูกต้อง
- Database service ยังไม่พร้อม

**แก้ไข:**
1. ตรวจสอบ `DATABASE_URL` format:
   ```
   postgresql://username:password@host:port/database
   ```
2. ตรวจสอบว่า Database service deploy แล้ว
3. ตรวจสอบ network connection ระหว่าง services

### ปัญหา: Frontend ไม่แสดงผล

**สาเหตุ:**
- Frontend build ไม่สำเร็จ
- Static files path ไม่ถูกต้อง

**แก้ไข:**
1. ตรวจสอบว่า `npm run build` สำเร็จใน build logs
2. ตรวจสอบ Dockerfile ว่า copy frontend build files ถูกต้อง

### ปัญหา: SSL Certificate ไม่ทำงาน

**สาเหตุ:**
- DNS ยังไม่ propagate
- Domain ไม่ชี้มาที่ VPS

**แก้ไข:**
1. ตรวจสอบ DNS:
   ```bash
   nslookup hospital.yourdomain.com
   ```
2. รอให้ DNS propagate (อาจใช้เวลา 5-30 นาที)
3. ลอง request certificate ใหม่ใน Coolify

---

## 📝 Checklist ก่อน Deploy

- [ ] ไฟล์ `Dockerfile` มีอยู่และถูกต้อง
- [ ] ไฟล์ `.dockerignore` มีอยู่
- [ ] `requirements.txt` มี dependencies ครบ
- [ ] `frontend/package.json` มี dependencies ครบ
- [ ] ตั้งค่า `SECRET_KEY` ใน Environment Variables
- [ ] ตั้งค่า `DATABASE_URL` ใน Environment Variables
- [ ] ตั้งค่า `CORS_ORIGINS` ให้ตรงกับ domain
- [ ] Database service deploy แล้ว (ถ้าใช้ PostgreSQL)
- [ ] Domain ตั้งค่าแล้ว
- [ ] DNS ชี้มาที่ VPS แล้ว

---

## 🔒 Security Best Practices

1. **เปลี่ยน SECRET_KEY** - อย่าใช้ค่า default
2. **ใช้ HTTPS** - เปิด SSL certificate
3. **ตั้งค่า CORS** - จำกัด origins ที่อนุญาต
4. **ใช้ Strong Database Password** - สำหรับ PostgreSQL
5. **Regular Updates** - อัปเดต dependencies เป็นประจำ
6. **Backup Database** - ตั้งค่าระบบสำรองข้อมูล

---

## 📞 การติดต่อ

หากมีปัญหาหรือคำถาม:
- **GitHub Issues:** https://github.com/prhdev222/med_file_case/issues
- **Email:** uradev222@gmail.com
- **Coolify Docs:** https://coolify.io/docs

---

## 🎉 เสร็จสิ้น!

หลังจาก deploy สำเร็จ คุณจะสามารถเข้าถึงระบบได้ที่:
- **URL:** `https://hospital.yourdomain.com`
- **Admin Login:** `admin` / `admin123` (เปลี่ยนทันที!)

**Happy Deploying! 🚀**

