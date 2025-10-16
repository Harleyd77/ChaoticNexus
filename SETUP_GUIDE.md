# ChaoticNexus - Multi-Computer Setup Guide

This guide helps you access and work with ChaoticNexus from different computers and locations.

## 📍 Repository Location

**GitHub Repository:** `https://github.com/Harleyd77/ChaoticNexus.git`

**Current Local Path (This PC - WSL):** `/mnt/c/Users/user/Documents/GitHub/ChaoticNexus`

## 🖥️ Setting Up on a New Computer

### Option 1: Clone Fresh from GitHub

```bash
# Navigate to where you want the project
cd ~/Documents/GitHub  # or any location you prefer

# Clone the repository
git clone https://github.com/Harleyd77/ChaoticNexus.git

# Enter the directory
cd ChaoticNexus

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac/WSL
# OR
.venv\Scripts\activate     # Windows PowerShell

# Install dependencies
pip install -r app/requirements.txt

# Create local environment file
cp .env .env.local
# Edit .env.local to use SQLite for local development:
# DATABASE_URL=sqlite:///./storage/app.db
```

### Option 2: Using Existing Clone

If you already have the repository cloned but need to set it up:

```bash
cd /path/to/ChaoticNexus

# Pull latest changes
git pull origin main

# Remove old virtual environment if it exists
rm -rf .venv

# Create fresh virtual environment
python3 -m venv .venv

# Activate and install
source .venv/bin/activate
pip install -r app/requirements.txt
```

## 🔄 Syncing Between Computers

### Before Leaving One Computer

```bash
cd /path/to/ChaoticNexus

# Check what changed
git status

# Stage your changes
git add .

# Commit your changes
git commit -m "Description of what you changed"

# Push to GitHub
git push origin main
```

### When Arriving at Another Computer

```bash
cd /path/to/ChaoticNexus

# Pull latest changes from GitHub
git pull origin main

# Ensure virtual environment is activated
source .venv/bin/activate

# Install any new dependencies (if requirements changed)
pip install -r app/requirements.txt
```

## 🚀 Running the Application

### Linux/Mac/WSL

```bash
cd /path/to/ChaoticNexus
./run_dev.sh
```

Or manually:
```bash
source .venv/bin/activate
export $(grep -v '^#' .env.local | xargs)
export FLASK_APP=app.wsgi:app
python -m flask run --host=0.0.0.0 --port=5000 --debug
```

### Windows PowerShell

```powershell
cd C:\path\to\ChaoticNexus
.venv\Scripts\activate
$env:FLASK_APP = "app.wsgi:app"
# Set other environment variables from .env.local
python -m flask run --host=0.0.0.0 --port=5000 --debug
```

## 📂 Important Paths to Know

### Windows Path
- `C:\Users\user\Documents\GitHub\ChaoticNexus`

### WSL Path (on Windows)
- `/mnt/c/Users/user/Documents/GitHub/ChaoticNexus`

### Typical Linux/Mac Path
- `~/Documents/GitHub/ChaoticNexus`
- Or: `/home/username/Documents/GitHub/ChaoticNexus`

## 🔑 SSH Keys for GitHub

If you need to set up SSH keys on a new computer:

```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "harley@work"

# Display the public key
cat ~/.ssh/id_ed25519.pub

# Copy the output and add it to GitHub:
# GitHub.com → Settings → SSH and GPG keys → New SSH key
```

Then update your git remote to use SSH:
```bash
git remote set-url origin git@github.com:Harleyd77/ChaoticNexus.git
```

## 📝 Configuration Files

### `.env.local` - Local Development Settings
**Create this file on each computer** (not tracked by git):
```
FLASK_ENV=development
HOST=0.0.0.0
PORT=5000
PYTHONUNBUFFERED=1
SECRET_KEY=dev-secret-key-change-in-production
DATABASE_URL=sqlite:///./storage/app.db
RUN_MIGRATIONS=1
```

### `.env` - Production Settings
**Tracked by git** - used for Docker/production deployment with PostgreSQL

## 🗄️ Database Considerations

- **Local Development:** Uses SQLite (`./storage/app.db`)
- **Production:** Uses PostgreSQL (configured in `.env`)
- Each computer will have its own SQLite database
- Database files are NOT synced via git (they're in `.gitignore`)

## 🛠️ Troubleshooting

### Virtual Environment Issues
```bash
# If venv doesn't work, recreate it
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r app/requirements.txt
```

### Git Conflicts
```bash
# If you have conflicts when pulling
git status
git stash  # temporarily save your changes
git pull origin main
git stash pop  # reapply your changes
```

### Permission Issues in WSL
```bash
# If you get permission errors
chmod +x run_dev.sh
chmod +x app/build.sh
```

## 💡 Best Practices

1. **Always pull before starting work:** `git pull origin main`
2. **Commit and push regularly:** Don't let changes pile up
3. **Use descriptive commit messages:** Makes it easier to track changes
4. **Keep virtual environments separate:** Don't commit `.venv` to git
5. **Use `.env.local` for local settings:** Don't commit sensitive data

## 📱 Quick Reference

### Common Commands
```bash
# Status check
git status

# Pull latest
git pull origin main

# Push changes
git add .
git commit -m "Your message"
git push origin main

# Start app
./run_dev.sh

# Activate venv
source .venv/bin/activate  # Linux/Mac/WSL
.venv\Scripts\activate     # Windows
```

## 🔗 Useful URLs

- **GitHub Repo:** https://github.com/Harleyd77/ChaoticNexus
- **Local App:** http://localhost:5000
- **GitHub Docs:** https://docs.github.com

---

**Last Updated:** October 16, 2025  
**Primary Development Location:** `/mnt/c/Users/user/Documents/GitHub/ChaoticNexus` (WSL on Windows PC)
