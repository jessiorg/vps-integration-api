# Usage Examples

## Table of Contents

1. [System Monitoring](#system-monitoring)
2. [Docker Management](#docker-management)
3. [Application Deployment](#application-deployment)
4. [File Management](#file-management)
5. [Process Management](#process-management)
6. [Automation Scripts](#automation-scripts)

## System Monitoring

### Example 1: Complete System Health Check

```bash
#!/bin/bash
# System health check script

API_URL="https://your-vps-domain.com/api/v1"
TOKEN="your_jwt_token"

# Get system info
echo "=== System Information ==="
curl -s -H "Authorization: Bearer $TOKEN" "$API_URL/system/info" | jq

# Get CPU usage
echo "\n=== CPU Usage ==="
curl -s -H "Authorization: Bearer $TOKEN" "$API_URL/system/cpu" | jq

# Get memory usage
echo "\n=== Memory Usage ==="
curl -s -H "Authorization: Bearer $TOKEN" "$API_URL/system/memory" | jq

# Get disk usage
echo "\n=== Disk Usage ==="
curl -s -H "Authorization: Bearer $TOKEN" "$API_URL/system/disk" | jq

# Get network stats
echo "\n=== Network Statistics ==="
curl -s -H "Authorization: Bearer $TOKEN" "$API_URL/system/network" | jq

# Get uptime
echo "\n=== System Uptime ==="
curl -s -H "Authorization: Bearer $TOKEN" "$API_URL/system/uptime" | jq
```

### Example 2: Resource Usage Alert

```python
import requests
import smtplib
from email.message import EmailMessage

API_URL = "https://your-vps-domain.com/api/v1"
TOKEN = "your_jwt_token"
headers = {"Authorization": f"Bearer {TOKEN}"}

def check_resources():
    # Check CPU
    cpu = requests.get(f"{API_URL}/system/cpu", headers=headers).json()
    if cpu['usage_percent'] > 80:
        send_alert(f"High CPU usage: {cpu['usage_percent']}%")
    
    # Check memory
    memory = requests.get(f"{API_URL}/system/memory", headers=headers).json()
    if memory['percent'] > 85:
        send_alert(f"High memory usage: {memory['percent']}%")
    
    # Check disk
    disk = requests.get(f"{API_URL}/system/disk", headers=headers).json()
    if disk['percent'] > 90:
        send_alert(f"High disk usage: {disk['percent']}%")

def send_alert(message):
    # Send email alert
    msg = EmailMessage()
    msg['Subject'] = 'VPS Resource Alert'
    msg['From'] = 'alerts@yourserver.com'
    msg['To'] = 'admin@yourserver.com'
    msg.set_content(message)
    
    with smtplib.SMTP('localhost') as s:
        s.send_message(msg)

if __name__ == '__main__':
    check_resources()
```

## Docker Management

### Example 3: Container Health Monitoring

```python
import requests
import time

API_URL = "https://your-vps-domain.com/api/v1"
TOKEN = "your_jwt_token"
headers = {"Authorization": f"Bearer {TOKEN}"}

def monitor_containers():
    while True:
        containers = requests.get(
            f"{API_URL}/docker/containers",
            headers=headers
        ).json()
        
        for container in containers:
            if container['status'] != 'running':
                print(f"⚠️  Container {container['name']} is {container['status']}")
                # Attempt to restart
                try:
                    requests.post(
                        f"{API_URL}/docker/containers/{container['id']}/start",
                        headers=headers
                    )
                    print(f"✓ Restarted {container['name']}")
                except Exception as e:
                    print(f"✗ Failed to restart {container['name']}: {e}")
        
        time.sleep(60)  # Check every minute

if __name__ == '__main__':
    monitor_containers()
```

### Example 4: Log Aggregation

```python
import requests
from datetime import datetime

API_URL = "https://your-vps-domain.com/api/v1"
TOKEN = "your_jwt_token"
headers = {"Authorization": f"Bearer {TOKEN}"}

def collect_logs(container_names, lines=100):
    """Collect logs from multiple containers"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for container in container_names:
        response = requests.get(
            f"{API_URL}/docker/containers/{container}/logs",
            headers=headers,
            params={"lines": lines}
        )
        
        if response.status_code == 200:
            logs = response.json()['logs']
            filename = f"logs/{container}_{timestamp}.log"
            
            with open(filename, 'w') as f:
                f.write(logs)
            
            print(f"✓ Saved logs for {container} to {filename}")
        else:
            print(f"✗ Failed to get logs for {container}")

if __name__ == '__main__':
    containers = ['nginx', 'redis', 'postgres']
    collect_logs(containers)
```

## Application Deployment

### Example 5: Deploy Node.js Application

```python
import requests
import time

API_URL = "https://your-vps-domain.com/api/v1"
TOKEN = "your_jwt_token"
headers = {"Authorization": f"Bearer {TOKEN}"}

def deploy_app():
    print("Starting deployment...")
    
    # 1. Create deployment directory
    print("Creating deployment directory...")
    requests.post(
        f"{API_URL}/files/write",
        headers=headers,
        json={
            "path": "/data/app/.gitkeep",
            "content": ""
        }
    )
    
    # 2. Write package.json
    print("Writing package.json...")
    package_json = '''
{
  "name": "my-app",
  "version": "1.0.0",
  "scripts": {
    "start": "node server.js"
  },
  "dependencies": {
    "express": "^4.18.0"
  }
}
'''
    requests.post(
        f"{API_URL}/files/write",
        headers=headers,
        json={
            "path": "/data/app/package.json",
            "content": package_json
        }
    )
    
    # 3. Write application code
    print("Writing application code...")
    server_js = '''
const express = require('express');
const app = express();

app.get('/', (req, res) => {
  res.json({ message: 'Hello from VPS!' });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
'''
    requests.post(
        f"{API_URL}/files/write",
        headers=headers,
        json={
            "path": "/data/app/server.js",
            "content": server_js
        }
    )
    
    # 4. Create Dockerfile
    print("Creating Dockerfile...")
    dockerfile = '''
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install --production
COPY . .
EXPOSE 3000
CMD ["npm", "start"]
'''
    requests.post(
        f"{API_URL}/files/write",
        headers=headers,
        json={
            "path": "/data/app/Dockerfile",
            "content": dockerfile
        }
    )
    
    # 5. Build and run container
    print("Building Docker image...")
    # Note: This would require additional API endpoint for building images
    # For now, you'd SSH in and run: docker build -t myapp /data/app
    
    print("Deployment complete!")

if __name__ == '__main__':
    deploy_app()
```

### Example 6: Blue-Green Deployment

```python
import requests
import time

API_URL = "https://your-vps-domain.com/api/v1"
TOKEN = "your_jwt_token"
headers = {"Authorization": f"Bearer {TOKEN}"}

def blue_green_deployment(new_version):
    """Perform blue-green deployment"""
    
    # 1. Start new version (green)
    print(f"Starting new version: {new_version}")
    requests.post(
        f"{API_URL}/docker/containers",
        headers=headers,
        json={
            "image": f"myapp:{new_version}",
            "name": "myapp-green",
            "ports": {"3000/tcp": 3001}
        }
    )
    
    # 2. Wait for green to be healthy
    print("Waiting for green environment to be ready...")
    time.sleep(10)
    
    # 3. Update nginx configuration to point to green
    print("Updating nginx configuration...")
    nginx_conf = f'''
upstream myapp {{
    server localhost:3001;  # Green
}}
'''
    requests.post(
        f"{API_URL}/files/write",
        headers=headers,
        json={
            "path": "/etc/nginx/conf.d/myapp.conf",
            "content": nginx_conf
        }
    )
    
    # 4. Reload nginx
    print("Reloading nginx...")
    requests.post(
        f"{API_URL}/docker/containers/nginx/restart",
        headers=headers
    )
    
    # 5. Stop old version (blue)
    print("Stopping old version...")
    time.sleep(5)
    requests.post(
        f"{API_URL}/docker/containers/myapp-blue/stop",
        headers=headers
    )
    
    # 6. Rename green to blue
    print("Deployment complete!")

if __name__ == '__main__':
    blue_green_deployment("v2.0.0")
```

## File Management

### Example 7: Backup Configuration Files

```python
import requests
from datetime import datetime
import json

API_URL = "https://your-vps-domain.com/api/v1"
TOKEN = "your_jwt_token"
headers = {"Authorization": f"Bearer {TOKEN}"}

def backup_configs():
    """Backup important configuration files"""
    configs = [
        "/etc/nginx/nginx.conf",
        "/etc/nginx/sites-available/default",
        "/data/app/.env",
        "/etc/systemd/system/myapp.service"
    ]
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_data = {}
    
    for config_path in configs:
        response = requests.get(
            f"{API_URL}/files/read",
            headers=headers,
            params={"path": config_path}
        )
        
        if response.status_code == 200:
            backup_data[config_path] = response.json()['content']
            print(f"✓ Backed up {config_path}")
        else:
            print(f"✗ Failed to backup {config_path}")
    
    # Save backup locally
    backup_file = f"backup_{timestamp}.json"
    with open(backup_file, 'w') as f:
        json.dump(backup_data, f, indent=2)
    
    print(f"\nBackup saved to {backup_file}")

if __name__ == '__main__':
    backup_configs()
```

## Process Management

### Example 8: Find and Kill Resource-Heavy Processes

```python
import requests

API_URL = "https://your-vps-domain.com/api/v1"
TOKEN = "your_jwt_token"
headers = {"Authorization": f"Bearer {TOKEN}"}

def kill_resource_hogs(cpu_threshold=80, memory_threshold=80):
    """Kill processes using too many resources"""
    
    # Get all processes
    response = requests.get(
        f"{API_URL}/processes",
        headers=headers,
        params={"limit": 100}
    )
    
    processes = response.json()
    
    for proc in processes:
        should_kill = False
        reason = []
        
        if proc['cpu_percent'] > cpu_threshold:
            should_kill = True
            reason.append(f"CPU: {proc['cpu_percent']}%")
        
        if proc['memory_percent'] > memory_threshold:
            should_kill = True
            reason.append(f"Memory: {proc['memory_percent']}%")
        
        if should_kill and proc['name'] not in ['systemd', 'init']:
            print(f"Killing {proc['name']} (PID {proc['pid']}): {', '.join(reason)}")
            
            response = requests.delete(
                f"{API_URL}/processes/{proc['pid']}",
                headers=headers
            )
            
            if response.status_code == 200:
                print(f"✓ Killed process {proc['pid']}")
            else:
                print(f"✗ Failed to kill process {proc['pid']}")

if __name__ == '__main__':
    kill_resource_hogs()
```

## Automation Scripts

### Example 9: Complete Monitoring Dashboard

```python
import requests
import time
import os
from datetime import datetime

API_URL = "https://your-vps-domain.com/api/v1"
TOKEN = "your_jwt_token"
headers = {"Authorization": f"Bearer {TOKEN}"}

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def display_dashboard():
    while True:
        clear_screen()
        print("="*60)
        print(f"VPS Monitoring Dashboard - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        # System Info
        system = requests.get(f"{API_URL}/system/info", headers=headers).json()
        print(f"\nHostname: {system['hostname']}")
        print(f"Platform: {system['platform']} {system['platform_release']}")
        print(f"Architecture: {system['architecture']}")
        
        # CPU
        cpu = requests.get(f"{API_URL}/system/cpu", headers=headers).json()
        print(f"\nCPU Usage: {cpu['usage_percent']}%")
        
        # Memory
        memory = requests.get(f"{API_URL}/system/memory", headers=headers).json()
        print(f"Memory: {memory['used_gb']:.2f}GB / {memory['total_gb']:.2f}GB ({memory['percent']}%)")
        
        # Disk
        disk = requests.get(f"{API_URL}/system/disk", headers=headers).json()
        print(f"Disk: {disk['used_gb']:.2f}GB / {disk['total_gb']:.2f}GB ({disk['percent']}%)")
        
        # Uptime
        uptime = requests.get(f"{API_URL}/system/uptime", headers=headers).json()
        print(f"Uptime: {uptime['uptime_formatted']}")
        
        # Docker Containers
        containers = requests.get(f"{API_URL}/docker/containers", headers=headers).json()
        print(f"\nDocker Containers ({len(containers)}):")
        for container in containers[:5]:
            status_icon = "🟢" if container['status'] == 'running' else "🔴"
            print(f"  {status_icon} {container['name']}: {container['status']}")
        
        # Top Processes
        processes = requests.get(
            f"{API_URL}/processes",
            headers=headers,
            params={"limit": 5}
        ).json()
        print(f"\nTop Processes:")
        for proc in processes:
            print(f"  {proc['name'][:20]:20} CPU: {proc['cpu_percent']:5.1f}% MEM: {proc['memory_percent']:5.1f}%")
        
        print("\nPress Ctrl+C to exit")
        time.sleep(5)

if __name__ == '__main__':
    try:
        display_dashboard()
    except KeyboardInterrupt:
        print("\nDashboard stopped.")
```

### Example 10: Automated Maintenance Script

```bash
#!/bin/bash
# Automated VPS maintenance script

API_URL="https://your-vps-domain.com/api/v1"
TOKEN="your_jwt_token"

echo "Starting VPS maintenance..."

# 1. Check system resources
echo "Checking system resources..."
DISK_USAGE=$(curl -s -H "Authorization: Bearer $TOKEN" "$API_URL/system/disk" | jq -r '.percent')

if (( $(echo "$DISK_USAGE > 85" | bc -l) )); then
    echo "⚠️  Disk usage is high: ${DISK_USAGE}%"
    # Clean up Docker
    echo "Cleaning Docker resources..."
    docker system prune -f
fi

# 2. Restart containers with issues
echo "Checking container health..."
CONTAINERS=$(curl -s -H "Authorization: Bearer $TOKEN" "$API_URL/docker/containers" | jq -r '.[] | select(.status != "running") | .id')

for CONTAINER in $CONTAINERS; do
    echo "Restarting container: $CONTAINER"
    curl -s -X POST -H "Authorization: Bearer $TOKEN" "$API_URL/docker/containers/$CONTAINER/start"
done

# 3. Update system packages (commented out for safety)
# echo "Updating system packages..."
# apt-get update && apt-get upgrade -y

# 4. Backup configurations
echo "Creating backups..."
/opt/vps-integration-api/scripts/backup.sh

echo "Maintenance complete!"
```

These examples demonstrate the full capabilities of the VPS Integration API for managing your Oracle VPS through MCP/Poke or direct API calls.
