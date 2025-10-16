# ChaoticNexus - Quick Start

## 🎯 First Time Setup

```bash
# Clone from GitHub
git clone https://github.com/Harleyd77/ChaoticNexus.git
cd ChaoticNexus

# Setup environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r app/requirements.txt

# Create local config
cp .env .env.local
# Edit .env.local: set DATABASE_URL=sqlite:///./storage/app.db
```

## 🚀 Daily Usage

```bash
# Start work (pull latest changes)
cd /path/to/ChaoticNexus
git pull origin main

# Run the app
./run_dev.sh

# Access at: http://localhost:5000
```

## 💾 End of Day (save & sync)

```bash
git status                           # See what changed
git add .                            # Stage changes
git commit -m "What you did today"   # Commit
git push origin main                 # Push to GitHub
```

## 📍 Locations

- **GitHub:** https://github.com/Harleyd77/ChaoticNexus.git
- **This PC (WSL):** `/mnt/c/Users/user/Documents/GitHub/ChaoticNexus`
- **This PC (Windows):** `C:\Users\user\Documents\GitHub\ChaoticNexus`

## 🆘 Troubleshooting

```bash
# Virtual env not working?
rm -rf .venv && python3 -m venv .venv
source .venv/bin/activate
pip install -r app/requirements.txt

# Git conflicts?
git stash        # Save your work
git pull         # Get latest
git stash pop    # Reapply your work
```

---

📚 **Full guide:** See `SETUP_GUIDE.md`
