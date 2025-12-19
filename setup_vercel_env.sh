#!/bin/bash
# Script สำหรับตั้งค่า Environment Variables ใน Vercel

# สร้าง SECRET_KEY
SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")

echo "Setting up Vercel Environment Variables..."
echo ""

# เพิ่ม Environment Variables
vercel env add FLASK_ENV production
vercel env add FLASK_DEBUG False
vercel env add SECRET_KEY "$SECRET_KEY"
vercel env add VERCEL 1

echo ""
echo "✅ Basic environment variables added!"
echo ""
echo "⚠️  You still need to add:"
echo "   - DATABASE_URL (from Supabase Coolify)"
echo "   - CORS_ORIGINS (https://medfiles.vercel.app)"
echo ""
echo "Add them with:"
echo "  vercel env add DATABASE_URL"
echo "  vercel env add CORS_ORIGINS"


