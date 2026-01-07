# 🚀 One-Command Startup Guide

You can now start ALL services (Frontend, Backend, Database) with a single command!

## 🎯 Quick Start Options

### **Option 1: Bash Script (Recommended for Mac/Linux)** ⭐

```bash
# First time setup
./start.sh

# Stop all services
./stop.sh
```

### **Option 2: NPM Scripts (Cross-platform)**

```bash
# First time: Install concurrently
npm install

# Start all services
npm run dev

# Alternative commands:
npm run setup          # One-time setup
npm run dev            # Start all services
npm run start:prod     # Production mode
```

### **Option 3: Makefile (Simple commands)**

```bash
# First time setup
make setup

# Start all services
make start

# Stop all services
make stop

# View logs
make logs

# Check status
make status
```

### **Option 4: Docker (Full containerization)**

```bash
# Build images
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## 📋 Detailed Instructions

### Method 1: Bash Script (./start.sh) ⭐ RECOMMENDED

**Advantages:**
- ✅ Simplest to use
- ✅ Auto-checks prerequisites
- ✅ Shows real-time status
- ✅ Creates logs automatically
- ✅ Saves process IDs for easy stopping

**Steps:**

```bash
# 1. First time only - make executable (already done)
chmod +x start.sh stop.sh

# 2. Configure environment (if not done)
# Edit backend/.env with your Supabase credentials
nano backend/.env

# 3. Start everything!
./start.sh

# The script will:
# ✓ Check prerequisites (Node, Python)
# ✓ Install dependencies if needed
# ✓ Clear ports 3000 and 8000
# ✓ Start backend on port 8000
# ✓ Start frontend on port 3000
# ✓ Show you all service URLs
# ✓ Save logs to logs/ directory

# 4. To stop everything:
./stop.sh
```

**View Logs:**
```bash
# All logs
tail -f logs/backend.log logs/frontend.log

# Backend only
tail -f logs/backend.log

# Frontend only
tail -f logs/frontend.log
```

---

### Method 2: NPM Scripts

**Advantages:**
- ✅ Cross-platform (Windows, Mac, Linux)
- ✅ Uses concurrently to run multiple processes
- ✅ Color-coded terminal output
- ✅ Easy to customize

**Steps:**

```bash
# 1. Install the root package.json
npm install

# This installs 'concurrently' for running multiple commands

# 2. One-time setup (if not done)
npm run setup

# 3. Start all services
npm run dev

# You'll see color-coded output:
# [DB]       - Cyan
# [BACKEND]  - Yellow
# [FRONTEND] - Green

# 4. Stop: Press Ctrl+C
```

**Available Scripts:**
```bash
npm run install:all    # Install all dependencies
npm run setup          # One-time setup
npm run dev            # Start all services (development)
npm run start:prod     # Start all services (production)
npm run build          # Build frontend
npm run test           # Run all tests
```

---

### Method 3: Makefile

**Advantages:**
- ✅ Simple commands
- ✅ Traditional Unix approach
- ✅ Self-documenting (make help)

**Steps:**

```bash
# 1. See all available commands
make help

# 2. First time setup
make setup

# 3. Start all services
make start
# or simply:
make dev

# 4. Stop all services
make stop

# 5. View logs
make logs

# 6. Check service status
make status

# 7. Clean everything
make clean
```

**All Makefile Commands:**
```bash
make help          # Show all commands
make install       # Install dependencies
make setup         # Complete setup
make start         # Start all services
make stop          # Stop all services
make dev           # Alias for start
make clean         # Clean build artifacts
make build         # Build frontend
make test          # Run tests
make logs          # View logs
make status        # Check service status
make docker-build  # Build Docker images
make docker-up     # Start with Docker
make docker-down   # Stop Docker services
```

---

### Method 4: Docker Compose

**Advantages:**
- ✅ Complete isolation
- ✅ Production-like environment
- ✅ Easy deployment
- ✅ Consistent across machines

**Steps:**

```bash
# 1. Create .env file in root
cat > .env << EOF
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_service_key
SECRET_KEY=your_secret_key
EOF

# 2. Build images (first time only)
docker-compose build

# 3. Start all services
docker-compose up -d

# Services will be available at:
# - Frontend: http://localhost:3000
# - Backend:  http://localhost:8000
# - Database: http://localhost:5432

# 4. View logs
docker-compose logs -f

# 5. Stop all services
docker-compose down

# 6. Stop and remove volumes
docker-compose down -v
```

---

## 🎯 Which Method Should I Use?

| Method | Best For | Difficulty |
|--------|----------|------------|
| **Bash Script** | Mac/Linux developers, quick start | ⭐ Easy |
| **NPM Scripts** | Cross-platform, familiar workflow | ⭐⭐ Easy |
| **Makefile** | Unix lovers, simple commands | ⭐⭐ Easy |
| **Docker** | Production-like, deployment | ⭐⭐⭐ Medium |

**Recommendation:** Start with **Bash Script** (`./start.sh`) for development!

---

## 📊 What Happens When You Start?

```
./start.sh
    │
    ├─→ Check Node.js ✓
    ├─→ Check Python ✓
    ├─→ Create venv (if needed)
    ├─→ Install dependencies (if needed)
    ├─→ Check .env files
    ├─→ Clear ports 3000, 8000
    │
    ├─→ START BACKEND (Port 8000)
    │   └─→ Load ML models
    │   └─→ Connect to Supabase
    │   └─→ Start FastAPI server
    │   └─→ Save PID to logs/backend.pid
    │
    ├─→ START FRONTEND (Port 3000)
    │   └─→ Start Next.js dev server
    │   └─→ Save PID to logs/frontend.pid
    │
    └─→ SHOW STATUS ✅
        Frontend:  http://localhost:3000
        Backend:   http://localhost:8000
        API Docs:  http://localhost:8000/docs
```

---

## 🔧 Configuration

### First Time Setup

1. **Backend Configuration:**
```bash
cd backend
cp .env.example .env
nano .env
```

Update with your Supabase credentials:
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your_service_role_key
SECRET_KEY=your_random_secret_key
```

2. **Frontend Configuration** (already set):
```bash
cd frontend
# .env.local is already configured
```

### Changing Ports

Edit the scripts if you need different ports:

**Bash Script:**
```bash
nano start.sh
# Change ports in the script
```

**NPM Scripts:**
```bash
nano package.json
# Modify the dev:backend and dev:frontend scripts
```

**Docker:**
```bash
nano docker-compose.yml
# Change the ports mapping
```

---

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Kill process on port 3000
lsof -ti :3000 | xargs kill -9

# Kill process on port 8000
lsof -ti :8000 | xargs kill -9

# Or use the stop script
./stop.sh
```

### Backend Won't Start

```bash
# Check logs
tail -f logs/backend.log

# Verify Python environment
cd backend
source venv/bin/activate
python --version
pip list

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Frontend Won't Start

```bash
# Check logs
tail -f logs/frontend.log

# Clear cache and reinstall
cd frontend
rm -rf .next node_modules
npm install
```

### Database Connection Issues

```bash
# Check Supabase credentials
cat backend/.env | grep SUPABASE

# Test connection
cd backend
source venv/bin/activate
python -c "from database.client import db; print(db.client)"
```

---

## 📝 Logs Location

```
logs/
├── backend.log     # Backend API logs
├── frontend.log    # Frontend Next.js logs
├── backend.pid     # Backend process ID
└── frontend.pid    # Frontend process ID
```

---

## 🎉 Success!

After running any of the startup methods, you should see:

✅ **Frontend running at:** http://localhost:3000  
✅ **Backend API at:** http://localhost:8000  
✅ **API Documentation:** http://localhost:8000/docs  

**Login with:**
- Email: `officer@example.com`
- Password: `password123`

---

## 💡 Pro Tips

1. **Always stop properly:**
   ```bash
   ./stop.sh  # Don't just Ctrl+C
   ```

2. **Check status anytime:**
   ```bash
   make status
   ```

3. **View logs in real-time:**
   ```bash
   tail -f logs/*.log
   ```

4. **Quick restart:**
   ```bash
   ./stop.sh && ./start.sh
   ```

5. **Clean build:**
   ```bash
   make clean && make start
   ```

---

## 🚀 Now you can start everything with just ONE command!

Choose your preferred method and run it. No more juggling 3 terminals! 🎊
