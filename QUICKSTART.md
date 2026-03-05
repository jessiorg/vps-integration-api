# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Deploy on Oracle VPS (ARM64)

```bash
# SSH into your Oracle Cloud VPS
ssh ubuntu@your-vps-ip

# Run the one-command installer
curl -fsSL https://raw.githubusercontent.com/jessiorg/vps-integration-api/main/scripts/install.sh | sudo bash
```

### Step 2: Configure GitHub OAuth

1. Go to: https://github.com/settings/developers
2. Click "New OAuth App"
3. Fill in:
   - **Application name**: `VPS Integration API`
   - **Homepage URL**: `http://YOUR_VPS_IP` (or your domain)
   - **Authorization callback URL**: `http://YOUR_VPS_IP/auth/github/callback`
4. Click "Register application"
5. Copy the **Client ID** and **Client Secret**

### Step 3: Update Configuration

```bash
# Edit the environment file
sudo nano /opt/vps-integration-api/.env

# Update these lines:
GITHUB_CLIENT_ID=paste_your_client_id_here
GITHUB_CLIENT_SECRET=paste_your_client_secret_here
GITHUB_REDIRECT_URI=http://YOUR_VPS_IP/auth/github/callback
ALLOWED_USERS=your_github_username

# Save and exit (Ctrl+O, Enter, Ctrl+X)
```

### Step 4: Start the Service

```bash
# Start the API service
sudo systemctl start vps-integration-api

# Check it's running
sudo systemctl status vps-integration-api

# Expected output: "active (running)"
```

### Step 5: Get Your Access Token

1. Open browser and visit: `http://YOUR_VPS_IP/auth/github`
2. Authorize the application
3. Copy the `access_token` from the JSON response
4. Save it somewhere safe - you'll need it for API calls

### Step 6: Test the API

```bash
# Replace YOUR_TOKEN with the token from Step 5
export TOKEN="YOUR_TOKEN"

# Test system info
curl -H "Authorization: Bearer $TOKEN" \
  http://YOUR_VPS_IP/api/v1/system/info

# Should return JSON with system information
```

## 🎯 What's Next?

### Option A: Use with MCP/Poke

See [MCP Integration Guide](docs/MCP_INTEGRATION.md)

### Option B: Direct API Usage

```python
import requests

API = "http://YOUR_VPS_IP/api/v1"
TOKEN = "your_access_token"
headers = {"Authorization": f"Bearer {TOKEN}"}

# Monitor system
cpu = requests.get(f"{API}/system/cpu", headers=headers).json()
print(f"CPU Usage: {cpu['usage_percent']}%")

# Manage Docker
containers = requests.get(f"{API}/docker/containers", headers=headers).json()
for c in containers:
    print(f"{c['name']}: {c['status']}")
```

### Option C: Set Up SSL (Recommended for Production)

```bash
# Install Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Get SSL certificate (replace with your domain)
sudo certbot --nginx -d your-domain.com

# Update .env with HTTPS URL
sudo nano /opt/vps-integration-api/.env
# Change: GITHUB_REDIRECT_URI=https://your-domain.com/auth/github/callback

# Restart service
sudo systemctl restart vps-integration-api
```

## 📊 Monitor Your VPS

### View API Logs

```bash
# Follow logs in real-time
sudo journalctl -u vps-integration-api -f

# View last 100 lines
sudo journalctl -u vps-integration-api -n 100
```

### Access Interactive Documentation

Visit: `http://YOUR_VPS_IP/docs`

This gives you a Swagger UI where you can:
- See all available endpoints
- Test API calls directly from the browser
- View request/response schemas

## 🛠️ Common Tasks

### Restart a Docker Container

```bash
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  http://YOUR_VPS_IP/api/v1/docker/containers/nginx/restart
```

### Check Disk Space

```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://YOUR_VPS_IP/api/v1/system/disk
```

### Read a Log File

```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://YOUR_VPS_IP/api/v1/files/read?path=/var/log/syslog"
```

### Get Container Logs

```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://YOUR_VPS_IP/api/v1/docker/containers/myapp/logs?lines=50"
```

## 🔧 Troubleshooting

### API Not Accessible

```bash
# Check if service is running
sudo systemctl status vps-integration-api

# Check firewall
sudo ufw status

# If firewall is blocking, allow port 80
sudo ufw allow 80/tcp
```

### "401 Unauthorized" Error

```bash
# Your token might be expired. Get a new one:
# Visit: http://YOUR_VPS_IP/auth/github

# Or verify your current token:
curl -H "Authorization: Bearer $TOKEN" \
  http://YOUR_VPS_IP/auth/verify
```

### Docker Permission Errors

```bash
# Check Docker socket permissions
ls -l /var/run/docker.sock

# Restart service
sudo systemctl restart vps-integration-api
```

## 📚 Learn More

- **Full Documentation**: [README.md](README.md)
- **MCP Integration**: [docs/MCP_INTEGRATION.md](docs/MCP_INTEGRATION.md)
- **Examples**: [docs/EXAMPLES.md](docs/EXAMPLES.md)
- **API Docs**: `http://YOUR_VPS_IP/docs`

## 🆘 Need Help?

- **GitHub Issues**: https://github.com/jessiorg/vps-integration-api/issues
- **Check logs**: `sudo journalctl -u vps-integration-api -f`

---

**Congratulations! 🎉** Your VPS Integration API is now running and ready to use!
