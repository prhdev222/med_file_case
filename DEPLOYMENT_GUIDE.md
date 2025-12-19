# 🚀 คู่มือการ Deploy ระบบจัดการโรงพยาบาล

คู่มือนี้จะแนะนำวิธีการ deploy ระบบจัดการโรงพยาบาลลงบน web hosting ต่างๆ

## 📋 สารบัญ

1. [เตรียมความพร้อมก่อน Deploy](#เตรียมความพร้อมก่อน-deploy)
2. [Deploy บน Heroku](#deploy-บน-heroku)
3. [Deploy บน Railway](#deploy-บน-railway)
4. [Deploy บน Render](#deploy-บน-render)
5. [Deploy บน DigitalOcean](#deploy-บน-digitalocean)
6. [Deploy บน VPS (Linux)](#deploy-บน-vps-linux)
7. [การตั้งค่า Domain และ SSL](#การตั้งค่า-domain-และ-ssl)
8. [การจัดการ Database](#การจัดการ-database)
9. [การสำรองข้อมูล](#การสำรองข้อมูล)

---

## 📦 เตรียมความพร้อมก่อน Deploy

### 1. ตรวจสอบไฟล์ที่จำเป็น

```bash
# ตรวจสอบว่าไฟล์เหล่านี้มีอยู่
- app.py
- requirements.txt
- frontend/package.json
- .env (หรือ env.example)
- .gitignore
```

### 2. Build Frontend

```bash
# เข้าไปที่โฟลเดอร์ frontend
cd frontend

# ติดตั้ง dependencies
npm install

# Build สำหรับ production
npm run build

# กลับมาที่ root directory
cd ..
```

### 3. ตั้งค่า Environment Variables

สร้างไฟล์ `.env` จาก `env.example`:

```bash
cp env.example .env
```

แก้ไข `.env` สำหรับ production:

```env
# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False

# Security (เปลี่ยนเป็นค่าที่ปลอดภัย!)
SECRET_KEY=your-super-secret-production-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# Database (สำหรับ production ควรใช้ PostgreSQL)
DATABASE_URL=postgresql://user:password@host:port/dbname

# Upload Settings
UPLOAD_FOLDER=storage/uploads
MAX_CONTENT_LENGTH=52428800

# Server Settings
HOST=0.0.0.0
PORT=5000

# CORS (ตั้งค่าให้ตรงกับ domain ของคุณ)
CORS_ORIGINS=https://your-domain.com

# Backup Settings
BACKUP_DIR=storage/backups
BACKUP_INTERVAL_HOURS=24
BACKUP_KEEP_DAYS=30
```

### 4. เพิ่ม Flask-CORS ใน requirements.txt

ตรวจสอบว่า `requirements.txt` มี:

```txt
Flask==3.1.2
Flask-SQLAlchemy==3.1.1
Flask-Login==0.6.3
Flask-CORS==5.0.0
Werkzeug==3.1.3
python-dotenv==1.0.0
gunicorn==21.2.0
psycopg2-binary==2.9.9  # สำหรับ PostgreSQL
```

---

## ☁️ Deploy บน Heroku

### 1. ติดตั้ง Heroku CLI

```bash
# Windows (ใช้ Chocolatey)
choco install heroku-cli

# macOS
brew tap heroku/brew && brew install heroku

# Linux
curl https://cli-assets.heroku.com/install.sh | sh
```

### 2. Login Heroku

```bash
heroku login
```

### 3. สร้าง Heroku App

```bash
# สร้าง app ใหม่
heroku create your-app-name

# หรือใช้ชื่อที่ Heroku สุ่มให้
heroku create
```

### 4. สร้างไฟล์สำหรับ Heroku

**สร้าง `Procfile`:**

```
web: gunicorn app:app
```

**สร้าง `runtime.txt` (ถ้าต้องการ Python version เฉพาะ):**

```
python-3.11.0
```

**อัปเดต `requirements.txt` ให้มี:**

```
gunicorn==21.2.0
psycopg2-binary==2.9.9
```

### 5. ตั้งค่า Environment Variables

```bash
# ตั้งค่า SECRET_KEY
heroku config:set SECRET_KEY=your-secret-key-here

# ตั้งค่า DATABASE_URL (Heroku จะสร้างให้อัตโนมัติ)
heroku addons:create heroku-postgresql:hobby-dev

# ตั้งค่าอื่นๆ
heroku config:set FLASK_ENV=production
heroku config:set FLASK_DEBUG=False
heroku config:set CORS_ORIGINS=https://your-app-name.herokuapp.com
```

### 6. Deploy

```bash
# เพิ่ม remote
git remote add heroku https://git.heroku.com/your-app-name.git

# Push ไปยัง Heroku
git push heroku main

# เปิด app
heroku open
```

### 7. ตรวจสอบ Logs

```bash
heroku logs --tail
```

---

## 🚂 Deploy บน Railway

### 1. สร้าง Account

ไปที่ [railway.app](https://railway.app) และสร้าง account

### 2. สร้าง Project ใหม่

1. คลิก "New Project"
2. เลือก "Deploy from GitHub repo"
3. เลือก repository ของคุณ

### 3. ตั้งค่า Environment Variables

ใน Railway Dashboard:
- ไปที่ Settings → Variables
- เพิ่ม environment variables:
  - `SECRET_KEY`
  - `DATABASE_URL` (Railway จะสร้าง PostgreSQL ให้อัตโนมัติ)
  - `FLASK_ENV=production`
  - `CORS_ORIGINS`

### 4. ตั้งค่า Build Command

ใน Settings → Build:
- Build Command: `pip install -r requirements.txt && cd frontend && npm install && npm run build`
- Start Command: `gunicorn app:app --bind 0.0.0.0:$PORT`

### 5. Deploy

Railway จะ deploy อัตโนมัติเมื่อคุณ push code ไปยัง GitHub

---

## 🎨 Deploy บน Render

### 1. สร้าง Account

ไปที่ [render.com](https://render.com) และสร้าง account

### 2. สร้าง Web Service

1. คลิก "New +" → "Web Service"
2. เชื่อมต่อ GitHub repository
3. ตั้งค่าดังนี้:
   - **Name:** your-app-name
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt && cd frontend && npm install && npm run build`
   - **Start Command:** `gunicorn app:app --bind 0.0.0.0:$PORT`

### 3. ตั้งค่า Environment Variables

ใน Environment:
- `SECRET_KEY`
- `DATABASE_URL` (สร้าง PostgreSQL database แยก)
- `FLASK_ENV=production`
- `CORS_ORIGINS`

### 4. Deploy

Render จะ deploy อัตโนมัติเมื่อคุณ push code

---

## 🌊 Deploy บน DigitalOcean

### 1. สร้าง Droplet

1. ไปที่ [DigitalOcean](https://www.digitalocean.com)
2. สร้าง Droplet ใหม่:
   - **Image:** Ubuntu 22.04
   - **Plan:** Basic ($6/month ขึ้นไป)
   - **Region:** เลือกที่ใกล้ที่สุด

### 2. เชื่อมต่อ SSH

```bash
ssh root@your-droplet-ip
```

### 3. ติดตั้ง Dependencies

```bash
# อัปเดตระบบ
apt update && apt upgrade -y

# ติดตั้ง Python และ pip
apt install python3 python3-pip python3-venv -y

# ติดตั้ง Node.js และ npm
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs

# ติดตั้ง Nginx
apt install nginx -y

# ติดตั้ง PostgreSQL
apt install postgresql postgresql-contrib -y
```

### 4. สร้าง User และ Directory

```bash
# สร้าง user สำหรับ app
adduser --disabled-password --gecos "" appuser

# สร้าง directory สำหรับ app
mkdir -p /var/www/hospital-admin
chown appuser:appuser /var/www/hospital-admin
```

### 5. Clone Repository

```bash
# สลับเป็น appuser
su - appuser

# Clone repository
cd /var/www/hospital-admin
git clone https://github.com/prhdev222/med_file_case.git .

# สร้าง virtual environment
python3 -m venv venv
source venv/bin/activate

# ติดตั้ง dependencies
pip install -r requirements.txt
cd frontend && npm install && npm run build && cd ..
```

### 6. ตั้งค่า Database

```bash
# สลับเป็น postgres user
sudo -u postgres psql

# สร้าง database และ user
CREATE DATABASE hospital_admin;
CREATE USER appuser WITH PASSWORD 'your-password';
GRANT ALL PRIVILEGES ON DATABASE hospital_admin TO appuser;
\q
```

### 7. ตั้งค่า Environment Variables

```bash
# สร้างไฟล์ .env
nano /var/www/hospital-admin/.env
```

เพิ่ม:

```env
FLASK_ENV=production
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://appuser:your-password@localhost/hospital_admin
CORS_ORIGINS=https://your-domain.com
```

### 8. สร้าง Systemd Service

```bash
sudo nano /etc/systemd/system/hospital-admin.service
```

เพิ่ม:

```ini
[Unit]
Description=Hospital Administration System
After=network.target

[Service]
User=appuser
Group=appuser
WorkingDirectory=/var/www/hospital-admin
Environment="PATH=/var/www/hospital-admin/venv/bin"
ExecStart=/var/www/hospital-admin/venv/bin/gunicorn --workers 3 --bind unix:/var/www/hospital-admin/hospital-admin.sock app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

### 9. ตั้งค่า Nginx

```bash
sudo nano /etc/nginx/sites-available/hospital-admin
```

เพิ่ม:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/hospital-admin/hospital-admin.sock;
    }

    location /static {
        alias /var/www/hospital-admin/static;
    }

    location /storage {
        alias /var/www/hospital-admin/storage;
    }
}
```

Enable site:

```bash
sudo ln -s /etc/nginx/sites-available/hospital-admin /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 10. เริ่ม Service

```bash
sudo systemctl start hospital-admin
sudo systemctl enable hospital-admin
sudo systemctl status hospital-admin
```

---

## 🐧 Deploy บน VPS (Linux)

ขั้นตอนคล้ายกับ DigitalOcean แต่ปรับตาม VPS ที่คุณใช้

### สำหรับ VPS อื่นๆ:

1. ติดตั้ง dependencies (Python, Node.js, Nginx, PostgreSQL)
2. Clone repository
3. สร้าง virtual environment
4. ติดตั้ง dependencies
5. ตั้งค่า database
6. ตั้งค่า systemd service
7. ตั้งค่า Nginx
8. ตั้งค่า SSL (Let's Encrypt)

---

## 🔒 การตั้งค่า Domain และ SSL

### ใช้ Let's Encrypt (ฟรี)

```bash
# ติดตั้ง Certbot
apt install certbot python3-certbot-nginx -y

# ขอ SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal (จะตั้งค่าอัตโนมัติ)
```

### อัปเดต Nginx Config

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/hospital-admin/hospital-admin.sock;
    }

    location /static {
        alias /var/www/hospital-admin/static;
    }
}
```

---

## 💾 การจัดการ Database

### สำหรับ Production: ใช้ PostgreSQL

**อัปเดต `requirements.txt`:**

```
psycopg2-binary==2.9.9
```

**อัปเดต `app.py`:**

```python
# เปลี่ยน DATABASE_URL ใน .env
DATABASE_URL=postgresql://user:password@host:port/dbname
```

**Migration:**

```bash
# สร้าง tables
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

---

## 💿 การสำรองข้อมูล

### 1. สำรอง Database

```bash
# PostgreSQL
pg_dump -U appuser hospital_admin > backup_$(date +%Y%m%d).sql

# SQLite (ถ้ายังใช้)
cp instance/hospital.db backup_$(date +%Y%m%d).db
```

### 2. สำรองไฟล์ Uploads

```bash
tar -czf uploads_backup_$(date +%Y%m%d).tar.gz storage/uploads/
```

### 3. สร้าง Script สำรองอัตโนมัติ

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/hospital-admin"

mkdir -p $BACKUP_DIR

# สำรอง database
pg_dump -U appuser hospital_admin > $BACKUP_DIR/db_$DATE.sql

# สำรองไฟล์
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz /var/www/hospital-admin/storage/uploads

# ลบไฟล์เก่า (เก็บไว้ 30 วัน)
find $BACKUP_DIR -type f -mtime +30 -delete
```

เพิ่มใน crontab:

```bash
crontab -e

# สำรองทุกวันเวลา 2:00 น.
0 2 * * * /path/to/backup.sh
```

---

## ✅ Checklist ก่อน Deploy

- [ ] Build frontend สำเร็จ (`npm run build`)
- [ ] ตั้งค่า `.env` สำหรับ production
- [ ] เปลี่ยน `SECRET_KEY` เป็นค่าที่ปลอดภัย
- [ ] ตั้งค่า `DATABASE_URL` (ใช้ PostgreSQL สำหรับ production)
- [ ] ตั้งค่า `CORS_ORIGINS` ให้ตรงกับ domain
- [ ] ตั้งค่า `FLASK_ENV=production`
- [ ] ตั้งค่า `FLASK_DEBUG=False`
- [ ] ทดสอบ local ก่อน deploy
- [ ] ตั้งค่า SSL certificate
- [ ] ตั้งค่าระบบสำรองข้อมูล
- [ ] ตั้งค่า monitoring และ logging

---

## 🆘 Troubleshooting

### ปัญหา: App ไม่ทำงาน

```bash
# ตรวจสอบ logs
journalctl -u hospital-admin -f

# ตรวจสอบ Nginx
sudo nginx -t
sudo systemctl status nginx
```

### ปัญหา: Database Connection Error

```bash
# ตรวจสอบ PostgreSQL
sudo systemctl status postgresql

# ตรวจสอบ connection
psql -U appuser -d hospital_admin
```

### ปัญหา: Permission Denied

```bash
# เปลี่ยน owner
sudo chown -R appuser:appuser /var/www/hospital-admin
```

---

## 📞 การติดต่อ

หากมีปัญหาหรือคำถาม:
- **GitHub Issues:** https://github.com/prhdev222/med_file_case/issues
- **Email:** uradev222@gmail.com

---

**Happy Deploying! 🚀**

