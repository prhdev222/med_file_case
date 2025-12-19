# 🔐 ตั้งค่า Environment Variables ใน Vercel

คู่มือการตั้งค่า Environment Variables สำหรับ medfiles.vercel.app

## 📋 ตัวแปรที่ต้องตั้งค่า

### 1. ไปที่ Vercel Dashboard

URL: https://vercel.com/prhdev222s-projects/medfiles/settings/environment-variables

### 2. เพิ่มตัวแปรเหล่านี้:

#### FLASK_ENV
```
production
```
**Environment:** Production, Preview, Development (เลือกทั้งหมด)

#### FLASK_DEBUG
```
False
```
**Environment:** Production, Preview, Development (เลือกทั้งหมด)

#### SECRET_KEY
```
aeab9e70eebe445d4f1bb7e2d8e0278f737947f2970faba8f83c2674f1d86af4
```
**Environment:** Production, Preview, Development (เลือกทั้งหมด)

**หมายเหตุ:** ใช้ค่าที่สร้างให้แล้ว หรือสร้างใหม่ด้วย:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

#### DATABASE_URL
```
postgresql://postgres:[PASSWORD]@[SUPABASE-HOST]:5432/postgres
```
**Environment:** Production, Preview, Development (เลือกทั้งหมด)

**ตัวอย่าง:**
```
postgresql://postgres:mypassword@supabase-abc123.coolify.local:5432/postgres
```

**วิธีได้ Connection String:**
1. ไปที่ Coolify → Supabase service
2. คัดลอก Connection String
3. ใช้ใน `DATABASE_URL`

#### CORS_ORIGINS
```
https://medfiles.vercel.app
```
**Environment:** Production, Preview, Development (เลือกทั้งหมด)

#### VERCEL
```
1
```
**Environment:** Production, Preview, Development (เลือกทั้งหมด)

---

## 🚀 หลังจากตั้งค่าแล้ว

### Redeploy เพื่อใช้ Environment Variables ใหม่:

```bash
vercel --prod
```

หรือใน Vercel Dashboard:
1. ไปที่ **Deployments**
2. คลิก **"..."** → **"Redeploy"**
3. เลือก **"Use existing Build Cache"** หรือ **"Rebuild"**

---

## ✅ ตรวจสอบ

### 1. ตรวจสอบ Environment Variables

```bash
vercel env ls
```

### 2. ทดสอบ Health Check

```bash
curl https://medfiles.vercel.app/health
```

ควรได้:
```json
{
  "status": "healthy",
  "database": "connected"
}
```

### 3. ทดสอบหน้าแรก

เปิด: https://medfiles.vercel.app

---

## 🆘 Troubleshooting

### ปัญหา: Database Connection Error

**Error:** `could not connect to server`

**แก้ไข:**
1. ตรวจสอบ `DATABASE_URL` format ถูกต้อง
2. ตรวจสอบ Supabase firewall เปิดแล้ว
3. ตรวจสอบ Supabase service ทำงานอยู่

### ปัญหา: CORS Error

**Error:** `CORS policy: No 'Access-Control-Allow-Origin'`

**แก้ไข:**
1. ตรวจสอบ `CORS_ORIGINS` ตั้งค่าแล้ว
2. ตรวจสอบว่า URL ตรงกับ domain ที่ใช้
3. Redeploy หลังจากตั้งค่า

---

## 📝 Checklist

- [ ] FLASK_ENV=production
- [ ] FLASK_DEBUG=False
- [ ] SECRET_KEY (ตั้งค่าแล้ว)
- [ ] DATABASE_URL (จาก Supabase)
- [ ] CORS_ORIGINS=https://medfiles.vercel.app
- [ ] VERCEL=1
- [ ] Redeploy แล้ว
- [ ] Health check ผ่านแล้ว
- [ ] หน้าแรกแสดงได้แล้ว

---

**Happy Deploying! 🚀**


