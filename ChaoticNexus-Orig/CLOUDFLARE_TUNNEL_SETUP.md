# 🌐 Cloudflare Tunnel Setup for PowderApp

## ✅ Installation Complete!

Cloudflared has been installed at: `~/cloudflared`

## 🚀 Quick Start (Temporary Tunnel)

The fastest way to create a tunnel for testing:

```bash
~/cloudflared tunnel --url http://localhost:5001
```

This will:
- Create a temporary tunnel
- Give you a random URL like `https://random-words-1234.trycloudflare.com`
- Route all traffic to your PowderApp at `localhost:5001`
- Work immediately (no setup needed!)

**Note**: This tunnel stops when you close the terminal or press Ctrl+C.

## 🔐 Production Setup (Named Tunnel)

For a permanent tunnel with your own domain:

### **Step 1: Login to Cloudflare**
```bash
~/cloudflared tunnel login
```

This will:
- Open your browser
- Ask you to select a Cloudflare zone/domain
- Save credentials to `~/.cloudflared/`

### **Step 2: Create a Named Tunnel**
```bash
~/cloudflared tunnel create powderapp
```

This creates a permanent tunnel named "powderapp" and gives you a tunnel ID.

### **Step 3: Create Configuration File**

Create `~/.cloudflared/config.yml`:

```yaml
tunnel: <YOUR-TUNNEL-ID>
credentials-file: /home/harley/.cloudflared/<YOUR-TUNNEL-ID>.json

ingress:
  # Route your domain to PowderApp
  - hostname: app.yourdomain.com
    service: http://localhost:5001
  
  # Catch-all rule (required)
  - service: http_status:404
```

### **Step 4: Route DNS**
```bash
~/cloudflared tunnel route dns powderapp app.yourdomain.com
```

This creates a CNAME record in your Cloudflare DNS pointing to your tunnel.

### **Step 5: Run the Tunnel**
```bash
~/cloudflared tunnel run powderapp
```

Or run in background:
```bash
nohup ~/cloudflared tunnel run powderapp > ~/cloudflared.log 2>&1 &
```

## 📋 Important Settings

### **Your App Details:**
- **Local URL**: `http://localhost:5001`
- **Docker Container**: `PowderApp1.3`
- **Login Page**: `http://localhost:5001/react/login`

### **Cloudflare Will Proxy:**
- All HTTP/HTTPS traffic
- Automatic SSL/TLS
- DDoS protection
- CDN caching (for static files)

## 🔧 Useful Commands

### **Check if tunnel is running:**
```bash
ps aux | grep cloudflared
```

### **List your tunnels:**
```bash
~/cloudflared tunnel list
```

### **View tunnel info:**
```bash
~/cloudflared tunnel info powderapp
```

### **Stop tunnel:**
```bash
# If running in foreground: Press Ctrl+C

# If running in background:
pkill cloudflared
```

### **View tunnel logs:**
```bash
# If running with nohup:
tail -f ~/cloudflared.log

# If running with systemd:
journalctl -u cloudflared -f
```

## 🎯 Quick Test Tunnel

Want to test right now? Run this command:

```bash
~/cloudflared tunnel --url http://localhost:5001
```

You'll get a URL that looks like:
```
https://random-words-1234.trycloudflare.com
```

Open that URL in your browser and you'll see your PowderApp login page! 🎉

## 🔐 Security Considerations

1. **Session Cookies**: Your Flask sessions should work fine over HTTPS
2. **Login Works**: The React login will work through the tunnel
3. **Database**: Your local database stays local (secure!)
4. **Uploads**: File uploads will work through the tunnel

## 📱 For Production Use

If you want this to run permanently:

1. **Create a systemd service** (optional):

Create `/etc/systemd/system/cloudflared.service`:
```ini
[Unit]
Description=Cloudflare Tunnel
After=network.target

[Service]
Type=simple
User=harley
ExecStart=/home/harley/cloudflared tunnel run powderapp
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

2. **Enable and start**:
```bash
sudo systemctl enable cloudflared
sudo systemctl start cloudflared
```

## 🎊 Summary

✅ **Installed**: `~/cloudflared`
✅ **App URL**: `http://localhost:5001`
✅ **Quick Test**: `~/cloudflared tunnel --url http://localhost:5001`
✅ **Your Login**: Modern React login with glassmorphism!

**To start a tunnel right now, just run:**
```bash
~/cloudflared tunnel --url http://localhost:5001
```

Then open the generated URL in your browser! 🚀













