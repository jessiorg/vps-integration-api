#!/bin/bash
# MCP Server Installation Script

echo "Installing Simple MCP Server..."

# Check if script already exists, download if not
if [ ! -f "$HOME/simple-mcp-server.py" ]; then
  echo "Downloading MCP server script..."
  curl -s -o "$HOME/simple-mcp-server.py" https://raw.githubusercontent.com/jessiorg/vps-integration-api/main/simple-mcp-server.py
  chmod +x "$HOME/simple-mcp-server.py"
else
  echo "MCP server script already exists"
fi

# Install required packages
echo "Installing required Python packages..."
pip3 install -q fastapi uvicorn sse-starlette psutil

# Create systemd service file
echo "Creating systemd service..."
sudo bash -c 'cat > /etc/systemd/system/simple-mcp-server.service << EOL
[Unit]
Description=Simple MCP Server
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu
ExecStart=/usr/bin/python3 /home/ubuntu/simple-mcp-server.py
Restart=always
RestartSec=10
Environment=MCP_API_KEY=default-secret-key-change-in-production

[Install]
WantedBy=multi-user.target
EOL'

# Reload systemd, enable and start service
echo "Starting service..."
sudo systemctl daemon-reload
sudo systemctl enable simple-mcp-server
sudo systemctl start simple-mcp-server

# Check service status
echo "Service status:"
sudo systemctl status simple-mcp-server --no-pager

echo ""
echo "Installation complete! MCP Server is running at:"
echo "http://$(hostname -I | awk '{print $1}'):8080/api/sse"
echo ""
echo "API Key: default-secret-key-change-in-production"
echo ""
echo "To view logs: sudo journalctl -u simple-mcp-server -f"
echo "To restart: sudo systemctl restart simple-mcp-server"
echo "To stop: sudo systemctl stop simple-mcp-server"
