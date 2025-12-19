# 🔐 สรุป Environment Variables สำหรับ Vercel

## 📋 รายการตัวแปรที่ต้องตั้งค่า

### 1. FLASK_ENV
```
Key: FLASK_ENV
Value: production
Environment: Production, Preview, Development (เลือกทั้งหมด)
```

### 2. FLASK_DEBUG
```
Key: FLASK_DEBUG
Value: False
Environment: Production, Preview, Development (เลือกทั้งหมด)
```

### 3. SECRET_KEY
```
Key: SECRET_KEY
Value: aeab9e70eebe445d4f1bb7e2d8e0278f737947f2970faba8f83c2674f1d86af4
Environment: Production, Preview, Development (เลือกทั้งหมด)
```

**หมายเหตุ:** ใช้ค่าที่สร้างให้แล้ว หรือสร้างใหม่ด้วย:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 4. DATABASE_URL
```
Key: DATABASE_URL
Value: postgresql://postgres:[PASSWORD]@[SUPABASE-HOST]:5432/postgres
Environment: Production, Preview, Development (เลือกทั้งหมด)
```

**ตัวอย่าง:**
```
postgresql://postgres:mypassword123@supabase-abc123.coolify.local:5432/postgres
```

**วิธีได้ค่า:**
1. ไปที่ Coolify → Supabase service
2. คัดลอก Connection String
3. แทนที่ `[PASSWORD]` และ `[SUPABASE-HOST]` ด้วยค่าจริง

### 5. CORS_ORIGINS
```
Key: CORS_ORIGINS
Value: https://medfiles.vercel.app
Environment: Production, Preview, Development (เลือกทั้งหมด)
```

### 6. VERCEL
```
Key: VERCEL
Value: 1
Environment: Production, Preview, Development (เลือกทั้งหมด)
```

---

## 📝 Copy-Paste Ready (สำหรับ Vercel Dashboard)

### วิธีที่ 1: ตั้งค่าทีละตัว

ไปที่: https://vercel.com/prhdev222s-projects/medfiles/settings/environment-variables

เพิ่มทีละตัวตามรายการด้านบน

### วิธีที่ 2: ใช้ Vercel CLI

```bash
# FLASK_ENV
vercel env add FLASK_ENV production

# FLASK_DEBUG
vercel env add FLASK_DEBUG False

# SECRET_KEY
vercel env add SECRET_KEY aeab9e70eebe445d4f1bb7e2d8e0278f737947f2970faba8f83c2674f1d86af4

# DATABASE_URL (ต้องใส่ค่าจริง)
vercel env add DATABASE_URL "postgresql://postgres:password@host:5432/postgres"

# CORS_ORIGINS
vercel env add CORS_ORIGINS "https://medfiles.vercel.app"

# VERCEL
vercel env add VERCEL 1
```

---

## ✅ Checklist

- [ ] FLASK_ENV = `production`
- [ ] FLASK_DEBUG = `False`
- [ ] SECRET_KEY = `<ตั้งค่าแล้ว>`
- [ ] DATABASE_URL = `<จาก Supabase Coolify>`
- [ ] CORS_ORIGINS = `https://medfiles.vercel.app`
- [ ] VERCEL = `1`
- [ ] Redeploy แล้ว (`vercel --prod`)

---

## 🔗 Links

- **Vercel Dashboard:** https://vercel.com/prhdev222s-projects/medfiles/settings/environment-variables
- **Production URL:** https://medfiles.vercel.app
- **Inspect:** https://vercel.com/prhdev222s-projects/medfiles

---

**หลังจากตั้งค่าแล้ว อย่าลืม redeploy!** 🚀


