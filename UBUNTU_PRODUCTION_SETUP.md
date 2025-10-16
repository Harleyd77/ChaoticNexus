# ChaoticNexus - Ubuntu Production Setup

## 🖥️ Computer Roles

- **Ubuntu PC** → **PRODUCTION** (Main database, final updates)
- **Windows WSL PC** → **TESTING** (Safe testing environment)
- **Other Computers** → **DEVELOPMENT** (Code editing, experiments)

## 🚀 Setting Up Ubuntu Production Machine

### 1. System Requirements

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.10+ and dependencies
sudo apt install -y python3 python3-pip python3-venv git

# Optional: Install PostgreSQL for production database
sudo apt install -y postgresql postgresql-contrib

# Verify Python version
python3 --version  # Should be 3.10 or higher
```

### 2. Clone Repository

```bash
# Navigate to desired location
cd ~
mkdir -p Documents/GitHub
cd Documents/GitHub

# Clone from GitHub
git clone https://github.com/Harleyd77/ChaoticNexus.git
cd ChaoticNexus
```

### 3. Set Up Virtual Environment

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r app/requirements.txt
```

### 4. Configure Production Environment

```bash
# Create production configuration
cat > .env.local << 'ENVEOF'
# Production Environment Configuration
FLASK_ENV=production
DATABASE_URL=sqlite:///./storage/production.db
SECRET_KEY=CHANGE-THIS-TO-SECURE-RANDOM-STRING
HOST=0.0.0.0
PORT=5000
RUN_MIGRATIONS=1
PYTHONUNBUFFERED=1

# Optional: Use PostgreSQL instead of SQLite
# DATABASE_URL=postgresql+psycopg://appuser:password@localhost:5432/chaoticnexus
ENVEOF

# Generate a secure secret key (recommended!)
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))" >> .env.local.new

echo "⚠️  IMPORTANT: Edit .env.local and set a secure SECRET_KEY!"
```

### 5. Initialize Database

```bash
# Create storage directory
mkdir -p storage

# Activate virtual environment
source .venv/bin/activate

# Set Flask app
export FLASK_APP=app.wsgi:app

# Run database migrations
flask db upgrade

echo "✅ Production database initialized!"
```

### 6. Create Production User

```bash
# Option 1: Using Flask CLI (if available)
flask create-admin

# Option 2: Using Python interactive shell
python3 << 'PYEOF'
from app import create_app
from app.models import db, User
from app.extensions import db

app = create_app()
with app.app_context():
    # Create admin user
    admin = User(username='admin', email='admin@example.com')
    admin.set_password('CHANGE_THIS_PASSWORD')
    db.session.add(admin)
    db.session.commit()
    print("✅ Admin user created!")
PYEOF
```

### 7. Set Up as System Service (Optional but Recommended)

```bash
# Create systemd service file
sudo nano /etc/systemd/system/chaoticnexus.service
```

Add this content:
```ini
[Unit]
Description=ChaoticNexus Flask Application
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/Documents/GitHub/ChaoticNexus
Environment="PATH=/home/YOUR_USERNAME/Documents/GitHub/ChaoticNexus/.venv/bin"
EnvironmentFile=/home/YOUR_USERNAME/Documents/GitHub/ChaoticNexus/.env.local
ExecStart=/home/YOUR_USERNAME/Documents/GitHub/ChaoticNexus/.venv/bin/gunicorn -c app/gunicorn.conf.py app.wsgi:app
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable chaoticnexus

# Start the service
sudo systemctl start chaoticnexus

# Check status
sudo systemctl status chaoticnexus
```

### 8. Set Up Nginx (Optional - for web serving)

```bash
# Install Nginx
sudo apt install -y nginx

# Create Nginx configuration
sudo nano /etc/nginx/sites-available/chaoticnexus
```

Add this content:
```nginx
server {
    listen 80;
    server_name your-domain.com;  # or use server IP

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /home/YOUR_USERNAME/Documents/GitHub/ChaoticNexus/app/static;
    }
}
```

Enable the site:
```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/chaoticnexus /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

## 🔄 Updating Production from Git

### Daily Update Workflow

```bash
# Navigate to project
cd ~/Documents/GitHub/ChaoticNexus

# Activate virtual environment
source .venv/bin/activate

# Pull latest changes from GitHub
git pull origin main

# Install any new dependencies
pip install -r app/requirements.txt

# Apply database migrations
export FLASK_APP=app.wsgi:app
flask db upgrade

# Restart the service
sudo systemctl restart chaoticnexus

echo "✅ Production updated!"
```

### Create Update Script

```bash
# Create update script
cat > update_production.sh << 'UPDATEEOF'
#!/bin/bash
set -e

echo "🔄 Updating ChaoticNexus Production..."

cd ~/Documents/GitHub/ChaoticNexus
source .venv/bin/activate

echo "📥 Pulling latest code..."
git pull origin main

echo "📦 Installing dependencies..."
pip install -r app/requirements.txt

echo "🗄️  Running database migrations..."
export FLASK_APP=app.wsgi:app
flask db upgrade

echo "♻️  Restarting service..."
sudo systemctl restart chaoticnexus

echo "✅ Production updated successfully!"
UPDATEEOF

# Make it executable
chmod +x update_production.sh

# Run updates with:
# ./update_production.sh
```

## 🔐 Security Recommendations

### 1. Secure Secret Key
```bash
# Generate secure key
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
# Add to .env.local
```

### 2. Firewall Configuration
```bash
# Allow SSH
sudo ufw allow ssh

# Allow HTTP (if using Nginx)
sudo ufw allow 80/tcp

# Allow HTTPS (if using SSL)
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable
```

### 3. Database Backups
```bash
# Create backup script
cat > backup_database.sh << 'BACKUPEOF'
#!/bin/bash
BACKUP_DIR=~/ChaoticNexus_backups
mkdir -p $BACKUP_DIR
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

cd ~/Documents/GitHub/ChaoticNexus
cp storage/production.db $BACKUP_DIR/production_${TIMESTAMP}.db

# Keep only last 30 backups
ls -t $BACKUP_DIR/production_*.db | tail -n +31 | xargs rm -f

echo "✅ Backup created: production_${TIMESTAMP}.db"
BACKUPEOF

chmod +x backup_database.sh

# Add to crontab for daily backups
# crontab -e
# Add line: 0 2 * * * /home/YOUR_USERNAME/backup_database.sh
```

## 📊 Monitoring

### Check Service Status
```bash
sudo systemctl status chaoticnexus
```

### View Logs
```bash
# Service logs
sudo journalctl -u chaoticnexus -f

# Application logs (if configured)
tail -f ~/Documents/GitHub/ChaoticNexus/logs/app.log
```

### Monitor Resources
```bash
# CPU and Memory
top
# or
htop

# Disk usage
df -h
```

## 🆘 Troubleshooting

### Service won't start
```bash
# Check logs
sudo journalctl -u chaoticnexus -n 50

# Check configuration
cd ~/Documents/GitHub/ChaoticNexus
source .venv/bin/activate
export FLASK_APP=app.wsgi:app
flask run  # Test manually
```

### Database migration errors
```bash
# Check migration status
flask db current

# Force upgrade
flask db upgrade

# If stuck, check logs
tail -f logs/*.log
```

### Permissions issues
```bash
# Fix ownership
sudo chown -R $USER:$USER ~/Documents/GitHub/ChaoticNexus

# Fix permissions
chmod 755 ~/Documents/GitHub/ChaoticNexus
chmod 600 ~/Documents/GitHub/ChaoticNexus/.env.local
```

## 📝 Quick Reference

### Production Commands
```bash
# Navigate to project
cd ~/Documents/GitHub/ChaoticNexus

# Activate venv
source .venv/bin/activate

# Update from Git
git pull origin main
pip install -r app/requirements.txt
flask db upgrade

# Service management
sudo systemctl start chaoticnexus
sudo systemctl stop chaoticnexus
sudo systemctl restart chaoticnexus
sudo systemctl status chaoticnexus

# View logs
sudo journalctl -u chaoticnexus -f

# Backup database
./backup_database.sh
```

## 🔗 Access URLs

- **Local:** http://localhost:5000
- **Network:** http://[Ubuntu-PC-IP]:5000
- **With Nginx:** http://your-domain.com

---

**This is your production environment - handle with care!** 🎯
