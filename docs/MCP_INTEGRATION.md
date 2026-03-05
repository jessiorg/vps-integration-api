# MCP Integration Guide

## Overview

This guide explains how to integrate the VPS Integration API with the Model Context Protocol (MCP) for seamless VPS management through Poke or other MCP clients.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Authentication Setup](#authentication-setup)
3. [MCP Configuration](#mcp-configuration)
4. [Available Tools](#available-tools)
5. [Usage Examples](#usage-examples)
6. [Security Best Practices](#security-best-practices)

## Prerequisites

- VPS Integration API installed and running on your Oracle VPS
- GitHub account with access to the API (added to `ALLOWED_USERS`)
- MCP client (Poke) configured
- SSL/TLS certificate for secure communication (recommended)

## Authentication Setup

### Step 1: Configure GitHub OAuth

1. Go to GitHub Settings → Developer settings → OAuth Apps
2. Create a new OAuth App:
   - **Application name**: VPS Integration API
   - **Homepage URL**: `https://your-vps-domain.com`
   - **Authorization callback URL**: `https://your-vps-domain.com/auth/github/callback`
3. Copy the Client ID and Client Secret

### Step 2: Update VPS Configuration

SSH into your VPS and edit the configuration:

```bash
sudo nano /opt/vps-integration-api/.env
```

Update these values:

```bash
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
GITHUB_REDIRECT_URI=https://your-vps-domain.com/auth/github/callback
ALLOWED_USERS=your_github_username
```

Restart the service:

```bash
sudo systemctl restart vps-integration-api
```

### Step 3: Obtain Access Token

1. Navigate to: `https://your-vps-domain.com/auth/github`
2. Authorize the application
3. Copy the JWT access token from the response

## MCP Configuration

### MCP Server Configuration File

Create or update your MCP server configuration (`~/.config/poke/mcp-servers.json`):

```json
{
  "vps-integration": {
    "command": "node",
    "args": ["/path/to/vps-mcp-server.js"],
    "env": {
      "VPS_API_URL": "https://your-vps-domain.com",
      "VPS_API_TOKEN": "your_jwt_token_here"
    }
  }
}
```

### MCP Server Implementation

Create a custom MCP server (`vps-mcp-server.js`):

```javascript
const { Server } = require('@modelcontextprotocol/sdk/server');
const { StdioServerTransport } = require('@modelcontextprotocol/sdk/server/stdio');
const axios = require('axios');

const API_URL = process.env.VPS_API_URL;
const API_TOKEN = process.env.VPS_API_TOKEN;

const api = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: { 'Authorization': `Bearer ${API_TOKEN}` }
});

const server = new Server({
  name: 'vps-integration',
  version: '1.0.0'
});

// System monitoring tools
server.tool('get_system_info', 'Get VPS system information', async () => {
  const response = await api.get('/system/info');
  return response.data;
});

server.tool('get_cpu_usage', 'Get CPU usage statistics', async () => {
  const response = await api.get('/system/cpu');
  return response.data;
});

server.tool('get_memory_usage', 'Get memory usage statistics', async () => {
  const response = await api.get('/system/memory');
  return response.data;
});

server.tool('get_disk_usage', 'Get disk usage statistics', async (params) => {
  const response = await api.get('/system/disk', {
    params: { path: params.path || '/' }
  });
  return response.data;
});

// Docker management tools
server.tool('list_containers', 'List Docker containers', async (params) => {
  const response = await api.get('/docker/containers', {
    params: { all: params.all || false }
  });
  return response.data;
});

server.tool('start_container', 'Start a Docker container', async (params) => {
  const response = await api.post(`/docker/containers/${params.container_id}/start`);
  return response.data;
});

server.tool('stop_container', 'Stop a Docker container', async (params) => {
  const response = await api.post(`/docker/containers/${params.container_id}/stop`);
  return response.data;
});

server.tool('get_container_logs', 'Get container logs', async (params) => {
  const response = await api.get(`/docker/containers/${params.container_id}/logs`, {
    params: { lines: params.lines || 100 }
  });
  return response.data;
});

// File operations tools
server.tool('read_file', 'Read file contents', async (params) => {
  const response = await api.get('/files/read', {
    params: { path: params.path }
  });
  return response.data;
});

server.tool('write_file', 'Write content to file', async (params) => {
  const response = await api.post('/files/write', {
    path: params.path,
    content: params.content,
    mode: params.mode || 'w'
  });
  return response.data;
});

server.tool('list_directory', 'List directory contents', async (params) => {
  const response = await api.get('/files/list', {
    params: { path: params.path }
  });
  return response.data;
});

// Process management tools
server.tool('list_processes', 'List running processes', async (params) => {
  const response = await api.get('/processes', {
    params: { limit: params.limit || 50 }
  });
  return response.data;
});

server.tool('get_process_info', 'Get process details', async (params) => {
  const response = await api.get(`/processes/${params.pid}`);
  return response.data;
});

// Start server
const transport = new StdioServerTransport();
server.connect(transport);
```

## Available Tools

### System Monitoring

| Tool | Description | Parameters |
|------|-------------|------------|
| `get_system_info` | Get VPS system information | None |
| `get_cpu_usage` | Get CPU usage statistics | None |
| `get_memory_usage` | Get memory usage statistics | None |
| `get_disk_usage` | Get disk usage statistics | `path` (optional) |
| `get_network_stats` | Get network statistics | None |
| `get_uptime` | Get system uptime | None |

### Docker Management

| Tool | Description | Parameters |
|------|-------------|------------|
| `list_containers` | List Docker containers | `all` (boolean) |
| `get_container_info` | Get container details | `container_id` |
| `start_container` | Start a container | `container_id` |
| `stop_container` | Stop a container | `container_id` |
| `restart_container` | Restart a container | `container_id` |
| `remove_container` | Remove a container | `container_id`, `force` |
| `get_container_logs` | Get container logs | `container_id`, `lines` |
| `get_container_stats` | Get container statistics | `container_id` |
| `create_container` | Create new container | `image`, `name`, etc. |

### File Operations

| Tool | Description | Parameters |
|------|-------------|------------|
| `read_file` | Read file contents | `path` |
| `write_file` | Write to file | `path`, `content`, `mode` |
| `delete_file` | Delete a file | `path` |
| `list_directory` | List directory contents | `path` |
| `check_file_exists` | Check if file exists | `path` |

### Process Management

| Tool | Description | Parameters |
|------|-------------|------------|
| `list_processes` | List running processes | `limit` |
| `get_process_info` | Get process details | `pid` |
| `kill_process` | Kill a process | `pid`, `signal_type` |
| `search_processes` | Search processes by name | `name` |

## Usage Examples

### Example 1: Check System Resources

```javascript
// Using Poke with MCP
const systemInfo = await poke.call('vps-integration', 'get_system_info');
const cpuUsage = await poke.call('vps-integration', 'get_cpu_usage');
const memoryUsage = await poke.call('vps-integration', 'get_memory_usage');

console.log(`CPU Usage: ${cpuUsage.usage_percent}%`);
console.log(`Memory Usage: ${memoryUsage.percent}%`);
```

### Example 2: Manage Docker Containers

```javascript
// List all containers
const containers = await poke.call('vps-integration', 'list_containers', {
  all: true
});

// Restart a specific container
await poke.call('vps-integration', 'restart_container', {
  container_id: 'nginx'
});

// Get container logs
const logs = await poke.call('vps-integration', 'get_container_logs', {
  container_id: 'nginx',
  lines: 50
});
```

### Example 3: Deploy Application

```javascript
// Read configuration file
const config = await poke.call('vps-integration', 'read_file', {
  path: '/etc/nginx/nginx.conf'
});

// Update configuration
await poke.call('vps-integration', 'write_file', {
  path: '/etc/nginx/sites-available/myapp',
  content: newConfig
});

// Restart nginx container
await poke.call('vps-integration', 'restart_container', {
  container_id: 'nginx'
});
```

### Example 4: Monitor Application

```javascript
// Find application process
const processes = await poke.call('vps-integration', 'search_processes', {
  name: 'node'
});

// Get detailed process info
const processInfo = await poke.call('vps-integration', 'get_process_info', {
  pid: processes[0].pid
});

console.log(`CPU: ${processInfo.cpu_percent}%`);
console.log(`Memory: ${processInfo.memory_percent}%`);
```

## Security Best Practices

### 1. Use HTTPS Only

Always use SSL/TLS for API communication:

```bash
sudo certbot --nginx -d your-vps-domain.com
```

### 2. Rotate Access Tokens

Regularly rotate your JWT tokens:

```bash
# Re-authenticate to get new token
curl https://your-vps-domain.com/auth/github
```

### 3. Limit User Access

Only add trusted users to `ALLOWED_USERS` in `.env`:

```bash
ALLOWED_USERS=user1,user2
```

### 4. Configure File Access

Restrict file operations to specific directories:

```bash
ALLOWED_PATHS=/data,/var/log,/etc/nginx
FORBIDDEN_PATHS=/etc/passwd,/etc/shadow,/root
```

### 5. Monitor API Usage

Regularly check API logs:

```bash
sudo journalctl -u vps-integration-api -f
```

### 6. Rate Limiting

The API has built-in rate limiting (60 requests/minute by default). Adjust if needed:

```bash
RATE_LIMIT_PER_MINUTE=60
```

### 7. Network Security

Use firewall rules to restrict access:

```bash
sudo ufw allow from YOUR_IP_ADDRESS to any port 443
```

## Troubleshooting

### Connection Issues

```bash
# Check if service is running
sudo systemctl status vps-integration-api

# Check service logs
sudo journalctl -u vps-integration-api -n 100

# Test health endpoint
curl http://localhost:8000/health
```

### Authentication Errors

```bash
# Verify token is valid
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://your-vps-domain.com/auth/verify

# Check allowed users
grep ALLOWED_USERS /opt/vps-integration-api/.env
```

### Docker Access Issues

```bash
# Check Docker socket permissions
ls -l /var/run/docker.sock

# Ensure service has access to Docker socket
sudo systemctl restart vps-integration-api
```

## Advanced Configuration

### Custom Port

Change the API port in `.env`:

```bash
API_PORT=8080
```

Update Nginx configuration accordingly.

### Multiple Workers

Adjust worker count for better performance:

```bash
API_WORKERS=8
```

### Logging Level

Change log verbosity:

```bash
LOG_LEVEL=debug  # Options: debug, info, warning, error
```

## Support

For issues and questions:

- GitHub Issues: https://github.com/jessiorg/vps-integration-api/issues
- Documentation: https://github.com/jessiorg/vps-integration-api/docs
