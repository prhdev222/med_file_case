# 🚀 Quick Start Guide - Deploy ระบบจัดการโรงพยาบาล

คู่มือเริ่มต้นเร็วสำหรับการ deploy ระบบ

## 📋 ตัวเลือกการ Deploy

### 1️⃣ Heroku (ง่ายที่สุด - แนะนำสำหรับเริ่มต้น)

**ข้อดี:**
- ง่ายและเร็ว
- มี PostgreSQL ให้อัตโนมัติ
- ฟรี tier สำหรับทดสอบ

**ขั้นตอน:**

```bash
# 1. ติดตั้ง Heroku CLI
# Windows: choco install heroku-cli
# macOS: brew install heroku
# Linux: curl https://cli-assets.heroku.com/install.sh | sh

# 2. Login
heroku login

# 3. สร้าง app
heroku create your-app-name

# 4. เพิ่ม PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# 5. ตั้งค่า Environment Variables
heroku config:set SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
heroku config:set FLASK_ENV=production
heroku config:set CORS_ORIGINS=https://your-app-name.herokuapp.com

# 6. Deploy
git push heroku main

# 7. เปิด app
heroku open
```

**ไฟล์ที่ต้องมี:**
- ✅ `Procfile` (มีอยู่แล้ว)
- ✅ `requirements.txt` (อัปเดตแล้ว)
- ✅ `runtime.txt` (มีอยู่แล้ว)

---

### 2️⃣ Railway (แนะนำ - ใช้งานง่าย)

**ข้อดี:**
- ง่ายกว่า Heroku
- มี PostgreSQL ให้อัตโนมัติ
- ราคาถูก

**ขั้นตอน:**

1. ไปที่ [railway.app](https://railway.app)
2. สร้าง account และเชื่อมต่อ GitHub
3. สร้าง Project ใหม่ → Deploy from GitHub
4. เลือก repository ของคุณ
5. ตั้งค่า Environment Variables:
   - `SECRET_KEY` (สร้างด้วย: `python -c 'import secrets; print(secrets.token_hex(32))'`)
   - `FLASK_ENV=production`
   - `CORS_ORIGINS` (URL ของ Railway app)
6. Railway จะ deploy อัตโนมัติ!

**Build Command:**
```
pip install -r requirements.txt && cd frontend && npm install && npm run build
```

**Start Command:**
```
gunicorn app:app --bind 0.0.0.0:$PORT
```

---

### 3️⃣ Render (แนะนำ - ฟรี tier ดี)

**ข้อดี:**
- ฟรี tier ดี
- มี PostgreSQL ให้
- Auto-deploy จาก GitHub

**ขั้นตอน:**

1. ไปที่ [render.com](https://render.com)
2. สร้าง account และเชื่อมต่อ GitHub
3. New → Web Service
4. เลือก repository
5. ตั้งค่า:
   - **Name:** your-app-name
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt && cd frontend && npm install && npm run build`
   - **Start Command:** `gunicorn app:app --bind 0.0.0.0:$PORT`
6. ตั้งค่า Environment Variables (เหมือน Railway)
7. Deploy!

---

### 4️⃣ DigitalOcean / VPS (สำหรับ Production จริง)

**ข้อดี:**
- ควบคุมได้เต็มที่
- ราคาถูก ($6/เดือน)
- เหมาะสำหรับ production

**ขั้นตอนย่อ:**

```bash
# 1. สร้าง Droplet (Ubuntu 22.04)

# 2. SSH เข้าไป
ssh root@your-droplet-ip

# 3. ติดตั้ง dependencies
apt update && apt upgrade -y
apt install python3 python3-pip python3-venv nodejs npm nginx postgresql -y

# 4. Clone repository
cd /var/www
git clone https://github.com/prhdev222/med_file_case.git hospital-admin
cd hospital-admin

# 5. สร้าง virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 6. Build frontend
cd frontend
npm install
npm run build
cd ..

# 7. ตั้งค่า database
sudo -u postgres psql
CREATE DATABASE hospital_admin;
CREATE USER appuser WITH PASSWORD 'your-password';
GRANT ALL PRIVILEGES ON DATABASE hospital_admin TO appuser;
\q

# 8. ตั้งค่า .env
nano .env
# เพิ่ม DATABASE_URL=postgresql://appuser:your-password@localhost/hospital_admin

# 9. ตั้งค่า systemd service
sudo cp systemd.service.example /etc/systemd/system/hospital-admin.service
sudo nano /etc/systemd/system/hospital-admin.service
# แก้ไข paths

# 10. ตั้งค่า Nginx
sudo cp nginx.conf.example /etc/nginx/sites-available/hospital-admin
sudo nano /etc/nginx/sites-available/hospital-admin
# แก้ไข domain และ paths
sudo ln -s /etc/nginx/sites-available/hospital-admin /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# 11. เริ่ม service
sudo systemctl start hospital-admin
sudo systemctl enable hospital-admin

# 12. ตั้งค่า SSL (Let's Encrypt)
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

---

## ⚙️ เตรียมความพร้อมก่อน Deploy

### 1. Build Frontend

```bash
cd frontend
npm install
npm run build
cd ..
```

### 2. ตั้งค่า Environment Variables

สร้างไฟล์ `.env`:

```env
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:password@host:port/dbname
CORS_ORIGINS=https://your-domain.com
```

### 3. สร้าง Secret Key

```bash
# Python
python -c 'import secrets; print(secrets.token_hex(32))'

# หรือใช้ online generator
```

---

## ✅ Checklist ก่อน Deploy

- [ ] Build frontend สำเร็จ (`npm run build`)
- [ ] ตั้งค่า `.env` สำหรับ production
- [ ] เปลี่ยน `SECRET_KEY` เป็นค่าที่ปลอดภัย
- [ ] ตั้งค่า `DATABASE_URL` (ใช้ PostgreSQL)
- [ ] ตั้งค่า `CORS_ORIGINS`
- [ ] ทดสอบ local ก่อน deploy

---

## 🆘 ปัญหาที่พบบ่อย

### Frontend ไม่แสดงผล

**แก้ไข:**
- ตรวจสอบว่า build frontend แล้ว (`npm run build`)
- ตรวจสอบ path ของ static files

### Database Connection Error

**แก้ไข:**
- ตรวจสอบ `DATABASE_URL` ใน environment variables
- ตรวจสอบว่า PostgreSQL service ทำงานอยู่

### CORS Error

**แก้ไข:**
- ตั้งค่า `CORS_ORIGINS` ให้ตรงกับ domain ของคุณ
- ตรวจสอบว่า Flask-CORS ติดตั้งแล้ว

---

## 📚 เอกสารเพิ่มเติม

ดูคู่มือฉบับเต็มที่: [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)

---

**Happy Deploying! 🚀**


