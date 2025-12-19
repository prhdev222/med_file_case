# 🚀 คู่มือ Redeploy บน Vercel

## 📋 วิธีที่ 1: ผ่าน GitHub (อัตโนมัติ)

### ขั้นตอน:

1. **Commit และ Push ไปยัง GitHub:**
   ```bash
   git add .
   git commit -m "Fix Vercel deployment"
   git push origin main
   ```

2. **Vercel จะ Deploy อัตโนมัติ:**
   - Vercel จะ detect การ push ไปยัง GitHub
   - จะ build และ deploy อัตโนมัติ
   - ใช้เวลา 2-5 นาที

3. **ตรวจสอบ Status:**
   - ไปที่ Vercel Dashboard
   - ดู Deployments tab
   - รอให้ build เสร็จ

---

## 📋 วิธีที่ 2: ผ่าน Vercel CLI (แนะนำ)

### ติดตั้ง Vercel CLI:

```bash
# ติดตั้ง Vercel CLI (ถ้ายังไม่มี)
npm install -g vercel

# หรือใช้ npx (ไม่ต้องติดตั้ง)
npx vercel
```

### Login:

```bash
vercel login
```

### Deploy:

```bash
# Deploy to preview
vercel

# Deploy to production
vercel --prod
```

### Redeploy Deployment ที่มีอยู่:

```bash
# ดู deployments
vercel ls

# Redeploy deployment ล่าสุด
vercel --prod --force
```

---

## 📋 วิธีที่ 3: ผ่าน Vercel Dashboard

### ขั้นตอน:

1. **ไปที่ Vercel Dashboard:**
   - https://vercel.com/prhdev222s-projects/medfiles

2. **ไปที่ Deployments:**
   - คลิก **Deployments** tab

3. **Redeploy:**
   - คลิก **"..."** (three dots) ที่ deployment ล่าสุด
   - เลือก **"Redeploy"**
   - เลือก:
     - **"Use existing Build Cache"** (เร็วกว่า)
     - หรือ **"Rebuild"** (clean build)

---

## 🔧 ตรวจสอบ Deployment

### 1. ดู Logs:

```bash
# ดู logs จาก Vercel CLI
vercel logs

# หรือดูใน Dashboard
# Vercel Dashboard → Deployments → คลิก deployment → Logs tab
```

### 2. ทดสอบ Health Check:

```bash
curl https://medfiles.vercel.app/health
```

**ควรได้:**
```json
{
  "status": "healthy",
  "database": "connected"
}
```

### 3. ตรวจสอบ Environment Variables:

```bash
# ดู environment variables
vercel env ls
```

---

## ⚙️ Vercel CLI Commands ที่มีประโยชน์

### ดู Project Info:

```bash
vercel inspect
```

### ดู Environment Variables:

```bash
vercel env ls
```

### เพิ่ม Environment Variable:

```bash
vercel env add DATABASE_URL production
# จะถามให้ใส่ value
```

### ดู Logs:

```bash
vercel logs
```

### Remove Deployment:

```bash
vercel remove [deployment-url]
```

---

## 🐛 Troubleshooting

### ปัญหา: Build Failed

**Error:**
```
Build failed
```

**แก้ไข:**
1. ดู logs ใน Vercel Dashboard
2. ตรวจสอบ `requirements.txt` มี dependencies ทั้งหมด
3. ตรวจสอบ Python version (ต้องเป็น 3.11)
4. ตรวจสอบ `vercel.json` configuration

### ปัญหา: Function Timeout

**Error:**
```
Function execution exceeded timeout
```

**แก้ไข:**
1. เพิ่ม `maxDuration` ใน `vercel.json`:
   ```json
   {
     "functions": {
       "app.py": {
         "maxDuration": 30
       }
     }
   }
   ```

### ปัญหา: Environment Variables ไม่ทำงาน

**Error:**
```
Environment variable not found
```

**แก้ไข:**
1. ตรวจสอบ Environment Variables ใน Vercel Dashboard
2. ตรวจสอบว่าเลือก Environment ถูกต้อง (Production, Preview)
3. Redeploy หลังจากตั้งค่า Environment Variables

---

## 📝 Checklist

- [ ] Code ถูก commit และ push ไปยัง GitHub แล้ว
- [ ] Environment Variables ตั้งค่าแล้ว
- [ ] `DATABASE_URL` ถูกต้องและมี password จริง
- [ ] Database tables สร้างแล้ว
- [ ] Deploy สำเร็จแล้ว
- [ ] Health check ผ่านแล้ว
- [ ] หน้าแรกแสดงได้แล้ว

---

## 🔗 Links ที่เกี่ยวข้อง

- **Vercel Dashboard:** https://vercel.com/prhdev222s-projects/medfiles
- **Vercel CLI Docs:** https://vercel.com/docs/cli
- **GitHub Repository:** https://github.com/prhdev222/med_file_case

---

**Happy Deploying! 🚀**


