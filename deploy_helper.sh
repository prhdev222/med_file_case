#!/bin/bash
# Helper script for deployment preparation

echo "🚀 Hospital Administration System - Deployment Helper"
echo "=================================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from env.example...${NC}"
    if [ -f env.example ]; then
        cp env.example .env
        echo -e "${GREEN}✅ Created .env file. Please update it with your production values!${NC}"
    else
        echo -e "${RED}❌ env.example not found!${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ .env file exists${NC}"
fi

# Check if frontend directory exists
if [ ! -d "frontend" ]; then
    echo -e "${RED}❌ Frontend directory not found!${NC}"
    exit 1
fi

# Build frontend
echo ""
echo "📦 Building frontend..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "Installing npm dependencies..."
    npm install
fi

echo "Building frontend for production..."
npm run build

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Frontend build failed!${NC}"
    exit 1
fi

cd ..
echo -e "${GREEN}✅ Frontend build completed${NC}"

# Check Python dependencies
echo ""
echo "🐍 Checking Python dependencies..."
if ! python3 -c "import flask" 2>/dev/null; then
    echo "Installing Python dependencies..."
    pip install -r requirements.txt
else
    echo -e "${GREEN}✅ Python dependencies installed${NC}"
fi

# Generate secret key
echo ""
echo "🔑 Generating secret key..."
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
echo -e "${YELLOW}Generated SECRET_KEY: ${SECRET_KEY}${NC}"
echo "Please add this to your .env file:"
echo "SECRET_KEY=$SECRET_KEY"

# Check required files
echo ""
echo "📋 Checking required files..."
REQUIRED_FILES=("app.py" "requirements.txt" "Procfile" "wsgi.py")
MISSING_FILES=()

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        MISSING_FILES+=("$file")
    fi
done

if [ ${#MISSING_FILES[@]} -eq 0 ]; then
    echo -e "${GREEN}✅ All required files present${NC}"
else
    echo -e "${RED}❌ Missing files: ${MISSING_FILES[*]}${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✅ Deployment preparation completed!${NC}"
echo ""
echo "Next steps:"
echo "1. Update .env file with production values"
echo "2. Set SECRET_KEY in your hosting platform"
echo "3. Set DATABASE_URL (use PostgreSQL for production)"
echo "4. Set CORS_ORIGINS to your domain"
echo "5. Deploy to your chosen platform"
echo ""
echo "For detailed instructions, see:"
echo "  - DEPLOY_QUICK_START.md (quick guide)"
echo "  - DEPLOYMENT_GUIDE.md (full guide)"


