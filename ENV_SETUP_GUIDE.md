# 🔧 Environment Configuration Guide

## 📍 **Where to Create the .env File**

You need to create the `.env` file in the **`backend`** directory:

```
Face-Recognition-Attendance-System/
├── frontend/
├── backend/                    ← CREATE .env FILE HERE
│   ├── app/
│   ├── core/
│   ├── db/
│   ├── utils/
│   ├── .env                   ← THIS FILE
│   ├── .env.example           ← EXAMPLE TEMPLATE
│   └── ...
└── README.md
```

## 🚀 **Quick Setup Steps**

### Step 1: Navigate to Backend Directory
```bash
cd backend
```

### Step 2: Copy the Example File
```bash
cp .env.example .env
```

### Step 3: Edit the .env File
```bash
# Use your preferred editor
nano .env
# or
vim .env
# or
code .env
```

## 🔑 **Required Environment Variables**

### **CRITICAL - Must Be Set:**

#### 1. Database Password
```env
DB_PASSWORD=your_secure_database_password_here
```
**⚠️ IMPORTANT**: Replace with your actual PostgreSQL password

#### 2. JWT Secret Key
```env
SECRET_KEY=your_super_secure_secret_key_here_minimum_32_characters
```
**⚠️ IMPORTANT**: Use a strong, unique secret key (minimum 32 characters)

### **Generate Secure Secret Key:**
```bash
# Option 1: Using Python
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Option 2: Using OpenSSL
openssl rand -base64 32

# Option 3: Using UUID
python3 -c "import uuid; print(str(uuid.uuid4()) + str(uuid.uuid4()))"
```

## 📋 **Complete .env File Template**

Create your `.env` file with these contents:

```env
# =============================================================================
# REQUIRED VARIABLES - MUST BE SET
# =============================================================================
DB_PASSWORD=your_actual_database_password
SECRET_KEY=your_generated_secret_key_here

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================
DB_HOST=localhost
DB_PORT=5432
DB_NAME=frs_db
DB_USER=postgres

# =============================================================================
# SECURITY CONFIGURATION
# =============================================================================
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# =============================================================================
# APPLICATION CONFIGURATION
# =============================================================================
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# =============================================================================
# CORS CONFIGURATION
# =============================================================================
FRONTEND_URL=http://localhost:3000
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# =============================================================================
# FACE RECOGNITION CONFIGURATION
# =============================================================================
FACE_RECOGNITION_TOLERANCE=0.6
FACE_DETECTION_MODEL=hog
FACE_ENCODING_MODEL=large

# =============================================================================
# CAMERA CONFIGURATION
# =============================================================================
DEFAULT_CAMERA_ID=0
MAX_CONCURRENT_STREAMS=5
STREAM_QUALITY=medium
FRAME_RATE=30

# =============================================================================
# FILE STORAGE CONFIGURATION
# =============================================================================
UPLOAD_DIR=uploads
FACE_IMAGES_DIR=face_images
MAX_FILE_SIZE=10485760

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================
LOG_FILE=logs/app.log
LOG_ROTATION=1 day
LOG_RETENTION=30 days

# =============================================================================
# FTS CONFIGURATION
# =============================================================================
FTS_AUTO_START=true
FTS_STARTUP_DELAY=2
FACE_TRACKING_AUTO_START=true
```

## 🔒 **Security Best Practices**

### 1. **Never Commit .env to Git**
The `.env` file should already be in `.gitignore`, but verify:
```bash
# Check if .env is ignored
git status
# .env should NOT appear in untracked files
```

### 2. **Use Strong Passwords**
- Database password: minimum 12 characters, mixed case, numbers, symbols
- Secret key: minimum 32 characters, cryptographically secure

### 3. **Environment-Specific Configuration**

#### **Development (.env)**
```env
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO
FTS_AUTO_START=true
```

#### **Production (.env)**
```env
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING
FTS_AUTO_START=false
DB_HOST=your_production_db_host
FRONTEND_URL=https://your-domain.com
ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com
```

## 🗃️ **Database Configuration**

### **Local PostgreSQL Setup**
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=frs_db
DB_USER=postgres
DB_PASSWORD=your_postgres_password
```

### **Remote Database (Production)**
```env
DB_HOST=your-db-server.com
DB_PORT=5432
DB_NAME=frs_production
DB_USER=frs_user
DB_PASSWORD=your_secure_production_password
```

### **Docker PostgreSQL**
```env
DB_HOST=localhost  # or docker container name
DB_PORT=5432
DB_NAME=frs_db
DB_USER=postgres
DB_PASSWORD=docker_postgres_password
```

## 🌐 **Frontend Integration**

### **React Development Server**
```env
FRONTEND_URL=http://localhost:3000
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### **Vite Development Server**
```env
FRONTEND_URL=http://localhost:5173
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

### **Production Frontend**
```env
FRONTEND_URL=https://your-app.com
ALLOWED_ORIGINS=https://your-app.com,https://www.your-app.com
```

## 📹 **Camera Configuration**

### **Single Camera Setup**
```env
DEFAULT_CAMERA_ID=0
MAX_CONCURRENT_STREAMS=1
```

### **Multiple Camera Setup**
```env
DEFAULT_CAMERA_ID=0
MAX_CONCURRENT_STREAMS=5
```

### **High-Performance Setup**
```env
STREAM_QUALITY=high
FRAME_RATE=60
MAX_CONCURRENT_STREAMS=10
```

## 🎯 **Face Recognition Tuning**

### **High Accuracy (Slower)**
```env
FACE_RECOGNITION_TOLERANCE=0.4
FACE_DETECTION_MODEL=cnn
FACE_ENCODING_MODEL=large
```

### **Balanced Performance**
```env
FACE_RECOGNITION_TOLERANCE=0.6
FACE_DETECTION_MODEL=hog
FACE_ENCODING_MODEL=large
```

### **Fast Performance (Lower Accuracy)**
```env
FACE_RECOGNITION_TOLERANCE=0.8
FACE_DETECTION_MODEL=hog
FACE_ENCODING_MODEL=small
```

## 🔍 **Troubleshooting**

### **Common Issues:**

#### 1. **"DB_PASSWORD is required" Error**
```bash
# Check if .env file exists
ls -la backend/.env

# Check if DB_PASSWORD is set
grep DB_PASSWORD backend/.env
```

#### 2. **"SECRET_KEY is required" Error**
```bash
# Generate a new secret key
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"
```

#### 3. **Database Connection Error**
```bash
# Test database connection
psql -h localhost -U postgres -d frs_db
```

#### 4. **CORS Errors**
```env
# Add your frontend URL to ALLOWED_ORIGINS
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,YOUR_FRONTEND_URL
```

## ✅ **Verification Steps**

### 1. **Check Configuration Loading**
```bash
cd backend
python3 -c "from app.config import settings; print('✅ Configuration loaded successfully')"
```

### 2. **Verify Database Connection**
```bash
cd backend
python3 -c "from app.config import settings; print(f'Database URL: {settings.DATABASE_URL}')"
```

### 3. **Test Environment Variables**
```bash
cd backend
python3 -c "
from app.config import settings
print(f'Environment: {settings.ENVIRONMENT}')
print(f'Debug: {settings.DEBUG}')
print(f'Database: {settings.DB_NAME}')
print(f'Secret Key Length: {len(settings.SECRET_KEY)}')
"
```

## 🚀 **Ready to Run**

Once your `.env` file is configured:

```bash
# Navigate to backend
cd backend

# Install dependencies (if not already done)
pip install -r requirements.txt

# Initialize database
python3 init_db.py

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 📝 **Summary**

**Location**: `backend/.env`

**Required Variables**:
- `DB_PASSWORD` (your PostgreSQL password)
- `SECRET_KEY` (32+ character secure key)

**Optional**: All other variables have sensible defaults

**Security**: Never commit `.env` to version control

The system will automatically load these environment variables when starting the backend server.