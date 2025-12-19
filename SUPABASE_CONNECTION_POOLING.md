# 🔗 Supabase Connection Pooling - ไม่ต้องตั้งค่าเพิ่มเติม!

## ✅ คำตอบสั้นๆ

**ไม่ต้องตั้งค่าเพิ่มเติมใน Supabase website!**

Connection Pooling เป็น feature ที่ Supabase มีให้อยู่แล้วโดยอัตโนมัติ แค่ใช้ Connection String ที่ถูกต้องเท่านั้น

---

## 🔍 Connection Pooling คืออะไร?

Connection Pooling คือการจัดการ database connections อัตโนมัติ เหมาะกับ:
- ✅ **Serverless functions** (Vercel, Netlify)
- ✅ **Short-lived connections**
- ✅ **High concurrency**

---

## 📋 วิธีใช้ Connection Pooling

### ขั้นตอนที่ 1: หา Connection String จาก Supabase Dashboard

1. **ไปที่ Supabase Dashboard:**
   - https://supabase.com/dashboard/project/vmfmoseeunnfwjzunnss

2. **ไปที่ Settings → Database:**
   - คลิก **Settings** (ไอคอนฟันเฟือง)
   - คลิก **Database**

3. **ดู Connection String:**
   - ไปที่ **Connection string** tab
   - เลือก **Connection pooling** (ไม่ใช่ Direct connection)
   - เลือก **URI** format
   - คัดลอก Connection String

   **รูปแบบที่เห็น:**
   ```
   postgresql://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
   ```

   หรือ:
   ```
   postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:6543/postgres?pgbouncer=true
   ```

### ขั้นตอนที่ 2: ใช้ Connection String ใน Vercel

1. **ไปที่ Vercel Dashboard:**
   - https://vercel.com/prhdev222s-projects/medfiles/settings/environment-variables

2. **ตั้งค่า DATABASE_URL:**
   - Key: `DATABASE_URL`
   - Value: Connection String ที่คัดลอกมา (port 6543)
   - Environment: Production, Preview, Development

3. **ตรวจสอบ:**
   - ใช้ port `6543` (Connection Pooling)
   - มี `?pgbouncer=true` parameter (ถ้ามี)
   - แทนที่ `[PASSWORD]` ด้วย password จริง

---

## 🔍 ตัวอย่าง Connection String

### Connection Pooling (แนะนำสำหรับ Vercel):

```
postgresql://postgres:[PASSWORD]@db.vmfmoseeunnfwjzunnss.supabase.co:6543/postgres?pgbouncer=true
```

### Direct Connection (ไม่แนะนำสำหรับ Vercel):

```
postgresql://postgres:[PASSWORD]@db.vmfmoseeunnfwjzunnss.supabase.co:5432/postgres
```

**ความแตกต่าง:**
- Port `6543` = Connection Pooling (เหมาะกับ serverless)
- Port `5432` = Direct Connection (เหมาะกับ long-lived connections)

---

## ⚙️ Connection Pooling Modes

Supabase มี 3 modes:

### 1. Transaction Mode (แนะนำ)
```
postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:6543/postgres?pgbouncer=true&pooler_mode=transaction
```

### 2. Session Mode
```
postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:6543/postgres?pgbouncer=true&pooler_mode=session
```

### 3. Default (Transaction Mode)
```
postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:6543/postgres?pgbouncer=true
```

**สำหรับ Vercel:** ใช้ Default หรือ Transaction Mode ก็ได้

---

## 🆚 เปรียบเทียบ

| Feature | Direct (5432) | Pooling (6543) |
|---------|---------------|----------------|
| **เหมาะกับ** | Long-lived connections | Serverless, Short-lived |
| **Connection Limit** | 1 connection per client | Shared pool |
| **Performance** | ดีสำหรับ persistent | ดีสำหรับ concurrent |
| **Vercel** | ❌ ไม่แนะนำ | ✅ แนะนำ |

---

## ✅ Checklist

- [ ] ไปที่ Supabase Dashboard → Settings → Database
- [ ] ดู Connection String → Connection pooling
- [ ] คัดลอก Connection String (port 6543)
- [ ] ตั้งค่าใน Vercel → Environment Variables
- [ ] แทนที่ `[PASSWORD]` ด้วย password จริง
- [ ] Redeploy Vercel

---

## 🔧 Troubleshooting

### ปัญหา: Connection Timeout

**สาเหตุ:** ใช้ port 5432 แทน 6543

**แก้ไข:**
- เปลี่ยนเป็น port 6543
- เพิ่ม `?pgbouncer=true` parameter

### ปัญหา: Too Many Connections

**สาเหตุ:** ใช้ Direct Connection (port 5432)

**แก้ไข:**
- เปลี่ยนเป็น Connection Pooling (port 6543)
- Supabase จะจัดการ connections อัตโนมัติ

### ปัญหา: Connection String ไม่มี port 6543

**แก้ไข:**
1. ไปที่ Supabase Dashboard → Settings → Database
2. ดู **Connection string** tab
3. เลือก **Connection pooling** (ไม่ใช่ Direct connection)
4. คัดลอก Connection String ที่มี port 6543

---

## 📝 สรุป

1. **ไม่ต้องตั้งค่าเพิ่มเติม** - Connection Pooling มีอยู่แล้วใน Supabase
2. **แค่ใช้ Connection String ที่ถูกต้อง** - port 6543
3. **หาได้จาก Supabase Dashboard** - Settings → Database → Connection string → Connection pooling
4. **ตั้งค่าใน Vercel** - Environment Variables → DATABASE_URL

---

## 🔗 Links ที่เกี่ยวข้อง

- **Supabase Dashboard:** https://supabase.com/dashboard/project/vmfmoseeunnfwjzunnss
- **Supabase Connection Pooling Docs:** https://supabase.com/docs/guides/database/connecting-to-postgres#connection-pooler
- **Vercel Environment Variables:** https://vercel.com/prhdev222s-projects/medfiles/settings/environment-variables

---

**Happy Connecting! 🔗**


