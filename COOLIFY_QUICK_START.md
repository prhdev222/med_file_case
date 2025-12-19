# 🚀 Coolify Quick Start - Deploy ใน 5 นาที!

## ✅ สิ่งที่ต้องมี

- ✅ Coolify VPS ที่ติดตั้งแล้ว
- ✅ GitHub repository: `prhdev222/med_file_case`
- ✅ Domain name (optional แต่แนะนำ)

---

## 🎯 ขั้นตอนการ Deploy

### 1. เข้า Coolify Dashboard

เปิดเว็บเบราว์เซอร์ไปที่ Coolify ของคุณ (เช่น `https://coolify.yourdomain.com`)

### 2. สร้าง Application ใหม่

1. คลิก **"New Resource"** → **"Application"**
2. เลือก **"Git Repository"**
3. เชื่อมต่อ GitHub และเลือก repository: `med_file_case`
4. เลือก branch: `main`

### 3. ตั้งค่า Build

- **Build Pack:** `Dockerfile` (Coolify จะ detect อัตโนมัติ)
- **Port:** `5000`

### 4. ตั้งค่า Database

**ถ้ามี Supabase อยู่แล้ว (แนะนำ):**
1. ไปที่ Supabase service ใน Coolify
2. คัดลอก Connection String
3. ใช้ใน `DATABASE_URL` (ดูขั้นตอนที่ 5)

**หรือสร้าง PostgreSQL ใหม่:**
1. **New Resource** → **"Database"** → **"PostgreSQL"**
2. ตั้งค่า:
   - Name: `hospital-admin-db`
   - Database: `hospital_admin`
   - Username: `hospital_user`
   - Password: (ตั้งรหัสผ่านที่ปลอดภัย)

### 5. ตั้งค่า Environment Variables

ใน Application → **Environment Variables** → เพิ่ม:

```env
FLASK_ENV=production
SECRET_KEY=<สร้างด้วย: python -c 'import secrets; print(secrets.token_hex(32))'>
# ถ้าใช้ Supabase:
DATABASE_URL=postgresql://postgres:your-password@supabase-host:5432/postgres
# หรือถ้าใช้ PostgreSQL จาก Coolify:
DATABASE_URL=postgresql://hospital_user:your-password@hospital-admin-db:5432/hospital_admin
CORS_ORIGINS=https://your-domain.com
PORT=5000
```

### 6. เพิ่ม Domain (Optional)

1. **Domains** → เพิ่ม domain ของคุณ
2. Enable **SSL** (Coolify จะขอ Let's Encrypt อัตโนมัติ)
3. ตั้งค่า DNS ชี้มาที่ VPS IP

### 7. Deploy!

คลิก **"Deploy"** และรอให้ build เสร็จ (ประมาณ 3-5 นาที)

---

## ✅ ตรวจสอบ

หลังจาก deploy สำเร็จ:

1. เปิด URL: `https://your-domain.com` หรือ `http://your-vps-ip:5000`
2. Health check: `https://your-domain.com/health`
3. Login: `admin` / `admin123` (เปลี่ยนทันที!)

---

## 🔧 Troubleshooting

### Build Failed?
- ตรวจสอบ Build Logs ใน Coolify
- ตรวจสอบว่า `Dockerfile` มีอยู่

### Database Error?
- ตรวจสอบ `DATABASE_URL` format
- ตรวจสอบว่า Database service deploy แล้ว

### SSL ไม่ทำงาน?
- ตรวจสอบ DNS ชี้มาที่ VPS แล้ว
- รอให้ DNS propagate (5-30 นาที)

---

## 📚 ดูคู่มือฉบับเต็ม

- **คู่มือทั่วไป:** [COOLIFY_DEPLOY.md](./COOLIFY_DEPLOY.md)
- **คู่มือ Supabase:** [COOLIFY_SUPABASE_SETUP.md](./COOLIFY_SUPABASE_SETUP.md) ⭐ (ถ้ามี Supabase)

---

**Happy Deploying! 🎉**

