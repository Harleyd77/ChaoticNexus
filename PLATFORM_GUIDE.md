# ChaoticNexus - Cross-Platform Guide

## 🖥️ Running on Different Systems

### Windows (Native - No WSL)

```powershell
# Open PowerShell in project folder
cd C:\Users\user\Documents\GitHub\ChaoticNexus

# Create virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\activate

# Install dependencies
pip install -r app/requirements.txt

# Create local config
copy .env .env.local
# Edit .env.local to set: DATABASE_URL=sqlite:///./storage/app.db

# Run the app
$env:FLASK_APP = "app.wsgi:app"
python -m flask run --host=0.0.0.0 --port=5000 --debug
```

### WSL / Linux

```bash
cd /path/to/ChaoticNexus
python3 -m venv .venv
source .venv/bin/activate
pip install -r app/requirements.txt
cp .env .env.local
# Edit .env.local
./run_dev.sh  # Or use flask run
```

### Mac

```bash
cd /path/to/ChaoticNexus
python3 -m venv .venv
source .venv/bin/activate
pip install -r app/requirements.txt
cp .env .env.local
# Edit .env.local
./run_dev.sh  # Or use flask run
```

## 🗄️ Database Strategies

### Option 1: Local Databases (Current Setup - RECOMMENDED FOR DEVELOPMENT)

**How it works:**
- Each computer has its own SQLite database
- Database files are NOT synced via Git (in .gitignore)
- Perfect for testing without affecting others

**Configuration (.env.local on each computer):**
```
DATABASE_URL=sqlite:///./storage/app.db
```

**Pros:**
✅ Fast and simple
✅ No network required
✅ Can't break production
✅ Test freely without affecting others

**Cons:**
❌ Each computer has different data
❌ Have to recreate test data on each machine

### Option 2: Shared Production Database (PostgreSQL)

**How it works:**
- One central database server (your main computer or cloud)
- All computers connect to the same database
- Real-time sync across all computers

**Configuration (.env.local - all computers point to same server):**
```
# Connect to shared PostgreSQL database
DATABASE_URL=postgresql+psycopg://username:password@server-ip:5432/chaoticnexus
```

**Pros:**
✅ Everyone sees same data
✅ No data duplication
✅ True production environment

**Cons:**
❌ Need network access to database server
❌ Testing can affect production data
❌ More complex setup

### Option 3: Hybrid Approach (BEST FOR YOUR WORKFLOW)

**Recommended Setup:**

#### Main Computer (Production)
```
# .env.local
DATABASE_URL=postgresql+psycopg://appuser:password@localhost:5432/chaoticnexus_production
FLASK_ENV=production
```

#### Development Computers (Testing)
```
# .env.local - Option A: Local SQLite
DATABASE_URL=sqlite:///./storage/app_dev.db
FLASK_ENV=development

# OR Option B: Connect to production (read-only testing)
DATABASE_URL=postgresql+psycopg://readonly_user:password@main-computer-ip:5432/chaoticnexus_production
FLASK_ENV=development
```

#### Testing Computer (Separate Test Database)
```
# .env.local
DATABASE_URL=postgresql+psycopg://appuser:password@main-computer-ip:5432/chaoticnexus_test
FLASK_ENV=development
```

## 🎯 Recommended Workflow

### Development Flow:

```
┌─────────────────┐
│  Main Computer  │  ← Production Database (PostgreSQL)
│  (Production)   │     Final, live data
└─────────────────┘
         ↑
         │ Push tested code
         │
┌─────────────────┐
│   Dev Computer  │  ← Local SQLite Database
│    (Testing)    │     Test changes safely
└─────────────────┘
         ↑
         │ Pull latest code
         │
┌─────────────────┐
│ Other Computer  │  ← Local SQLite Database
│   (Editing)     │     Edit & experiment
└─────────────────┘
```

### Daily Workflow:

**On Dev/Test Computers:**
1. Pull latest code from GitHub
2. Work with local SQLite database
3. Test your changes
4. Push code (not database) to GitHub
5. Have main computer pull & update

**On Main Computer:**
1. Pull tested code from GitHub
2. Review changes
3. Run with production database
4. Deploy updates

## 🔧 Setting Up PostgreSQL (Main Computer)

If you want a shared production database:

### On Windows (Main Computer):

```powershell
# Install PostgreSQL
# Download from: https://www.postgresql.org/download/windows/

# Or use Docker:
docker run --name chaoticnexus-db `
  -e POSTGRES_USER=appuser `
  -e POSTGRES_PASSWORD=yourpassword `
  -e POSTGRES_DB=chaoticnexus `
  -p 5432:5432 `
  -v chaoticnexus-data:/var/lib/postgresql/data `
  -d postgres:15
```

### On Linux/WSL (Main Computer):

```bash
# Install PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE chaoticnexus;
CREATE USER appuser WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE chaoticnexus TO appuser;
\q
```

## 🌐 Network Access

To allow other computers to access your main database:

### PostgreSQL Configuration:
Edit `postgresql.conf`:
```
listen_addresses = '*'  # Allow connections from any IP
```

Edit `pg_hba.conf`:
```
host    all    all    0.0.0.0/0    md5  # Allow password auth from any IP
```

**Security Note:** In production, restrict to specific IPs!

## 📊 Database Migration Strategy

### When you make database changes:

1. **Create migration on dev computer:**
   ```bash
   flask db migrate -m "Description of changes"
   git add migrations/
   git commit -m "Add database migration"
   git push
   ```

2. **Apply on main computer:**
   ```bash
   git pull
   flask db upgrade  # Applies migrations to production DB
   ```

3. **Other computers pull automatically:**
   ```bash
   git pull
   flask db upgrade  # Updates their local DB
   ```

## 💾 Data Sync Options

### Option 1: Export/Import Test Data

```bash
# Export from main computer
flask export-data > test_data.json

# Commit to git (if not sensitive)
git add test_data.json
git commit -m "Update test data"
git push

# Import on dev computers
git pull
flask import-data < test_data.json
```

### Option 2: Database Backup/Restore

```bash
# Backup production
pg_dump chaoticnexus > backup.sql

# Restore to test database
psql chaoticnexus_test < backup.sql
```

### Option 3: Keep Separate

Just use different data on each computer - often best for development!

## 🎯 Quick Decision Guide

**Choose Local SQLite if:**
- You want simple setup
- You're editing/testing code
- You don't need shared data
- You're offline frequently

**Choose Shared PostgreSQL if:**
- Multiple people need same data
- You're running production
- You need real-time collaboration
- You have reliable network

**Choose Hybrid if:**
- You want both flexibility and production environment
- Different computers serve different purposes
- You want to test safely while having production data available
