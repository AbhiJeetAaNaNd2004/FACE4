# 🎯 Face Recognition Attendance System

A comprehensive, production-ready face recognition-based attendance tracking system with real-time detection, automatic camera management, modern web interface, and role-based access control.

## 📋 Table of Contents

- [🚀 Quick Start](#-quick-start)
- [📁 Project Structure](#-project-structure)
- [🔧 Installation](#-installation)
- [⚙️ Environment Configuration](#️-environment-configuration)
- [🗄️ Database Setup](#️-database-setup)
- [🏃‍♂️ Running the Application](#️-running-the-application)
- [🌟 Features](#-features)
- [📹 Camera Management](#-camera-management)
- [👥 User Management](#-user-management)
- [🚀 Production Deployment](#-production-deployment)
- [🔧 Troubleshooting](#-troubleshooting)
- [📚 API Documentation](#-api-documentation)
- [🤝 Support](#-support)

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+**
- **Node.js 16+** (for frontend)
- **PostgreSQL 12+**
- **Git**

### 1-Minute Setup

```bash
# 1. Clone the repository
git clone <your-repository-url>
cd face-recognition-attendance-system

# 2. Create Python virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
cd frontend && npm install && cd ..

# 4. Setup database
python setup_postgresql.py

# 5. Initialize database tables
python backend/init_db.py

# 6. Start the system
python start_unified_server.py --enable-fts
```

**🎉 Your system is now running!**
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

**Default Login:**
- Username: `admin`
- Password: `admin123`

---

## 📁 Project Structure

```
face-recognition-attendance-system/
├── 📂 backend/                    # FastAPI backend application
│   ├── 📂 app/                    # Main application code
│   │   ├── 📂 routers/           # API route handlers
│   │   ├── 📂 models/            # Database models
│   │   └── main.py               # FastAPI app entry point
│   ├── 📂 core/                  # Core system components
│   │   └── fts_system.py         # Face Tracking System
│   ├── 📂 db/                    # Database configuration
│   │   ├── db_manager.py         # Database operations
│   │   └── models.py             # SQLAlchemy models
│   ├── 📂 utils/                 # Utility functions
│   │   ├── camera_discovery.py  # Camera detection
│   │   └── auto_camera_detector.py
│   ├── 📂 tasks/                 # Background tasks
│   ├── .env                      # Backend environment variables
│   └── init_db.py               # Database initialization
├── 📂 frontend/                   # React frontend application
│   ├── 📂 src/                   # React source code
│   │   ├── 📂 components/        # React components
│   │   ├── 📂 pages/             # Page components
│   │   ├── 📂 hooks/             # Custom React hooks
│   │   ├── 📂 utils/             # Frontend utilities
│   │   └── App.tsx               # Main React app
│   ├── 📂 public/                # Static assets
│   ├── package.json              # Frontend dependencies
│   └── tailwind.config.js        # Tailwind CSS config
├── 📂 logs/                      # Application logs
├── .env                          # Root environment variables
├── .gitignore                    # Git ignore file
├── requirements.txt              # Python dependencies
├── package.json                  # Root package.json with scripts
├── setup_postgresql.py          # Database setup script
├── setup_dev.sh                 # Development setup script
├── setup_env.sh                 # Environment setup script
├── start_unified_server.py      # Main application starter
├── start_system.sh              # System startup script (Linux)
├── start_camera_detection.py    # Camera detection utility
├── start_face_detection.py      # Face detection utility
└── README.md                    # This file
```

### 📝 Key Files Explained

| File | Purpose |
|------|---------|
| `start_unified_server.py` | **Main application entry point** - Starts backend, frontend, and face tracking |
| `setup_postgresql.py` | **Database setup** - Creates PostgreSQL database and user |
| `backend/init_db.py` | **Database initialization** - Creates tables and sample data |
| `.env` | **Environment configuration** - All system settings |
| `requirements.txt` | **Python dependencies** - All required Python packages |
| `package.json` | **Project scripts** - NPM scripts for development and deployment |
| `setup_dev.sh` | **Development setup** - Automated development environment setup |
| `start_system.sh` | **System startup** - Production-ready startup script for Linux |

---

## 🔧 Installation

### Development Mode Installation

#### Windows Setup

```cmd
# 1. Install Python 3.8+ from python.org
# 2. Install Node.js 16+ from nodejs.org
# 3. Install PostgreSQL 12+ from postgresql.org
# 4. Install Git from git-scm.com

# 5. Clone and setup project
git clone <repository-url>
cd face-recognition-attendance-system

# 6. Create virtual environment
python -m venv venv
venv\Scripts\activate

# 7. Install dependencies
pip install -r requirements.txt
cd frontend
npm install
cd ..

# 8. Setup database
python setup_postgresql.py

# 9. Initialize database
python backend\init_db.py
```

#### Linux Setup

```bash
# 1. Install system dependencies
sudo apt update
sudo apt install -y python3 python3-pip python3-venv nodejs npm postgresql postgresql-contrib git

# 2. Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 3. Clone and setup project
git clone <repository-url>
cd face-recognition-attendance-system

# 4. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 5. Install dependencies
pip install -r requirements.txt
cd frontend && npm install && cd ..

# 6. Setup database
python setup_postgresql.py

# 7. Initialize database
python backend/init_db.py
```

### Production Mode Installation

For production deployment, follow the development installation steps, then:

```bash
# 1. Build frontend for production
cd frontend
npm run build
cd ..

# 2. Update environment variables for production
# Edit .env file and set:
DEBUG=False
LOG_LEVEL=WARNING
SECRET_KEY=your-production-secret-key
JWT_SECRET_KEY=your-production-jwt-key

# 3. Setup reverse proxy (nginx recommended)
# 4. Configure SSL certificates
# 5. Setup process manager (systemd/PM2)
```

---

## ⚙️ Environment Configuration

### Environment Variables

The system uses `.env` files for configuration. Both root and backend directories have `.env` files that are **already created** with sensible defaults.

#### Root `.env` file contains:

```bash
# Database Configuration
DATABASE_URL=postgresql://facerecog_user:your_secure_password_here@localhost:5432/face_recognition_db
DB_HOST=localhost
DB_PORT=5432
DB_NAME=face_recognition_db
DB_USER=facerecog_user
DB_PASSWORD=your_secure_password_here

# Security Keys (CHANGE THESE IN PRODUCTION!)
SECRET_KEY=face-recognition-super-secret-key-change-this-in-production-2024
JWT_SECRET_KEY=jwt-secret-key-for-face-recognition-system-change-in-production

# Application Settings
DEBUG=True
BACKEND_PORT=8000
FRONTEND_PORT=3000

# Face Recognition Settings
FACE_DETECTION_THRESHOLD=0.5
FACE_RECOGNITION_THRESHOLD=0.6
MAX_FACE_DISTANCE=0.4

# Camera Settings
DEFAULT_CAMERA_RESOLUTION_WIDTH=1920
DEFAULT_CAMERA_RESOLUTION_HEIGHT=1080
DEFAULT_CAMERA_FPS=30
MAX_CAMERAS=16

# Performance Settings
ENABLE_GPU=True
BATCH_SIZE=1
NUM_WORKERS=4
```

### 🔒 Security Configuration

**IMPORTANT**: For production, you **MUST** change these values:

```bash
# Generate secure keys
SECRET_KEY=your-super-secure-secret-key-64-characters-minimum
JWT_SECRET_KEY=another-super-secure-jwt-key-64-characters-minimum
DB_PASSWORD=your-very-secure-database-password

# Set production mode
DEBUG=False
LOG_LEVEL=WARNING
```

---

## 🗄️ Database Setup

### Automatic Setup (Recommended)

```bash
# This script handles everything automatically
python setup_postgresql.py
```

### Manual Setup

If automatic setup fails, follow these steps:

#### 1. Create Database and User

```sql
-- Connect to PostgreSQL as superuser
sudo -u postgres psql

-- Create database and user
CREATE DATABASE face_recognition_db;
CREATE USER facerecog_user WITH PASSWORD 'your_secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE face_recognition_db TO facerecog_user;
\q
```

#### 2. Update Environment Variables

Update the database password in both `.env` files:
```bash
DB_PASSWORD=your_secure_password_here
```

#### 3. Initialize Database Tables

```bash
python backend/init_db.py
```

### Database Schema

The system creates these tables:
- **users** - System users (admins, super admins)
- **employees** - Employee records
- **departments** - Department information
- **cameras** - Camera configurations
- **attendance** - Attendance records
- **face_embeddings** - Face recognition data

---

## 🏃‍♂️ Running the Application

### Development Mode

#### Option 1: Unified Server (Recommended)
```bash
# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Start everything (backend + frontend + face tracking)
python start_unified_server.py --enable-fts
```

#### Option 2: Individual Components
```bash
# Terminal 1: Backend only
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend only
cd frontend
npm start

# Terminal 3: Face tracking (optional)
python start_face_detection.py
```

#### Option 3: Using NPM Scripts
```bash
# Start both backend and frontend
npm run dev

# Start only backend
npm run dev:backend

# Start only frontend
npm run dev:frontend
```

### Production Mode

#### Linux (systemd service)
```bash
# Copy service file
sudo cp face-recognition.service /etc/systemd/system/

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable face-recognition
sudo systemctl start face-recognition

# Check status
sudo systemctl status face-recognition
```

#### Using Process Manager
```bash
# Using PM2
npm install -g pm2
pm2 start start_unified_server.py --name face-recognition

# Using screen (simple option)
screen -S face-recognition
python start_unified_server.py --enable-fts
# Ctrl+A, D to detach
```

### Application URLs

Once running, access the system at:

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:3000 | Main web interface |
| **Backend API** | http://localhost:8000 | REST API endpoints |
| **API Documentation** | http://localhost:8000/docs | Interactive API docs |
| **Admin Panel** | http://localhost:3000/admin | Admin dashboard |

---

## 🌟 Features

### ✅ Core Features

- **🎯 Real-time Face Recognition** - AI-powered attendance tracking using InsightFace
- **📹 Multi-Camera Support** - Support for USB, built-in, and IP cameras
- **🔄 Automatic Camera Detection** - Auto-discovers and configures cameras
- **👥 Employee Management** - Complete employee lifecycle management
- **📊 Attendance Tracking** - Automated check-in/check-out with reporting
- **🎛️ Admin Dashboard** - Comprehensive admin interface
- **🔐 Role-Based Access** - Super Admin, Admin, and Employee roles
- **📱 Responsive Design** - Works on desktop, tablet, and mobile
- **🚀 REST API** - Complete API with documentation
- **📈 Real-time Updates** - WebSocket-based live updates

### 🔧 Advanced Features

- **🔍 Smart Camera Discovery** - ONVIF protocol support for IP cameras
- **📐 Tripwire Detection** - Configurable detection zones
- **⚡ GPU Acceleration** - CUDA support for better performance
- **📊 Performance Monitoring** - System stats and metrics
- **🔒 JWT Authentication** - Secure token-based authentication
- **📝 Comprehensive Logging** - Detailed system and error logs
- **�� Automatic Backup** - Database and face data backup
- **🌐 Multi-language Support** - Internationalization ready

---

## 📹 Camera Management

### Automatic Camera Detection

The system automatically detects cameras when started:

```bash
# Start with automatic camera detection
python start_unified_server.py --enable-fts
```

### Manual Camera Management

1. **Access Camera Management**
   - Login as Super Admin
   - Go to **Admin** → **Camera Management**

2. **Auto-Detect Cameras**
   - Click **"🔍 Auto-Detect Cameras"**
   - System scans for USB and IP cameras
   - Detected cameras appear in the list

3. **Configure Camera Settings**
   - **Name**: Descriptive camera name
   - **Resolution**: 720p, 1080p, 4K options
   - **FPS**: 15, 30, 60 FPS options
   - **Status**: Active/Inactive
   - **Location**: Physical location description

### Supported Cameras

| Type | Examples | Notes |
|------|----------|-------|
| **USB Cameras** | Logitech, Microsoft, Generic | Plug and play |
| **Built-in Cameras** | Laptop webcams | Automatically detected |
| **IP Cameras** | Hikvision, Dahua, Axis | ONVIF protocol support |
| **RTSP Streams** | Network cameras | Custom RTSP URL support |

### Camera Performance Optimization

| Setting | Low-End System | Mid-Range System | High-End System |
|---------|---------------|------------------|-----------------|
| **Resolution** | 720p | 1080p | 4K |
| **FPS** | 15 | 30 | 60 |
| **Max Cameras** | 2-4 | 8-12 | 16+ |

---

## 👥 User Management

### Default Users

The system comes with pre-configured users:

| Username | Password | Role | Permissions |
|----------|----------|------|-------------|
| `admin` | `admin123` | Super Admin | Full system access |
| `user` | `user123` | Admin | Employee and attendance management |

**⚠️ IMPORTANT**: Change these passwords immediately after first login!

### User Roles

#### Super Admin
- Full system access
- User management
- System configuration
- Camera management
- Database operations

#### Admin
- Employee management
- Attendance tracking
- Report generation
- Camera monitoring

#### Employee (Future)
- View own attendance
- Update profile
- Check-in/out manually

### Creating New Users

1. Login as Super Admin
2. Go to **Super Admin** → **User Management**
3. Click **"Add User"**
4. Fill in user details:
   - Username (unique)
   - Password (secure)
   - Role (Admin/Super Admin)
   - Link to employee record (optional)
5. Save user

---

## 🚀 Production Deployment

### Pre-Production Checklist

- [ ] Change default passwords
- [ ] Update environment variables for production
- [ ] Set up SSL certificates
- [ ] Configure firewall rules
- [ ] Set up database backups
- [ ] Configure monitoring
- [ ] Test all functionality

### Environment Configuration

```bash
# Production .env settings
DEBUG=False
LOG_LEVEL=WARNING
SECRET_KEY=your-production-secret-key-minimum-64-characters
JWT_SECRET_KEY=your-production-jwt-key-minimum-64-characters
DB_PASSWORD=your-secure-production-database-password

# Security settings
JWT_EXPIRE_MINUTES=30
CORS_ORIGINS=["https://yourdomain.com"]
```

### Reverse Proxy Setup (Nginx)

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # WebSocket support
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### Process Management

#### Systemd Service (Linux)

Create `/etc/systemd/system/face-recognition.service`:

```ini
[Unit]
Description=Face Recognition Attendance System
After=network.target postgresql.service

[Service]
Type=simple
User=facerecog
WorkingDirectory=/opt/face-recognition-system
Environment=PATH=/opt/face-recognition-system/venv/bin
ExecStart=/opt/face-recognition-system/venv/bin/python start_unified_server.py --enable-fts
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable face-recognition
sudo systemctl start face-recognition
```

### Monitoring and Logging

#### Log Rotation

Create `/etc/logrotate.d/face-recognition`:

```
/opt/face-recognition-system/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 facerecog facerecog
}
```

#### Health Monitoring

```bash
# Health check script
#!/bin/bash
curl -f http://localhost:8000/health || exit 1
```

### Backup Strategy

```bash
# Database backup
pg_dump -U facerecog_user face_recognition_db > backup_$(date +%Y%m%d).sql

# Face encodings backup
tar -czf face_encodings_backup_$(date +%Y%m%d).tar.gz face_encodings/
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Database Connection Failed

```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Restart PostgreSQL
sudo systemctl restart postgresql

# Test connection
psql -h localhost -U facerecog_user -d face_recognition_db
```

#### 2. Camera Not Detected

**USB Cameras:**
- Check physical connection
- Try different USB ports
- Close other applications using camera
- Check camera permissions (Linux):
  ```bash
  sudo usermod -a -G video $USER
  # Logout and login again
  ```

**IP Cameras:**
- Verify network connectivity: `ping camera_ip`
- Check camera credentials
- Ensure ONVIF is enabled
- Check firewall settings

#### 3. Frontend Not Loading

```bash
# Check if backend is running
curl http://localhost:8000/health

# Rebuild frontend
cd frontend
npm install
npm run build
cd ..

# Clear browser cache
```

#### 4. Face Recognition Not Working

- Ensure good lighting conditions
- Check camera focus and position
- Verify employees have enrolled faces
- Adjust detection thresholds in `.env`:
  ```bash
  FACE_DETECTION_THRESHOLD=0.4  # Lower = more sensitive
  FACE_RECOGNITION_THRESHOLD=0.5 # Lower = more lenient
  ```

#### 5. Performance Issues

**System Optimization:**
- Lower camera resolution (4K → 1080p → 720p)
- Reduce FPS (60 → 30 → 15)
- Disable unused cameras
- Close unnecessary applications

**Memory Issues:**
```bash
# Check system resources
htop  # Linux
# Task Manager (Windows)

# Adjust performance settings in .env
GPU_MEMORY_FRACTION=0.6
BATCH_SIZE=1
MAX_CAMERAS=8
```

### Log Files

Check application logs for detailed error information:

```bash
# Application logs
tail -f logs/app.log

# Backend logs
tail -f backend/backend.log

# Frontend logs (browser console)
# Open browser developer tools (F12)
```

### Getting Help

1. **Check logs** for error details
2. **Verify environment** variables are correct
3. **Test database** connection
4. **Check camera** permissions and connections
5. **Review system** requirements
6. **Consult API documentation** at http://localhost:8000/docs

---

## 📚 API Documentation

### Base URL
- **Development**: http://localhost:8000
- **Production**: https://yourdomain.com/api

### Authentication

```bash
# Login
POST /auth/login
{
  "username": "admin",
  "password": "admin123"
}

# Response
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "username": "admin",
    "role": "super_admin"
  }
}
```

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | System health check |
| `POST` | `/auth/login` | User authentication |
| `GET` | `/employees/` | List all employees |
| `POST` | `/employees/` | Create new employee |
| `POST` | `/employees/{id}/enroll-face` | Enroll employee face |
| `GET` | `/cameras/` | List all cameras |
| `POST` | `/cameras/auto-detect` | Auto-detect cameras |
| `GET` | `/attendance/` | Get attendance records |
| `POST` | `/system/start` | Start face tracking system |
| `POST` | `/system/stop` | Stop face tracking system |
| `GET` | `/system/status` | Get system status |

### Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🤝 Support

### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **OS** | Windows 10, Ubuntu 18.04 | Windows 11, Ubuntu 20.04+ |
| **RAM** | 4GB | 8GB+ |
| **CPU** | Dual-core 2.5GHz | Quad-core 3.0GHz+ |
| **Storage** | 5GB | 20GB SSD |
| **GPU** | None | NVIDIA GTX 1060+ |
| **Network** | 100Mbps | Gigabit Ethernet |

### Performance Guidelines

| Use Case | Configuration | Expected Performance |
|----------|---------------|---------------------|
| **Small Office (1-2 cameras)** | 4GB RAM, Dual-core CPU | 30 FPS, <100ms response |
| **Medium Office (4-8 cameras)** | 8GB RAM, Quad-core CPU | 30 FPS, <200ms response |
| **Large Office (8+ cameras)** | 16GB RAM, 8-core CPU, GPU | 30 FPS, <300ms response |

### Maintenance

#### Daily Tasks
- Monitor system logs
- Check camera functionality
- Verify attendance accuracy

#### Weekly Tasks
- Review system performance
- Check database integrity
- Update face encodings if needed

#### Monthly Tasks
- Update system packages
- Review security settings
- Performance optimization

### Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### License

This project is licensed under the MIT License. See LICENSE file for details.

---

**🎉 Congratulations!** Your Face Recognition Attendance System is now ready for use. The system provides enterprise-grade face recognition with automatic camera management, making attendance tracking effortless and accurate.

For technical support or questions, please check the troubleshooting section or refer to the API documentation.
