# ChaoticNexus - Computer Roles & Workflow

## 🖥️ Your Computer Setup

```
┌─────────────────────────────────────────┐
│         Ubuntu PC (Production)          │
│  • Main production database             │
│  • Real customer data                   │
│  • Final updates deployed here          │
│  • Runs as systemd service              │
└─────────────────────────────────────────┘
                    ↑
                    │ Pull tested code
                    │
            ┌───────┴────────┐
            │    GitHub      │
            │  (Code Sync)   │
            └───────┬────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
        ↓                       ↓
┌───────────────────┐   ┌───────────────────┐
│  Windows + WSL    │   │ Other Computers   │
│    (Testing)      │   │  (Development)    │
│ • Test changes    │   │ • Edit code       │
│ • Local dev DB    │   │ • Local dev DB    │
│ • Safe testing    │   │ • Experiments     │
└───────────────────┘   └───────────────────┘
```

## 📋 Computer Roles

### 🎯 Ubuntu PC - PRODUCTION
**Location:** Separate Ubuntu computer  
**Purpose:** Production server with real data  
**Database:** `production.db` (SQLite) or PostgreSQL  
**Environment:** Production  

**What happens here:**
- Pull tested code from GitHub
- Run with production database
- Real customer data
- Deploy final updates
- Runs as system service

**Setup:** See `UBUNTU_PRODUCTION_SETUP.md`

---

### 🧪 Windows + WSL PC - TESTING
**Location:** This computer  
**Purpose:** Testing environment  
**Database:** `dev.db` (SQLite)  
**Environment:** Development  

**What happens here:**
- Edit and test code
- Local test database
- Safe testing - can't break production
- Push tested code to GitHub

**Current Path:** `/mnt/c/Users/user/Documents/GitHub/ChaoticNexus`

---

### 💻 Other Computers - DEVELOPMENT
**Location:** Various (laptop, work PC, etc.)  
**Purpose:** Code editing, experiments  
**Database:** `dev.db` (SQLite)  
**Environment:** Development  

**What happens here:**
- Clone from GitHub
- Edit code in Cursor
- Test locally
- Push changes to GitHub

---

## 🔄 Typical Workflow

### Daily Development Flow:

```
1. Testing/Dev Computer (This PC or Others):
   ├─ Pull latest code: git pull origin main
   ├─ Edit code in Cursor
   ├─ Test with local database
   ├─ Commit changes: git commit -m "description"
   └─ Push to GitHub: git push origin main

2. GitHub:
   └─ Code is now available for production

3. Ubuntu Production PC:
   ├─ Pull updates: git pull origin main
   ├─ Update dependencies: pip install -r app/requirements.txt
   ├─ Migrate database: flask db upgrade
   └─ Restart service: sudo systemctl restart chaoticnexus
```

### Safety Features:

✅ **Can't break production from testing computers**  
✅ **Each computer has its own database**  
✅ **Code syncs, data doesn't**  
✅ **Production only updates when you pull**  

## 📊 What Gets Synced

### ✅ Synced via GitHub
- Python code
- HTML templates
- CSS/JavaScript
- Database schema (migrations)
- Configuration files
- Documentation

### ❌ NOT Synced (local only)
- Database files (`.db`)
- Virtual environment (`.venv/`)
- Local config (`.env.local`)
- User uploads (optional)
- Logs

## 🎯 Quick Access

| Computer | Path | Config | Database |
|----------|------|--------|----------|
| **Ubuntu Production** | `~/Documents/GitHub/ChaoticNexus` | `.env.local` (production) | `production.db` |
| **Windows WSL Testing** | `/mnt/c/Users/user/Documents/GitHub/ChaoticNexus` | `.env.local` (development) | `dev.db` |
| **Other Dev Computers** | Varies | `.env.local` (development) | `dev.db` |

## 📚 Documentation by Computer

### For Ubuntu Production PC:
- 📖 **UBUNTU_PRODUCTION_SETUP.md** ← Start here
- 📖 SETUP_GUIDE.md
- 📖 QUICK_START.md

### For This Testing PC (WSL):
- 📖 SETUP_GUIDE.md
- 📖 QUICK_START.md
- 📖 PLATFORM_GUIDE.md
- 📖 DATABASE_SETUP_RECOMMENDATION.md

### For Other Dev Computers:
- 📖 SETUP_GUIDE.md
- 📖 QUICK_START.md
- 📖 PLATFORM_GUIDE.md

## 🔗 GitHub Repository

**URL:** https://github.com/Harleyd77/ChaoticNexus

All computers connect to this repository to sync code.

---

**Remember:** Code syncs everywhere, databases stay local! 🎯
