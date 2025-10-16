# ChaoticNexus - New Computer Setup Checklist

## ✅ First Time Setup on a New Computer

Follow these steps in order:

### Step 1: Install Prerequisites ✋
```bash
# Verify you have:
git --version          # Git (for cloning)
python3 --version      # Python 3.10+ (or python --version on Windows)

# If missing, install:
# - Git: https://git-scm.com/downloads
# - Python: https://www.python.org/downloads/
```

### Step 2: Clone the Repository 📥
```bash
# Navigate to where you want the project
cd ~/Documents/GitHub  # Linux/Mac/WSL
# OR
cd C:\Users\YourName\Documents\GitHub  # Windows

# Clone from GitHub
git clone https://github.com/Harleyd77/ChaoticNexus.git

# Enter the directory
cd ChaoticNexus
```

**✅ At this point, ALL files from GitHub are downloaded, including:**
- All code files
- Documentation (SETUP_GUIDE.md, QUICK_START.md, etc.)
- Workspace configuration (ChaoticNexus.code-workspace)
- Database migrations
- Everything!

### Step 3: Create Virtual Environment 🐍
```bash
# Linux/Mac/WSL:
python3 -m venv .venv
source .venv/bin/activate

# Windows (PowerShell):
python -m venv .venv
.venv\Scripts\activate

# Windows (CMD):
python -m venv .venv
.venv\Scripts\activate.bat
```

### Step 4: Install Dependencies 📦
```bash
# Make sure venv is activated (you should see (.venv) in prompt)
pip install --upgrade pip
pip install -r app/requirements.txt

# Wait for installation to complete...
```

### Step 5: Create Local Configuration 🔧
```bash
# Linux/Mac/WSL:
cat > .env.local << 'ENVEOF'
FLASK_ENV=development
DATABASE_URL=sqlite:///./storage/dev.db
SECRET_KEY=dev-secret-key
HOST=0.0.0.0
PORT=5000
FLASK_DEBUG=1
RUN_MIGRATIONS=1
PYTHONUNBUFFERED=1
ENVEOF

# Windows (PowerShell):
@"
FLASK_ENV=development
DATABASE_URL=sqlite:///./storage/dev.db
SECRET_KEY=dev-secret-key
HOST=0.0.0.0
PORT=5000
FLASK_DEBUG=1
RUN_MIGRATIONS=1
PYTHONUNBUFFERED=1
"@ | Out-File -FilePath .env.local -Encoding utf8

# Windows (manually):
# Just copy the content above into a file named .env.local
```

### Step 6: Initialize Database 🗄️
```bash
# Create storage directory
mkdir -p storage  # Linux/Mac/WSL
# OR
mkdir storage     # Windows

# Set Flask app
export FLASK_APP=app.wsgi:app  # Linux/Mac/WSL
# OR
$env:FLASK_APP = "app.wsgi:app"  # Windows PowerShell

# Run migrations to create database
flask db upgrade
```

### Step 7: Open Workspace in Cursor 🎯
```bash
# Option A: Command line
cursor ChaoticNexus.code-workspace

# Option B: In Cursor
# File → Open Workspace from File
# Navigate to: ChaoticNexus.code-workspace
# Click Open
```

### Step 8: Verify Everything Works ✅
```bash
# Test the app
# Linux/Mac/WSL:
./run_dev.sh

# Windows:
# Activate venv, then:
python -m flask run --host=0.0.0.0 --port=5000 --debug

# Visit: http://localhost:5000
# You should see the app running!
```

---

## 📋 What You Get Automatically from GitHub

When you clone, you get:

✅ **All Code Files**
- Python application code
- HTML templates  
- CSS/JavaScript
- Static assets

✅ **All Documentation**
- SETUP_GUIDE.md
- QUICK_START.md
- UBUNTU_PRODUCTION_SETUP.md
- PLATFORM_GUIDE.md
- DATABASE_SETUP_RECOMMENDATION.md
- COMPUTER_ROLES.md
- This checklist!

✅ **Configuration Files**
- ChaoticNexus.code-workspace (Cursor settings)
- .gitignore (what NOT to sync)
- requirements.txt (Python dependencies)
- Database migration files

✅ **Scripts**
- run_dev.sh (run script for Linux/Mac/WSL)

---

## ❌ What You DON'T Get (Must Create Locally)

These are intentionally NOT on GitHub:

❌ **.venv/** - Virtual environment (create with `python -m venv .venv`)
❌ **.env.local** - Local config (create from Step 5 above)
❌ **storage/dev.db** - Database (created when you run migrations)
❌ **__pycache__/** - Python cache (created automatically)

**Why?** These are specific to each computer and shouldn't be shared.

---

## 🔄 After Initial Setup - Daily Use

Once set up, your daily workflow is simple:

### Starting Work:
```bash
cd /path/to/ChaoticNexus
git pull origin main              # Get latest code
source .venv/bin/activate         # Activate venv
cursor ChaoticNexus.code-workspace  # Open workspace
```

### Working:
- Edit files in Cursor
- Test with `./run_dev.sh` or `flask run`
- Make changes, test, repeat

### Ending Work:
```bash
git add .
git commit -m "What you changed"
git push origin main
```

---

## 🆘 Quick Troubleshooting

### "cursor: command not found"
→ Open Cursor manually, then: File → Open Workspace from File

### "python: command not found"  
→ Try `python3` instead, or install Python

### "ModuleNotFoundError"
→ Activate venv and run: `pip install -r app/requirements.txt`

### "Database error"
→ Run migrations: `flask db upgrade`

### ".env.local not found"
→ Create it using Step 5 above

### Different data than other computers
→ This is normal! Each computer has its own test data

---

## ⏱️ Time Estimate

- First time setup: **5-10 minutes**
- Daily startup: **30 seconds**

---

## 🎯 Summary

1. ✅ Clone repository (gets everything from GitHub)
2. ✅ Create virtual environment (local only)
3. ✅ Install dependencies (local only)
4. ✅ Create .env.local (local only)
5. ✅ Initialize database (local only)
6. ✅ Open workspace (workspace file from GitHub!)
7. ✅ Start coding!

**The workspace file and all docs ARE on GitHub!**  
**But you need to do the setup steps first.**

---

## 📞 Need Help?

Refer to:
- **SETUP_GUIDE.md** - Detailed multi-computer guide
- **QUICK_START.md** - Quick reference
- **PLATFORM_GUIDE.md** - Platform-specific instructions
