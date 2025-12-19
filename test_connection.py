#!/usr/bin/env python3
"""
ทดสอบ Connection String จาก Supabase
"""

import psycopg2
import sys
from urllib.parse import quote_plus

def test_connection(database_url):
    """ทดสอบ database connection"""
    print("=" * 60)
    print("🧪 ทดสอบ Connection String")
    print("=" * 60)
    
    # Mask password for display
    if '@' in database_url:
        display_url = database_url.split('@')[1]
        print(f"📋 Testing connection to: {display_url}")
    else:
        print(f"📋 Testing connection...")
    
    try:
        # Test connection
        print("\n⏳ กำลังเชื่อมต่อ...")
        
        # psycopg2 doesn't support query parameters in URI, so we need to parse it
        # Remove query parameters for connection test (pgbouncer=true is just metadata)
        if '?' in database_url:
            base_url = database_url.split('?')[0]
            print(f"ℹ️  Removing query parameters for connection test...")
        else:
            base_url = database_url
        
        conn = psycopg2.connect(base_url)
        print("✅ Connection successful!")
        
        # Test query
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()
        print(f"\n📊 PostgreSQL version:")
        print(f"   {version[0]}")
        
        # Test if tables exist
        print("\n📋 ตรวจสอบ Tables:")
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cur.fetchall()
        
        if tables:
            print(f"   ✅ พบ {len(tables)} tables:")
            for table in tables:
                print(f"      - {table[0]}")
        else:
            print("   ⚠️  ไม่พบ tables (อาจจะยังไม่ได้สร้าง)")
            print("   💡 ใช้ supabase_schema.sql เพื่อสร้าง tables")
        
        # Test specific tables
        required_tables = ['admin_user', 'department', 'patient_case']
        print("\n🔍 ตรวจสอบ Required Tables:")
        for table_name in required_tables:
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = %s
                );
            """, (table_name,))
            exists = cur.fetchone()[0]
            if exists:
                print(f"   ✅ {table_name} - มีอยู่")
            else:
                print(f"   ❌ {table_name} - ไม่พบ")
        
        cur.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print("✅ ทดสอบสำเร็จ! Connection String ใช้ได้")
        print("=" * 60)
        return True
        
    except psycopg2.OperationalError as e:
        print(f"\n❌ Connection failed: {e}")
        print("\n🔍 ตรวจสอบ:")
        print("   1. DATABASE_URL format ถูกต้องหรือไม่")
        print("   2. Password ถูกต้องหรือไม่")
        print("   3. Host สามารถเข้าถึงได้หรือไม่")
        print("   4. Port ถูกต้องหรือไม่ (6543 สำหรับ Connection Pooling)")
        return False
    except psycopg2.Error as e:
        print(f"\n❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("\n" + "=" * 60)
    print("🔗 Supabase Connection String Tester")
    print("=" * 60)
    
    # วิธีที่ 1: ใช้จาก environment variable
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    database_url = os.getenv('DATABASE_URL')
    
    if database_url:
        print("\n📋 ใช้ DATABASE_URL จาก environment variable")
        success = test_connection(database_url)
    else:
        print("\n⚠️  ไม่พบ DATABASE_URL ใน environment variable")
        print("\n📝 วิธีใช้:")
        print("   1. สร้าง Connection String:")
        print("      postgresql://postgres:[PASSWORD]@db.vmfmoseeunnfwjzunnss.supabase.co:6543/postgres?pgbouncer=true")
        print("\n   2. ตั้งค่าใน .env file:")
        print("      DATABASE_URL=postgresql://postgres:[PASSWORD]@db.vmfmoseeunnfwjzunnss.supabase.co:6543/postgres?pgbouncer=true")
        print("\n   3. หรือรัน script พร้อม Connection String:")
        print("      python test_connection.py 'postgresql://postgres:[PASSWORD]@db.vmfmoseeunnfwjzunnss.supabase.co:6543/postgres?pgbouncer=true'")
        
        # วิธีที่ 2: ใช้จาก command line argument
        if len(sys.argv) > 1:
            database_url = sys.argv[1]
            print(f"\n📋 ใช้ Connection String จาก command line")
            success = test_connection(database_url)
        else:
            # วิธีที่ 3: ใส่ Connection String ตรงๆ
            print("\n" + "=" * 60)
            print("💡 ใส่ Connection String ตรงๆ:")
            print("=" * 60)
            print("\nรูปแบบ:")
            print("postgresql://postgres:[PASSWORD]@db.vmfmoseeunnfwjzunnss.supabase.co:6543/postgres?pgbouncer=true")
            print("\nตัวอย่าง:")
            print("postgresql://postgres:mypassword123@db.vmfmoseeunnfwjzunnss.supabase.co:6543/postgres?pgbouncer=true")
            
            connection_string = input("\n🔗 ใส่ Connection String (หรือกด Enter เพื่อออก): ").strip()
            
            if connection_string:
                success = test_connection(connection_string)
            else:
                print("\n❌ ไม่ได้ใส่ Connection String")
                sys.exit(1)
    
    if success:
        print("\n✅ Connection String ใช้ได้! สามารถใช้ใน Vercel ได้เลย")
        sys.exit(0)
    else:
        print("\n❌ Connection String ไม่สามารถใช้ได้ กรุณาตรวจสอบอีกครั้ง")
        sys.exit(1)

if __name__ == '__main__':
    main()

