# 🔗 วิธีหา Connection String จาก Supabase Dashboard

## 📋 จากภาพที่เห็น

คุณอยู่ที่หน้า **Database Settings** ซึ่งมี:
- ✅ Database password (ใช้สร้าง Connection String)
- ✅ Connection pooling configuration (ไม่ต้องเปลี่ยนค่า)

**แต่ Connection String อยู่ที่หน้าอื่น!**

---

## 🔍 วิธีหา Connection String

### ขั้นตอนที่ 1: ไปที่ Connection String Page

1. **ใน Supabase Dashboard** (ที่คุณอยู่ตอนนี้)
2. ดู sidebar ซ้าย → **"Connect"** button (ด้านบน)
3. หรือไปที่: **Settings** → **Database** → **Connection string** tab

### ขั้นตอนที่ 2: เลือก Connection Pooling

1. ในหน้า Connection string:
   - เลือก **"Connection pooling"** (ไม่ใช่ Direct connection)
   - เลือก **"URI"** format
   - คัดลอก Connection String

2. **Connection String ที่ได้:**
   ```
   postgresql://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
   ```
   
   หรือ:
   ```
   postgresql://postgres:[PASSWORD]@db.vmfmoseeunnfwjzunnss.supabase.co:6543/postgres?pgbouncer=true
   ```

---

## 📝 สร้าง Connection String เอง (ถ้าไม่มี)

### จากข้อมูลในภาพ:

1. **Database Password:**
   - ดูจากหน้า Settings → Database password
   - หรือคลิก "Reset database password" ถ้าไม่รู้

2. **Project Reference:**
   - จาก URL: `vmfmoseeunnfwjzunnss`

3. **สร้าง Connection String:**
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.vmfmoseeunnfwjzunnss.supabase.co:6543/postgres?pgbouncer=true
   ```
   
   แทนที่ `[YOUR-PASSWORD]` ด้วย password จากหน้า Settings

---

## ⚙️ Connection Pooling Configuration (ไม่ต้องเปลี่ยน)

จากภาพที่เห็น:
- **Pool Size:** 15 (default สำหรับ Nano plan) - **ไม่ต้องเปลี่ยน**
- **Max Client Connections:** 200 (fixed) - **ไม่สามารถเปลี่ยนได้**

**สรุป:** ใช้ค่า default ได้เลย ไม่ต้องตั้งค่าเพิ่มเติม!

---

## 🚀 ตั้งค่าใน Vercel

### ขั้นตอนที่ 1: ไปที่ Vercel Dashboard

https://vercel.com/prhdev222s-projects/medfiles/settings/environment-variables

### ขั้นตอนที่ 2: เพิ่ม DATABASE_URL

**Key:** `DATABASE_URL`

**Value:**
```
postgresql://postgres:[YOUR-PASSWORD]@db.vmfmoseeunnfwjzunnss.supabase.co:6543/postgres?pgbouncer=true
```

**Environment:**
- ✅ Production
- ✅ Preview
- ✅ Development (optional)

**สำคัญ:** แทนที่ `[YOUR-PASSWORD]` ด้วย password จริงจาก Supabase Settings

### ขั้นตอนที่ 3: Redeploy

```bash
vercel --prod --force
```

---

## ✅ Checklist

- [ ] หา Database Password จาก Supabase Settings
- [ ] ไปที่ Connection string page (ไม่ใช่ Settings)
- [ ] คัดลอก Connection String (port 6543) หรือสร้างเอง
- [ ] ตั้งค่าใน Vercel → Environment Variables
- [ ] แทนที่ `[YOUR-PASSWORD]` ด้วย password จริง
- [ ] Redeploy Vercel

---

## 🔗 Links

- **Supabase Dashboard:** https://supabase.com/dashboard/project/vmfmoseeunnfwjzunnss
- **Connection String Page:** https://supabase.com/dashboard/project/vmfmoseeunnfwjzunnss/settings/database (คลิก "Connection string" tab)
- **Vercel Environment Variables:** https://vercel.com/prhdev222s-projects/medfiles/settings/environment-variables

---

**สรุป:** Connection Pooling configuration ที่เห็นในภาพ - **ไม่ต้องเปลี่ยนค่า** แค่หา Connection String และใช้ใน Vercel!


