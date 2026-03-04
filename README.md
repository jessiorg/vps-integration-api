# VPS Integration API - Production Ready

![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-green)
![Python](https://img.shields.io/badge/Python-3.12+-blue)
![Docker](https://img.shields.io/badge/Docker-Enabled-blue)
![Security](https://img.shields.io/badge/Security-OAuth2-red)

## 🚀 Overview

A production-ready FastAPI application for VPS management and integration. Provides secure endpoints for system monitoring, Docker container management, file operations, and more. Designed for MCP (Model Context Protocol) integration with GitHub OAuth security.

## ✨ Features

- **FastAPI Framework**: High-performance async API
- **System Monitoring**: CPU, memory, disk, network stats
- **Docker Management**: Container lifecycle, logs, stats
- **File Operations**: Secure file read/write/delete
- **Process Management**: List, kill, monitor processes
- **GitHub OAuth**: Secure authentication
- **Rate Limiting**: Request throttling
- **Auto Documentation**: Swagger UI & ReDoc
- **WebSocket Support**: Real-time updates
- **Production Ready**: Logging, error handling, security

## 📚 API Endpoints

### System Endpoints

#### System Info
```bash
GET /api/v1/system/info
Authorization: Bearer {token}
```

Response:
```json
{
  "hostname": "vps-server",
  "platform": "Linux",
  "cpu_count": 4,
  "memory_total": "16GB",
  "disk_total": "500GB"
}
```

#### CPU Usage
```bash
GET /api/v1/system/cpu
Authorization: Bearer {token}
```

#### Memory Usage
```bash
GET /api/v1/system/memory
Authorization: Bearer {token}
```

#### Disk Usage
```bash
GET /api/v1/system/disk
Authorization: Bearer {token}
```

### Docker Endpoints

#### List Containers
```bash
GET /api/v1/docker/containers
Authorization: Bearer {token}
```

#### Container Details
```bash
GET /api/v1/docker/containers/{container_id}
Authorization: Bearer {token}
```

#### Start Container
```bash
POST /api/v1/docker/containers/{container_id}/start
Authorization: Bearer {token}
```

#### Stop Container
```bash
POST /api/v1/docker/containers/{container_id}/stop
Authorization: Bearer {token}
```

#### Container Logs
```bash
GET /api/v1/docker/containers/{container_id}/logs?lines=100
Authorization: Bearer {token}
```

#### Container Stats
```bash
GET /api/v1/docker/containers/{container_id}/stats
Authorization: Bearer {token}
```

### File Operations

#### Read File
```bash
GET /api/v1/files/read?path=/path/to/file
Authorization: Bearer {token}
```

#### Write File
```bash
POST /api/v1/files/write
Authorization: Bearer {token}
Content-Type: application/json

{
  "path": "/path/to/file",
  "content": "file content",
  "mode": "w"
}
```

#### Delete File
```bash
DELETE /api/v1/files/delete?path=/path/to/file
Authorization: Bearer {token}
```

#### List Directory
```bash
GET /api/v1/files/list?path=/path/to/dir
Authorization: Bearer {token}
```

### Process Management

#### List Processes
```bash
GET /api/v1/processes
Authorization: Bearer {token}
```

#### Process Details
```bash
GET /api/v1/processes/{pid}
Authorization: Bearer {token}
```

#### Kill Process
```bash
DELETE /api/v1/processes/{pid}
Authorization: Bearer {token}
```

### Authentication

#### GitHub OAuth Login
```bash
GET /auth/github
```

#### OAuth Callback
```bash
GET /auth/github/callback?code={auth_code}
```

#### Verify Token
```bash
GET /auth/verify
Authorization: Bearer {token}
```

## 📁 Architecture

```
vps-integration-api/
├── api/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app
│   ├── config.py               # Configuration
│   ├── auth/
│   │   ├── oauth.py            # GitHub OAuth
│   │   └── security.py         # JWT, permissions
│   ├── routers/
│   │   ├── system.py           # System endpoints
│   │   ├── docker.py           # Docker endpoints
│   │   ├── files.py            # File operations
│   │   └── processes.py        # Process management
│   ├── middleware/
│   │   ├── rate_limit.py       # Rate limiting
│   │   └── logging.py          # Request logging
│   └── utils/
│       ├── helpers.py          # Utility functions
│       └── validators.py       # Input validation
├── Dockerfile
├── requirements.txt
├── docker-compose.service.yml
└── scripts/
    └── deploy.sh
```

## 🛠️ Installation

### Prerequisites

- Docker 24.0+
- Docker Compose 2.20+
- GitHub OAuth App (for authentication)
- Minimum 2GB RAM

### Quick Start

1. **Clone repository**
   ```bash
   git clone https://github.com/jessiorg/vps-integration-api.git
   cd vps-integration-api
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   nano .env
   # Add your GitHub OAuth credentials
   ```

3. **Deploy**
   ```bash
   sudo chmod +x scripts/deploy.sh
   sudo ./scripts/deploy.sh
   ```

4. **Test API**
   ```bash
   curl http://localhost:8003/health
   ```

### GitHub OAuth Setup

1. Go to GitHub Settings → Developer settings → OAuth Apps
2. Create new OAuth App:
   - Name: VPS Integration API
   - Homepage URL: `https://your-domain.com`
   - Callback URL: `https://your-domain.com/auth/github/callback`
3. Copy Client ID and Client Secret to `.env`

## 🌐 Usage Examples

### Python Client

```python
import requests

base_url = "https://your-domain.com/api/v1"
token = "your_jwt_token"
headers = {"Authorization": f"Bearer {token}"}

# Get system info
response = requests.get(f"{base_url}/system/info", headers=headers)
print(response.json())

# List Docker containers
response = requests.get(f"{base_url}/docker/containers", headers=headers)
containers = response.json()

for container in containers:
    print(f"{container['name']}: {container['status']}")

# Read file
response = requests.get(
    f"{base_url}/files/read",
    params={"path": "/etc/nginx/nginx.conf"},
    headers=headers
)
print(response.json()["content"])

# Start container
response = requests.post(
    f"{base_url}/docker/containers/my-container/start",
    headers=headers
)
print(response.json())
```

### JavaScript/Node.js

```javascript
const axios = require('axios');

const api = axios.create({
  baseURL: 'https://your-domain.com/api/v1',
  headers: { 'Authorization': `Bearer ${token}` }
});

// System monitoring
async function getSystemStats() {
  const [cpu, memory, disk] = await Promise.all([
    api.get('/system/cpu'),
    api.get('/system/memory'),
    api.get('/system/disk')
  ]);
  
  return {
    cpu: cpu.data,
    memory: memory.data,
    disk: disk.data
  };
}

// Docker management
async function restartContainer(containerName) {
  await api.post(`/docker/containers/${containerName}/stop`);
  await new Promise(resolve => setTimeout(resolve, 2000));
  await api.post(`/docker/containers/${containerName}/start`);
}

// File operations
async function updateConfig(path, content) {
  await api.post('/files/write', {
    path: path,
    content: content,
    mode: 'w'
  });
}
```

### curl Examples

```bash
# Get JWT token (after OAuth)
TOKEN="your_jwt_token"

# System info
curl -H "Authorization: Bearer $TOKEN" \
  https://your-domain.com/api/v1/system/info

# CPU usage
curl -H "Authorization: Bearer $TOKEN" \
  https://your-domain.com/api/v1/system/cpu

# List containers
curl -H "Authorization: Bearer $TOKEN" \
  https://your-domain.com/api/v1/docker/containers

# Container logs
curl -H "Authorization: Bearer $TOKEN" \
  "https://your-domain.com/api/v1/docker/containers/nginx/logs?lines=50"

# Read file
curl -H "Authorization: Bearer $TOKEN" \
  "https://your-domain.com/api/v1/files/read?path=/var/log/app.log"

# Write file
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"path":"/tmp/test.txt","content":"Hello World"}' \
  https://your-domain.com/api/v1/files/write
```

## 🔧 Configuration

### Environment Variables

**.env file:**
```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4
LOG_LEVEL=info

# Security
SECRET_KEY=your-secret-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# GitHub OAuth
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
GITHUB_REDIRECT_URI=https://your-domain.com/auth/github/callback

# Allowed Users (GitHub usernames)
ALLOWED_USERS=user1,user2,user3

# CORS
CORS_ORIGINS=https://your-domain.com,http://localhost:3000

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60

# Docker Socket
DOCKER_SOCKET=/var/run/docker.sock

# File Operations
ALLOWED_PATHS=/data,/var/log,/etc/nginx
FORBIDDEN_PATHS=/etc/passwd,/etc/shadow
```

## 🔒 Security

### Authentication Flow

1. User clicks "Login with GitHub"
2. Redirected to GitHub OAuth
3. User authorizes app
4. Callback with auth code
5. Exchange code for access token
6. Verify user in allowed list
7. Generate JWT token
8. Return token to client

### Authorization

```python
from fastapi import Depends, HTTPException
from api.auth.security import get_current_user

@app.get("/api/v1/protected")
async def protected_endpoint(current_user: dict = Depends(get_current_user)):
    return {"message": f"Hello, {current_user['username']}"}
```

### Rate Limiting

- 60 requests per minute per IP (configurable)
- Returns 429 Too Many Requests when exceeded
- Sliding window algorithm

### File Access Control

- Whitelist allowed paths
- Blacklist forbidden paths
- Path traversal protection
- Permission validation

## 📊 Use Cases

### 1. MCP Integration

```python
# MCP server can call API to manage VPS
from mcp import Server
import requests

class VPSTools:
    def __init__(self, api_url, token):
        self.api_url = api_url
        self.headers = {"Authorization": f"Bearer {token}"}
    
    def get_container_status(self, container_name):
        response = requests.get(
            f"{self.api_url}/docker/containers/{container_name}",
            headers=self.headers
        )
        return response.json()
    
    def restart_service(self, service_name):
        # Stop container
        requests.post(
            f"{self.api_url}/docker/containers/{service_name}/stop",
            headers=self.headers
        )
        # Start container
        requests.post(
            f"{self.api_url}/docker/containers/{service_name}/start",
            headers=self.headers
        )
```

### 2. Monitoring Dashboard

```javascript
// Real-time monitoring
setInterval(async () => {
  const stats = await getSystemStats();
  updateDashboard(stats);
}, 5000);

function updateDashboard(stats) {
  document.getElementById('cpu').textContent = stats.cpu.usage + '%';
  document.getElementById('memory').textContent = stats.memory.percent + '%';
  document.getElementById('disk').textContent = stats.disk.percent + '%';
}
```

### 3. Automated Deployment

```bash
#!/bin/bash
# Deploy new version

API="https://your-domain.com/api/v1"
TOKEN="your_token"

# Pull new image
curl -X POST -H "Authorization: Bearer $TOKEN" \
  "$API/docker/images/pull" \
  -d '{"image": "myapp:latest"}'

# Stop old container
curl -X POST -H "Authorization: Bearer $TOKEN" \
  "$API/docker/containers/myapp/stop"

# Start new container
curl -X POST -H "Authorization: Bearer $TOKEN" \
  "$API/docker/containers/create" \
  -d '{"image": "myapp:latest", "name": "myapp"}'
```

## 📝 Monitoring & Logging

### View Logs
```bash
# Container logs
docker logs vps-integration-api

# Follow logs
docker logs -f vps-integration-api

# API logs
docker exec vps-integration-api cat /var/log/api.log
```

### Health Checks
```bash
# Health endpoint
curl http://localhost:8003/health

# Metrics
curl http://localhost:8003/metrics
```

## 🚀 Production Deployment

### 1. SSL/TLS
```bash
sudo certbot --nginx -d your-domain.com
```

### 2. Firewall
```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 3. Systemd Service
```bash
# Ensure starts on boot
sudo systemctl enable docker
```

### 4. Monitoring
- Integrate with Prometheus
- Set up Grafana dashboards
- Configure alerts

## 📚 Documentation

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [GitHub OAuth](https://docs.github.com/en/developers/apps/building-oauth-apps)
- [Docker SDK](https://docker-py.readthedocs.io/)

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md)

## 📄 License

MIT License - see [LICENSE](LICENSE)

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/)
- [Docker SDK for Python](https://docker-py.readthedocs.io/)
- [psutil](https://github.com/giampaolo/psutil)

---

**Version**: 1.0.0  
**Last Updated**: March 4, 2026  
**Maintained by**: Organiser (@jessiorg)