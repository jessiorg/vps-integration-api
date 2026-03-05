#!/usr/bin/env python3
"""
Simple MCP-Compatible Server using FastAPI
Provides system information and command execution capabilities with SSE support
"""

import os
import json
import asyncio
import subprocess
import platform
import psutil
from datetime import datetime
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Initialize FastAPI app
app = FastAPI(
    title="Simple MCP Server",
    description="MCP-compatible server for system information and command execution",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Key Configuration
API_KEY = os.getenv("MCP_API_KEY", "default-secret-key-change-in-production")


# Authentication
async def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """Verify API key from request headers"""
    if not x_api_key or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return x_api_key


# Request/Response Models
class CommandRequest(BaseModel):
    command: str
    timeout: Optional[int] = 30


class CommandResponse(BaseModel):
    success: bool
    stdout: str
    stderr: str
    return_code: int
    execution_time: float


class SystemInfoResponse(BaseModel):
    hostname: str
    platform: str
    platform_release: str
    platform_version: str
    architecture: str
    processor: str
    cpu_count: int
    cpu_percent: float
    memory_total: int
    memory_available: int
    memory_percent: float
    disk_total: int
    disk_used: int
    disk_free: int
    disk_percent: float
    boot_time: str
    uptime_seconds: float


class MCPMessage(BaseModel):
    """MCP-compatible message format"""
    type: str
    data: Dict[str, Any]
    timestamp: str


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Simple MCP Server",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": {
            "health": "/health",
            "system_info": "/api/system-info",
            "execute_command": "/api/execute",
            "sse_stream": "/api/sse"
        }
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


# System Information endpoint
@app.get("/api/system-info", response_model=SystemInfoResponse)
async def get_system_info(api_key: str = Depends(verify_api_key)):
    """Get comprehensive system information"""
    try:
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = (datetime.now() - boot_time).total_seconds()
        
        disk_usage = psutil.disk_usage('/')
        memory = psutil.virtual_memory()
        
        return SystemInfoResponse(
            hostname=platform.node(),
            platform=platform.system(),
            platform_release=platform.release(),
            platform_version=platform.version(),
            architecture=platform.machine(),
            processor=platform.processor() or "Unknown",
            cpu_count=psutil.cpu_count(),
            cpu_percent=psutil.cpu_percent(interval=1),
            memory_total=memory.total,
            memory_available=memory.available,
            memory_percent=memory.percent,
            disk_total=disk_usage.total,
            disk_used=disk_usage.used,
            disk_free=disk_usage.free,
            disk_percent=disk_usage.percent,
            boot_time=boot_time.isoformat(),
            uptime_seconds=uptime
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get system info: {str(e)}")


# Command Execution endpoint
@app.post("/api/execute", response_model=CommandResponse)
async def execute_command(
    request: CommandRequest,
    api_key: str = Depends(verify_api_key)
):
    """Execute a shell command with timeout"""
    try:
        start_time = datetime.now()
        
        # Execute command with timeout
        process = await asyncio.create_subprocess_shell(
            request.command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=request.timeout
            )
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()
            raise HTTPException(
                status_code=408,
                detail=f"Command execution timed out after {request.timeout} seconds"
            )
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return CommandResponse(
            success=process.returncode == 0,
            stdout=stdout.decode('utf-8', errors='replace'),
            stderr=stderr.decode('utf-8', errors='replace'),
            return_code=process.returncode,
            execution_time=execution_time
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Command execution failed: {str(e)}")


# SSE (Server-Sent Events) endpoint
@app.get("/api/sse")
async def sse_endpoint(api_key: str = Depends(verify_api_key)):
    """Server-Sent Events endpoint for real-time updates"""
    
    async def event_generator():
        """Generate SSE events"""
        try:
            # Send initial connection message
            yield f"data: {json.dumps({'type': 'connected', 'message': 'SSE stream established', 'timestamp': datetime.utcnow().isoformat()})}\n\n"
            
            # Send periodic system updates
            while True:
                try:
                    # Get current system metrics
                    cpu_percent = psutil.cpu_percent(interval=1)
                    memory = psutil.virtual_memory()
                    disk = psutil.disk_usage('/')
                    
                    data = {
                        'type': 'system_update',
                        'timestamp': datetime.utcnow().isoformat(),
                        'metrics': {
                            'cpu_percent': cpu_percent,
                            'memory_percent': memory.percent,
                            'disk_percent': disk.percent,
                            'memory_available_mb': memory.available / (1024 * 1024),
                            'disk_free_gb': disk.free / (1024 * 1024 * 1024)
                        }
                    }
                    
                    yield f"data: {json.dumps(data)}\n\n"
                    
                    # Wait before next update
                    await asyncio.sleep(5)
                    
                except asyncio.CancelledError:
                    # Client disconnected
                    break
                except Exception as e:
                    error_data = {
                        'type': 'error',
                        'message': str(e),
                        'timestamp': datetime.utcnow().isoformat()
                    }
                    yield f"data: {json.dumps(error_data)}\n\n"
                    await asyncio.sleep(5)
                    
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


# MCP-compatible tools list endpoint
@app.get("/api/tools")
async def list_tools(api_key: str = Depends(verify_api_key)):
    """List available MCP tools"""
    return {
        "tools": [
            {
                "name": "get_system_info",
                "description": "Get comprehensive system information including CPU, memory, disk usage, and uptime",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "execute_command",
                "description": "Execute a shell command with optional timeout",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "The shell command to execute"
                        },
                        "timeout": {
                            "type": "integer",
                            "description": "Timeout in seconds (default: 30)",
                            "default": 30
                        }
                    },
                    "required": ["command"]
                }
            }
        ]
    }


if __name__ == "__main__":
    import uvicorn
    
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    
    print(f"Starting Simple MCP Server on {host}:{port}")
    print(f"API Key: {API_KEY[:8]}...")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )
