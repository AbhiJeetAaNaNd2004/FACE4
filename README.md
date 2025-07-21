# 🎯 Face Recognition Attendance System

A comprehensive face recognition-based attendance tracking system with real-time detection, automatic camera management, web interface, and role-based access control.

## 📋 Table of Contents

1. [Quick Start](#-quick-start)
   - [Fixed Quick Start (Recommended)](#-option-1-fixed-quick-start-recommended-for-memory-issues)
   - [Standard Quick Start](#-option-2-standard-quick-start)
   - [Software Dependencies](#software-dependencies)
2. [Installation](#-installation)
   - [Standard Installation](#method-1-standard-installation)
   - [GPU Accelerated Installation](#method-2-gpu-accelerated-installation)
   - [Docker Installation](#method-3-docker-installation)
   - [System Dependencies](#system-dependencies-ubuntudebian)
3. [Features Overview](#-features-overview)
4. [System Requirements](#-system-requirements)
5. [Installation Guide](#-installation-guide)
   - [Windows Setup](#windows-setup)
   - [Linux Setup](#linux-setup)
6. [Database Setup](#-database-setup)
7. [Environment Configuration](#-environment-configuration)
8. [Starting the System](#-starting-the-system)
9. [Camera Management](#-camera-management)
10. [Usage Guide](#-usage-guide)
11. [Troubleshooting](#-troubleshooting)
12. [Performance Optimization](#-performance-optimization)
13. [Production Deployment](#-production-deployment)
14. [API Documentation](#-api-documentation)

---

## 🚀 Quick Start

### ⚡ Option 1: Fixed Quick Start (Recommended for Memory Issues)

```bash
# 1. Clone the repository
git clone <repository-url>
cd face-recognition-attendance-system

# 2. Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# 3. Install all dependencies
pip install -r requirements.txt
cd frontend && npm install && cd ..

# 4. Setup database (PostgreSQL)
python setup_postgresql.py  # Creates PostgreSQL database
python backend/init_db.py   # Initializes tables and sample data

# 5. Start with memory optimizations (RECOMMENDED)
python start_system_fixed.py
```

### ⚡ Option 2: Standard Quick Start

```bash
# Follow steps 1-4 above, then:

# 5. Start the unified server with face tracking
python start_unified_server.py --enable-fts
```

### Software Dependencies
```bash
# Core requirements
Python 3.8+         # Backend runtime
Node.js 16+         # Frontend build tools (optional)
PostgreSQL 12+      # Database server (recommended)
Git                 # Version control

# Optional (for GPU acceleration)
CUDA Toolkit 11.x   # For GPU-accelerated face recognition
```

## 🔧 Installation

### Method 1: Standard Installation

```bash
# Install core dependencies
pip install fastapi uvicorn sqlalchemy requests python-dotenv

# Install computer vision libraries
pip install opencv-python numpy Pillow

# Install face recognition libraries
pip install onnxruntime faiss-cpu insightface

# Install all dependencies at once
pip install -r requirements.txt
```

### Method 2: GPU Accelerated Installation

```bash
# For NVIDIA GPU acceleration
pip install faiss-gpu onnxruntime-gpu

# Verify CUDA compatibility
python -c "import torch; print(torch.cuda.is_available())"
```

### Method 3: Docker Installation

```bash
# Build the container
docker build -t face-recognition-attendance .

# Run the container
docker run -p 8000:8000 -p 3000:3000 face-recognition-attendance
```

### System Dependencies (Ubuntu/Debian)
```bash
# Install system packages
sudo apt update
sudo apt install -y \
  python3 python3-pip python3-dev \
  nodejs npm \
  postgresql postgresql-contrib \
  build-essential cmake \
  libopencv-dev python3-opencv \
  git curl wget
```

---

## 🌟 Features Overview

### ✅ **Core Functionality**
- **🎯 Real-time Face Detection & Recognition** - AI-powered attendance tracking using InsightFace
- **📹 Automatic Camera Management** - Auto-detects and configures USB, built-in, and network cameras
- **🔄 Multi-Camera Support** - Process up to 16+ camera feeds simultaneously
- **👥 Role-Based Access Control** - Super Admin, Admin, and Employee access levels
- **💻 Modern Web Dashboard** - React frontend with real-time updates and responsive design
- **🚀 RESTful API** - FastAPI backend with comprehensive OpenAPI documentation
- **📊 Attendance Tracking** - Automated check-in/check-out with detailed reporting
- **👤 Employee Management** - Complete employee lifecycle management
- **📡 Live Monitoring** - Real-time camera feeds with detection overlays

### 🔧 **Advanced Features**
- **🔍 Comprehensive Camera Detection** - Detects USB, built-in, and IP cameras automatically
- **⚙️ Smart Camera Configuration** - Super admin interface for selecting and configuring cameras for FTS
- **📐 Advanced Tripwire System** - Configurable detection zones with directional crossing detection
- **🌐 ONVIF Camera Discovery** - Automatic network camera detection and integration
- **🎛️ Granular Camera Control** - Enable/disable cameras, adjust settings, and manage FTS integration
- **⚡ Real-time Updates** - WebSocket-based live activity feeds
- **🔐 JWT Authentication** - Secure token-based authentication system
- **📈 Performance Monitoring** - Real-time system stats and camera performance metrics

### 🏗️ **Technology Stack**
- **Backend**: FastAPI (Python), PostgreSQL, SQLAlchemy ORM
- **Frontend**: React 18, TypeScript, Tailwind CSS, Zustand
- **AI/ML**: InsightFace, FAISS, OpenCV, ByteTracker
- **Authentication**: JWT tokens with bcrypt password hashing
- **Real-time**: WebSocket for live updates
- **Camera**: ONVIF protocol, RTSP streaming, USB camera support

---

## 💻 System Requirements

### **Minimum Requirements**
- **OS**: Windows 10+ or Linux (Ubuntu 18.04+, CentOS 7+)
- **RAM**: 4GB (8GB+ recommended for multiple cameras)
- **CPU**: Dual-core 2.5GHz (Quad-core 3.0GHz+ recommended)
- **Storage**: 5GB free space (more for face data storage)
- **Network**: Internet connection for package installation
- **Cameras**: USB webcam or IP camera (optional for testing)

### **Recommended Setup**
- **RAM**: 8-16GB for optimal performance
- **CPU**: Quad-core 3.0GHz+ or 8-core for multiple cameras
- **GPU**: NVIDIA GPU with CUDA support (optional but recommended)
- **Storage**: SSD with 20GB+ free space
- **Network**: Gigabit Ethernet for IP cameras

### **High-Performance Setup (4K, Multiple Cameras)**
- **RAM**: 16GB+
- **CPU**: 8-core 3.5GHz+ (Intel i7/i9 or AMD Ryzen 7/9)
- **GPU**: NVIDIA GTX 1060+ or RTX series
- **Storage**: NVMe SSD with 50GB+ free space

---

## 🚀 Installation Guide

### **Windows Setup**

#### **Step 1: Install Python**
1. Download Python 3.8-3.11 from [python.org](https://www.python.org/downloads/)
2. **Important**: Check "Add Python to PATH" during installation
3. Verify installation:
```cmd
python --version
pip --version
```

#### **Step 2: Install Git**
1. Download Git from [git-scm.com](https://git-scm.com/download/win)
2. Install with default settings
3. Verify: `git --version`

#### **Step 3: Install PostgreSQL**
1. Download PostgreSQL 12+ from [postgresql.org](https://www.postgresql.org/download/windows/)
2. During installation:
   - Set password for `postgres` user (remember this!)
   - Use default port `5432`
   - Install pgAdmin (recommended)
3. Verify installation:
```cmd
psql --version
```

#### **Step 4: Install System Dependencies**
Open **Command Prompt as Administrator** and run:
```cmd
# Install Visual C++ Build Tools (required for some packages)
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/

# Install required Windows packages
pip install --upgrade pip setuptools wheel
```

#### **Step 5: Clone and Setup Project**
```cmd
# Clone the repository
git clone https://github.com/your-repo/face-recognition-system.git
cd face-recognition-system

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Install additional Windows-specific packages
pip install psycopg2-binary bcrypt passlib psutil
```

#### **Step 6: Install Node.js (for Frontend)**
1. Download Node.js 16+ from [nodejs.org](https://nodejs.org/)
2. Install with default settings
3. Verify: `node --version` and `npm --version`

#### **Step 7: Setup Frontend**
```cmd
cd frontend
npm install
npm run build
cd ..
```

---

### **Linux Setup**

#### **Step 1: Update System**
```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade -y

# CentOS/RHEL
sudo yum update -y
# OR for newer versions
sudo dnf update -y
```

#### **Step 2: Install Python and Development Tools**
```bash
# Ubuntu/Debian
sudo apt install -y python3 python3-pip python3-venv python3-dev
sudo apt install -y build-essential libssl-dev libffi-dev
sudo apt install -y libpq-dev python3-psycopg2

# CentOS/RHEL
sudo yum groupinstall -y "Development Tools"
sudo yum install -y python3 python3-pip python3-devel
sudo yum install -y postgresql-devel openssl-devel libffi-devel

# OR for newer CentOS/RHEL
sudo dnf groupinstall -y "Development Tools"
sudo dnf install -y python3 python3-pip python3-devel
sudo dnf install -y postgresql-devel openssl-devel libffi-devel
```

#### **Step 3: Install Git**
```bash
# Ubuntu/Debian
sudo apt install -y git

# CentOS/RHEL
sudo yum install -y git
# OR
sudo dnf install -y git
```

#### **Step 4: Install PostgreSQL**
```bash
# Ubuntu/Debian
sudo apt install -y postgresql postgresql-contrib postgresql-client
sudo systemctl start postgresql
sudo systemctl enable postgresql

# CentOS/RHEL
sudo yum install -y postgresql-server postgresql-contrib
# OR
sudo dnf install -y postgresql-server postgresql-contrib

sudo postgresql-setup initdb
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### **Step 5: Install Camera and Media Dependencies**
```bash
# Ubuntu/Debian
sudo apt install -y v4l-utils ffmpeg libopencv-dev
sudo apt install -y libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev

# CentOS/RHEL
sudo yum install -y v4l-utils ffmpeg opencv-devel
# OR
sudo dnf install -y v4l-utils ffmpeg opencv-devel
```

#### **Step 6: Clone and Setup Project**
```bash
# Clone the repository
git clone https://github.com/your-repo/face-recognition-system.git
cd face-recognition-system

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip and install dependencies
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Install additional system packages for better compatibility
pip install psycopg2-binary bcrypt passlib psutil
```

#### **Step 7: Install Node.js (for Frontend)**
```bash
# Ubuntu/Debian - Install via NodeSource
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# CentOS/RHEL - Install via NodeSource
curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
sudo yum install -y nodejs
# OR
sudo dnf install -y nodejs
```

#### **Step 8: Setup Frontend**
```bash
cd frontend
npm install
npm run build
cd ..
```

---

## 🗄️ Database Setup

### **Create Database and User**

#### **Windows**
```cmd
# Connect to PostgreSQL (enter password when prompted)
psql -U postgres -h localhost

# In PostgreSQL shell:
CREATE DATABASE face_recognition_db;
CREATE USER facerecog_user WITH PASSWORD 'your_secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE face_recognition_db TO facerecog_user;
\q
```

#### **Linux**
```bash
# Switch to postgres user and create database
sudo -u postgres psql

# In PostgreSQL shell:
CREATE DATABASE face_recognition_db;
CREATE USER facerecog_user WITH PASSWORD 'your_secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE face_recognition_db TO facerecog_user;
\q
```

### **Test Database Connection**
```bash
# Test connection (both Windows and Linux)
psql -h localhost -U facerecog_user -d face_recognition_db

# If successful, you should see:
# face_recognition_db=>

# Exit with: \q
```

---

## ⚙️ Environment Configuration

### **Create Environment File**
Create a `.env` file in the project root:

```bash
# Database Configuration
DATABASE_URL=postgresql://facerecog_user:your_secure_password_here@localhost:5432/face_recognition_db
DB_HOST=localhost
DB_PORT=5432
DB_NAME=face_recognition_db
DB_USER=facerecog_user
DB_PASSWORD=your_secure_password_here

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production
JWT_SECRET_KEY=another-secret-key-for-jwt-tokens
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60

# Application Settings
DEBUG=True
LOG_LEVEL=INFO
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
GPU_MEMORY_FRACTION=0.7
BATCH_SIZE=1
NUM_WORKERS=4

# File Paths
UPLOAD_DIR=uploads
FACE_ENCODINGS_DIR=face_encodings
LOGS_DIR=logs
```

### **Initialize Database Tables**
```bash
# Activate virtual environment first
# Windows:
venv\Scripts\activate
# Linux:
source venv/bin/activate

# Initialize database
python -c "
from db.db_manager import DatabaseManager
db = DatabaseManager()
db.init_database()
print('Database initialized successfully!')
"
```

---

## 🚀 Starting the System

### **Quick Start (Unified Server)**
```bash
# Windows
venv\Scripts\activate
python start_unified_server.py --enable-fts

# Linux
source venv/bin/activate
python start_unified_server.py --enable-fts
```

**The system will be available at:**
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### **Component-by-Component Startup**

#### **Option 1: Start Backend Only**
```bash
# Windows
venv\Scripts\activate
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Linux
source venv/bin/activate
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### **Option 2: Start Frontend Only**
```bash
cd frontend
npm start
# Runs on http://localhost:3000
```

#### **Option 3: Start Face Tracking System Only**
```bash
# Windows
venv\Scripts\activate
python start_fts_only.py

# Linux
source venv/bin/activate
python start_fts_only.py
```

### **Default Credentials**
- **Super Admin**: `admin` / `admin123`
- **Regular Admin**: `user` / `user123`

**⚠️ IMPORTANT**: Change these passwords immediately after first login!

---

## 📹 Camera Management

### **🔄 Automatic Camera Detection**
The system automatically detects all connected cameras when FTS starts:

```bash
# Cameras are auto-detected when you start with FTS enabled
python start_unified_server.py --enable-fts
```

**Supported Camera Types:**
- ✅ USB Webcams and Security Cameras
- ✅ Built-in Laptop/Desktop Cameras  
- ✅ IP Cameras with ONVIF Support
- ✅ RTSP Network Streams

### **📋 Manual Camera Management**

#### **Auto-Detect Cameras Anytime**
1. **Via Super Admin Dashboard**:
   - Login as Super Admin
   - Go to **Super Admin Dashboard**
   - Click **"Auto-Detect Cameras"** in Quick Actions
   - Click **"Start Detection"**

2. **Via Camera Management**:
   - Go to **Admin** → **Camera Management**  
   - Click **"🔍 Auto-Detect Cameras"** button
   - Detected cameras appear in the list automatically

#### **Configure Individual Camera Settings**
1. Go to **Admin** → **Camera Management**
2. Find your camera and click **"⚙️ Settings"**
3. Configure the following:

**📝 Camera Name**
- Set descriptive names (e.g., "Main Entrance", "Office Floor 2")
- Used throughout the system for identification

**📐 Resolution Settings**
Choose from presets:
- **VGA**: 640 × 480 (4:3) - Basic quality
- **HD 720p**: 1280 × 720 (16:9) - Good performance
- **Full HD 1080p**: 1920 × 1080 (16:9) ⭐ **Recommended**
- **QHD 1440p**: 2560 × 1440 (16:9) - High quality
- **4K UHD**: 3840 × 2160 (16:9) - Maximum quality

Or set **Custom Resolution**: 320×240 to 4096×2160 pixels

**🎬 Frame Rate (FPS)**
Preset options: 5, 10, 15, 20, 24, 25, 30, 60 FPS
- **Recommended**: 30 FPS for balanced performance
- **High Performance**: 60 FPS (requires more processing power)
- **Power Saving**: 15 FPS for basic monitoring
- **Custom**: 1-120 FPS

**📍 Location Description**
- Physical location details for easy identification

**🔛 Camera Status**  
- **Active**: Camera participates in face detection
- **Inactive**: Camera is disabled and not used

4. Click **"Save Settings"** - Changes apply immediately!

### **📏 Tripwire Configuration**
Set virtual detection lines for entry/exit monitoring:

1. In Camera Management, click **"Edit"** on a camera
2. Configure tripwire settings:
   - **Position**: Where detection line appears (0.0-1.0)
   - **Spacing**: Width of detection zone  
   - **Direction**: Horizontal or Vertical
   - **Name**: Descriptive tripwire name

### **🎯 Recommended Camera Settings**

**🏢 Office Environments**
- Resolution: 1920×1080 (Full HD)
- FPS: 30
- Tripwire: Horizontal at entrance doors

**🚶 High-Traffic Areas**  
- Resolution: 1280×720 (HD 720p)
- FPS: 30-60
- Multiple tripwires for entry/exit detection

**💻 Low-Power Systems**
- Resolution: 1280×720 (HD 720p)  
- FPS: 15-20
- Single tripwire at main detection point

**🎥 High-Quality Recording**
- Resolution: 3840×2160 (4K UHD)
- FPS: 30
- Note: Requires powerful hardware

---

## 📖 Usage Guide

### **👤 Employee Management**

#### **Add New Employee**
1. Go to **Admin** → **Employee Management**
2. Click **"Add Employee"**
3. Fill in employee details:
   - Employee ID (unique)
   - Full Name
   - Department
   - Job Role  
   - Date Joined
   - Email & Phone (optional)
4. Click **"Save"**

#### **Enroll Employee Face**
1. In Employee Management, click **"Enroll Face"** for an employee
2. **Live Enrollment**: Use webcam to capture face in real-time
3. **Upload Photo**: Upload a clear face photo
4. System processes and stores face encoding automatically
5. Employee can now be recognized by any camera

### **📊 Attendance Tracking**

#### **Automatic Check-in/Check-out**
- Employees simply walk past any active camera
- System automatically detects and logs attendance
- No manual interaction required
- Duplicate entries within 5 minutes are filtered

#### **View Attendance Records**
1. Go to **Admin** → **Attendance Records**
2. Filter by:
   - Date range
   - Employee
   - Department
   - Camera location
3. Export reports in CSV/Excel format

#### **Live Monitoring**
1. Go to **Admin** → **Live Monitor**
2. View real-time camera feeds
3. See live face detection and recognition
4. Switch between multiple cameras
5. Monitor system performance

### **🎛️ Super Admin Functions**

#### **User Management**
1. Go to **Super Admin** → **User Management**
2. Create admin accounts:
   - Set username and password
   - Assign roles (Admin/Super Admin)
   - Link to employee records
3. Manage user permissions and access

#### **System Control**
1. **Start/Stop FTS**: Control Face Tracking System
2. **Auto-Detect Cameras**: Scan for new cameras
3. **View System Status**: Monitor performance metrics
4. **Database Management**: Backup and maintenance

#### **Camera Discovery**
1. **Network Scanning**: Discover IP cameras on network
2. **ONVIF Detection**: Auto-configure ONVIF cameras
3. **Manual Addition**: Add cameras with custom URLs

---

## 🔧 Troubleshooting

### **🚫 Common Issues**

#### **Database Connection Failed**
```bash
# Check PostgreSQL service status
# Windows:
sc query postgresql-x64-13

# Linux:
sudo systemctl status postgresql

# Restart if needed:
# Windows: Services → PostgreSQL → Restart
# Linux:
sudo systemctl restart postgresql
```

#### **Camera Not Detected**
1. **USB Cameras**:
   - Check physical connection
   - Try different USB ports
   - Install camera drivers
   - Close other applications using camera

2. **Network Cameras**:
   - Verify network connectivity: `ping camera_ip`
   - Check camera credentials
   - Ensure ONVIF is enabled on camera
   - Check firewall settings

3. **Permission Issues (Linux)**:
```bash
# Add user to video group
sudo usermod -a -G video $USER
# Logout and login again
```

#### **Poor Performance**
1. **Lower Camera Settings**:
   - Reduce resolution (4K → 1080p → 720p)
   - Lower FPS (60 → 30 → 15)
   - Disable unused cameras

2. **System Optimization**:
```bash
# Check system resources
# Windows: Task Manager
# Linux:
htop
# or
top
```

3. **Memory Issues**:
```bash
# Run memory cleanup script
python fix_memory_and_ports.py
```

#### **Frontend Not Loading**
```bash
# Check if backend is running
curl http://localhost:8000/health

# Rebuild frontend
cd frontend
npm install
npm run build
cd ..

# Clear browser cache or try incognito mode
```

#### **Face Recognition Not Working**
1. **Check Face Enrollment**:
   - Ensure employees have enrolled faces
   - Verify face encoding files exist
   - Re-enroll if face data corrupted

2. **Camera Quality**:
   - Ensure good lighting
   - Check camera focus and position
   - Verify resolution settings

3. **Detection Thresholds**:
   - Adjust in `.env` file:
   ```
   FACE_DETECTION_THRESHOLD=0.4  # Lower = more sensitive
   FACE_RECOGNITION_THRESHOLD=0.5 # Lower = more lenient
   ```

### **📝 Log Files**
Check application logs for detailed error information:

```bash
# Windows
type logs\app.log
type logs\fts.log

# Linux  
cat logs/app.log
cat logs/fts.log

# Real-time monitoring (Linux)
tail -f logs/app.log
```

### **🔄 Reset System**
If you need to completely reset the system:

```bash
# 1. Stop all services
# Kill any running processes

# 2. Reset database
psql -U postgres -h localhost
DROP DATABASE face_recognition_db;
CREATE DATABASE face_recognition_db;
GRANT ALL PRIVILEGES ON DATABASE face_recognition_db TO facerecog_user;
\q

# 3. Reinitialize
python -c "
from db.db_manager import DatabaseManager
db = DatabaseManager()
db.init_database()
"

# 4. Restart system
python start_unified_server.py --enable-fts
```

---

## ⚡ Performance Optimization

### **🏃 Speed Improvements**

#### **Hardware Optimization**
1. **GPU Acceleration** (NVIDIA):
```bash
# Install CUDA toolkit from NVIDIA
# Install GPU-accelerated packages
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

2. **CPU Optimization**:
   - Set CPU affinity for FTS process
   - Use all available cores: Set `NUM_WORKERS=8` in `.env`
   - Close unnecessary applications

#### **Camera Settings for Performance**
- **Multiple Cameras**: Use 720p @ 30 FPS
- **Single Camera**: Use 1080p @ 30-60 FPS  
- **Low-Power Systems**: Use 720p @ 15 FPS
- **High-End Systems**: Use 4K @ 30 FPS

#### **Database Optimization**
```sql
-- Add indexes for better query performance
-- Connect to database and run:
CREATE INDEX idx_attendance_employee_id ON attendance(employee_id);
CREATE INDEX idx_attendance_timestamp ON attendance(timestamp);
CREATE INDEX idx_employees_employee_id ON employees(employee_id);
```

#### **Memory Management**
```bash
# Adjust memory settings in .env
GPU_MEMORY_FRACTION=0.6  # Use 60% of GPU memory
BATCH_SIZE=1            # Process 1 frame at a time
MAX_CAMERAS=8           # Limit concurrent cameras

# For systems with >16GB RAM
BATCH_SIZE=4
MAX_CAMERAS=16
```

### **📊 Monitoring Performance**
1. **System Monitor**: Go to Super Admin → System Status
2. **Camera Performance**: Check FPS and detection rates per camera
3. **Database Performance**: Monitor query times in logs
4. **Resource Usage**: Monitor CPU, RAM, and GPU usage

---

## 🏭 Production Deployment

### **🔒 Security Hardening**

#### **1. Change Default Passwords**
```bash
# Update .env file
SECRET_KEY=your-production-secret-key-very-long-and-secure
JWT_SECRET_KEY=another-production-jwt-key-very-long-and-secure

# Change default admin password immediately after first login
```

#### **2. Database Security**
```sql
-- Create production database user with limited privileges
CREATE USER prod_user WITH PASSWORD 'very_secure_production_password';
GRANT CONNECT ON DATABASE face_recognition_db TO prod_user;
GRANT USAGE ON SCHEMA public TO prod_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO prod_user;
```

#### **3. Network Security**
```bash
# Configure firewall (Linux)
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP  
sudo ufw allow 443   # HTTPS
sudo ufw allow 8000  # Backend (internal only)
sudo ufw enable

# Windows: Configure Windows Firewall to allow only necessary ports
```

#### **4. SSL/HTTPS Setup** (Recommended)
```bash
# Install nginx as reverse proxy
# Ubuntu/Debian:
sudo apt install nginx certbot python3-certbot-nginx

# Configure nginx for SSL termination
# Example nginx config in /etc/nginx/sites-available/face-recognition
```

### **🚀 Production Configuration**

#### **Environment Variables (.env)**
```bash
# Production Settings
DEBUG=False
LOG_LEVEL=WARNING
BACKEND_PORT=8000
FRONTEND_PORT=3000

# Database (Production)
DATABASE_URL=postgresql://prod_user:secure_password@localhost:5432/face_recognition_db

# Security (Generate new keys!)
SECRET_KEY=very-long-production-secret-key-change-this
JWT_SECRET_KEY=very-long-jwt-secret-key-change-this
JWT_EXPIRE_MINUTES=30  # Shorter for production

# Performance
ENABLE_GPU=True
MAX_CAMERAS=16
NUM_WORKERS=8
```

#### **Systemd Service (Linux)**
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
sudo systemctl status face-recognition
```

#### **Windows Service**
Use NSSM (Non-Sucking Service Manager):
1. Download NSSM from [nssm.cc](https://nssm.cc/download)
2. Install service:
```cmd
nssm install FaceRecognition
# Path: C:\path\to\project\venv\Scripts\python.exe  
# Startup directory: C:\path\to\project
# Arguments: start_unified_server.py --enable-fts
```

### **📊 Production Monitoring**

#### **Log Management**
```bash
# Configure log rotation (Linux)
sudo nano /etc/logrotate.d/face-recognition

# Add:
/opt/face-recognition-system/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 facerecog facerecog
}
```

#### **Backup Strategy**
```bash
# Daily database backup script
#!/bin/bash
BACKUP_DIR="/backup/face-recognition"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup
pg_dump -U prod_user -h localhost face_recognition_db > "$BACKUP_DIR/db_backup_$DATE.sql"

# Keep only last 30 days
find "$BACKUP_DIR" -name "db_backup_*.sql" -mtime +30 -delete

# Backup face encodings
tar -czf "$BACKUP_DIR/faces_backup_$DATE.tar.gz" face_encodings/
```

#### **Health Monitoring**
```bash
# Create health check script
#!/bin/bash
# Check if API is responding
curl -f http://localhost:8000/health || exit 1

# Check if FTS is running  
pgrep -f "start_unified_server" || exit 1

# Check database connection
python -c "
from db.db_manager import DatabaseManager
try:
    db = DatabaseManager()
    db.get_connection()
    print('Database OK')
except:
    exit(1)
"
```

---

## 📚 API Documentation

### **🔗 API Endpoints**

**Base URL**: `http://localhost:8000`

#### **Authentication**
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
  "token_type": "bearer"
}
```

#### **Employee Management**
```bash
# Get all employees
GET /employees/

# Create employee
POST /employees/
{
  "employee_id": "EMP001",
  "name": "John Doe", 
  "department_id": 1,
  "role": "Software Engineer",
  "date_joined": "2024-01-01"
}

# Enroll face
POST /employees/{employee_id}/enroll-face
# (multipart/form-data with image file)
```

#### **Camera Management**
```bash
# Get all cameras
GET /cameras/

# Auto-detect cameras
POST /cameras/auto-detect

# Update camera settings
PUT /cameras/{camera_id}/settings
{
  "camera_name": "Main Entrance",
  "resolution_width": 1920,
  "resolution_height": 1080,
  "fps": 30,
  "is_active": true
}
```

#### **System Control**
```bash
# Start FTS
POST /system/start

# Stop FTS  
POST /system/stop

# Get system status
GET /system/status
```

#### **Attendance**
```bash
# Get attendance records
GET /attendance/?start_date=2024-01-01&end_date=2024-01-31

# Manual attendance entry
POST /attendance/
{
  "employee_id": "EMP001",
  "action": "check_in",
  "camera_id": 1
}
```

### **📖 Interactive API Documentation**
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🤝 Support & Maintenance

### **📞 Getting Help**

1. **Check Logs**: Always check log files first
2. **System Status**: Use Super Admin → System Status
3. **Documentation**: Refer to this README
4. **Database**: Verify PostgreSQL is running
5. **Permissions**: Check file and camera permissions

### **🔄 Regular Maintenance**

#### **Weekly Tasks**
- Check log files for errors
- Verify database backup integrity  
- Monitor system performance
- Review attendance accuracy

#### **Monthly Tasks**
- Update system packages: `pip install -r requirements.txt --upgrade`
- Clean old log files
- Verify face encoding integrity
- Performance optimization review

#### **Quarterly Tasks**
- Full system backup
- Security audit and password updates
- Hardware performance review
- Database optimization and cleanup

---

## 📝 License & Credits

This Face Recognition Attendance System is built with:
- **FastAPI** - Modern Python web framework
- **React** - Frontend user interface
- **InsightFace** - Face recognition AI models
- **PostgreSQL** - Robust database system
- **OpenCV** - Computer vision library

---

**🎉 Congratulations!** Your Face Recognition Attendance System is now ready for production use. The system provides enterprise-grade face recognition with automatic camera management, making attendance tracking effortless and accurate.

For any issues or questions, please check the troubleshooting section or refer to the API documentation at `http://localhost:8000/docs`.