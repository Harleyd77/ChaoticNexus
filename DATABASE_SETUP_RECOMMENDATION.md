# ChaoticNexus - Recommended Database Setup

## 🎯 Your Workflow (Based on Requirements)

You have:
- **Main Computer**: Final production database
- **Other Computers**: Edit code, test changes

## ✅ Recommended Configuration

### 1️⃣ Main Computer (This PC - Production)

**Purpose:** Run production with real data

**.env.local:**
```bash
FLASK_ENV=production
DATABASE_URL=sqlite:///./storage/production.db
# Or PostgreSQL for production:
# DATABASE_URL=postgresql+psycopg://appuser:password@localhost:5432/chaoticnexus
SECRET_KEY=your-secure-production-key
HOST=0.0.0.0
PORT=5000
```

**Usage:**
- Pull tested code from GitHub
- Run with production database
- Real customer data lives here
- Deploy from here

### 2️⃣ Other Computers (Development/Testing)

**Purpose:** Edit code, test safely

**.env.local:**
```bash
FLASK_ENV=development
DATABASE_URL=sqlite:///./storage/dev.db
SECRET_KEY=dev-secret-key
HOST=0.0.0.0
PORT=5000
FLASK_DEBUG=1
```

**Usage:**
- Pull latest code from GitHub
- Local SQLite with test data
- Make changes, test freely
- Push code (not database) to GitHub
- Can't accidentally break production

## 📋 Step-by-Step Setup

### On THIS Computer (Main - WSL):

```bash
cd /mnt/c/Users/user/Documents/GitHub/ChaoticNexus

# Edit .env.local
cat > .env.local << 'ENVEOF'
FLASK_ENV=production
DATABASE_URL=sqlite:///./storage/production.db
SECRET_KEY=change-to-secure-key-for-production
HOST=0.0.0.0
PORT=5000
RUN_MIGRATIONS=1
ENVEOF

# Create storage directory
mkdir -p storage

# Initialize production database
source .venv/bin/activate
export FLASK_APP=app.wsgi:app
flask db upgrade

echo "✅ Main computer (production) configured!"
```

### On Other Computers:

```bash
# Clone the repository
git clone https://github.com/Harleyd77/ChaoticNexus.git
cd ChaoticNexus

# Create virtual environment
python3 -m venv .venv        # Linux/Mac/WSL
# OR
python -m venv .venv         # Windows

# Activate
source .venv/bin/activate    # Linux/Mac/WSL
# OR
.venv\Scripts\activate       # Windows

# Install dependencies
pip install -r app/requirements.txt

# Create dev config
cat > .env.local << 'ENVEOF'
FLASK_ENV=development
DATABASE_URL=sqlite:///./storage/dev.db
SECRET_KEY=dev-secret-key
HOST=0.0.0.0
PORT=5000
FLASK_DEBUG=1
RUN_MIGRATIONS=1
ENVEOF

# Create storage and initialize dev database
mkdir -p storage
export FLASK_APP=app.wsgi:app  # Linux/Mac/WSL
# OR
$env:FLASK_APP = "app.wsgi:app"  # Windows

flask db upgrade

echo "✅ Development computer configured!"
```

## 🔄 Daily Workflow

### On Development Computers:

```bash
# Morning: Pull latest code
git pull origin main

# Work: Edit files in Cursor
# ... make changes ...

# Test: Run locally with dev database
./run_dev.sh  # or flask run

# Done: Push code changes
git add .
git commit -m "Description of changes"
git push origin main
```

### On Main Computer:

```bash
# Pull tested changes
git pull origin main

# Apply any database migrations
flask db upgrade

# Run with production database
./run_dev.sh  # or your production command
```

## 🗄️ Database Files Explained

```
ChaoticNexus/
├── storage/
│   ├── production.db     ← Main computer only (NOT in git)
│   ├── dev.db           ← Dev computers only (NOT in git)
│   └── uploads/         ← Shared files (optional in git)
├── .env.local           ← Different on each computer (NOT in git)
└── migrations/          ← Database schema (IN git, shared)
```

## 🔐 What Gets Synced via Git

✅ **Synced (in Git):**
- Python code (`app/`, `tests/`)
- Database schema (`migrations/`)
- HTML templates
- Static files (CSS, JS)
- Documentation
- Workspace configuration

❌ **NOT Synced (in .gitignore):**
- Database files (`storage/*.db`)
- Virtual environment (`.venv/`)
- Local config (`.env.local`)
- Python cache (`__pycache__/`)
- User uploads (optional)

## 🚀 Advantages of This Setup

### For You:
✅ **Safe Testing**: Can't accidentally break production  
✅ **Fast Development**: No network dependency  
✅ **Simple Setup**: SQLite = no database server needed  
✅ **Flexible**: Work offline on dev computers  
✅ **Clear Separation**: Production data separate from test data  

### Workflow:
1. **Dev computer**: Edit code → Test locally → Push to GitHub
2. **Main computer**: Pull from GitHub → Review → Run in production
3. **Other computers**: Always pull latest before starting work

## 🔄 Sharing Test Data (Optional)

If you want same test data on all dev computers:

### Create Test Data Script:

```python
# tools/create_test_data.py
from app import create_app
from app.models import db, User, Customer, Job

def seed_test_data():
    app = create_app()
    with app.app_context():
        # Clear existing
        db.drop_all()
        db.create_all()
        
        # Create test data
        user = User(username='admin', email='admin@test.com')
        user.set_password('admin123')
        db.session.add(user)
        
        customer = Customer(name='Test Customer', email='test@test.com')
        db.session.add(customer)
        
        db.session.commit()
        print("✅ Test data created!")

if __name__ == '__main__':
    seed_test_data()
```

Run on any dev computer:
```bash
python tools/create_test_data.py
```

## 💡 When to Upgrade to PostgreSQL

Stay with SQLite until you need:
- Multiple simultaneous users
- More than ~100GB of data
- Advanced database features
- High concurrent writes

For your workflow: **SQLite is perfect!**

## 🆘 Troubleshooting

### "Database is locked" error
→ SQLite can't handle multiple connections well  
→ Stop all other instances of the app

### Different data on each computer
→ This is normal and expected!  
→ Each computer has its own test data  
→ Only code/schema syncs via Git

### Migration conflicts
→ Always pull before creating migrations  
→ If conflicts, delete migration file and recreate

## 📞 Quick Reference

| Computer Type | Database | Config | Use Case |
|--------------|----------|--------|----------|
| Main (This PC) | `production.db` | Production | Live data, final updates |
| Dev Computer | `dev.db` | Development | Safe testing, experiments |
| Other Computer | `dev.db` | Development | Code editing, testing |

---

**Summary:** Code syncs via GitHub, databases stay local. Simple and safe! 🎉
