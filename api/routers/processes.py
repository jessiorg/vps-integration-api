"""Process Management Router"""

import logging
import signal
from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from pydantic import BaseModel
import psutil

from api.auth.security import get_current_user
from api.config import settings

logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)

router = APIRouter()


class ProcessInfo(BaseModel):
    pid: int
    name: str
    status: str
    cpu_percent: float
    memory_percent: float
    username: str
    create_time: float


class ProcessDetail(BaseModel):
    pid: int
    name: str
    status: str
    cpu_percent: float
    memory_percent: float
    memory_info: dict
    username: str
    create_time: float
    cmdline: List[str]
    cwd: str
    num_threads: int
    connections: List[dict]


@router.get("", response_model=List[ProcessInfo])
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def list_processes(
    request: Request,
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
) -> List[ProcessInfo]:
    """List running processes"""
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'status', 'username', 'create_time']):
            try:
                pinfo = proc.info
                processes.append(
                    ProcessInfo(
                        pid=pinfo['pid'],
                        name=pinfo['name'],
                        status=pinfo['status'],
                        cpu_percent=proc.cpu_percent(interval=0.1),
                        memory_percent=proc.memory_percent(),
                        username=pinfo.get('username', 'N/A'),
                        create_time=pinfo['create_time']
                    )
                )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Sort by CPU usage and limit
        processes.sort(key=lambda x: x.cpu_percent, reverse=True)
        return processes[:limit]
    
    except Exception as e:
        logger.error(f"Failed to list processes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list processes: {str(e)}"
        )


@router.get("/{pid}", response_model=ProcessDetail)
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def get_process(
    pid: int,
    request: Request,
    current_user: dict = Depends(get_current_user)
) -> ProcessDetail:
    """Get detailed process information"""
    try:
        proc = psutil.Process(pid)
        
        # Get connections safely
        try:
            connections = [
                {
                    "fd": conn.fd,
                    "family": str(conn.family),
                    "type": str(conn.type),
                    "laddr": f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None,
                    "raddr": f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                    "status": conn.status
                }
                for conn in proc.connections()
            ]
        except (psutil.AccessDenied, AttributeError):
            connections = []
        
        # Get cwd safely
        try:
            cwd = proc.cwd()
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            cwd = "N/A"
        
        # Get cmdline safely
        try:
            cmdline = proc.cmdline()
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            cmdline = []
        
        return ProcessDetail(
            pid=proc.pid,
            name=proc.name(),
            status=proc.status(),
            cpu_percent=proc.cpu_percent(interval=0.1),
            memory_percent=proc.memory_percent(),
            memory_info=proc.memory_info()._asdict(),
            username=proc.username(),
            create_time=proc.create_time(),
            cmdline=cmdline,
            cwd=cwd,
            num_threads=proc.num_threads(),
            connections=connections
        )
    
    except psutil.NoSuchProcess:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Process {pid} not found"
        )
    except psutil.AccessDenied:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied to process {pid}"
        )
    except Exception as e:
        logger.error(f"Failed to get process {pid}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get process: {str(e)}"
        )


@router.delete("/{pid}")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def kill_process(
    pid: int,
    request: Request,
    signal_type: int = signal.SIGTERM,
    current_user: dict = Depends(get_current_user)
) -> Dict:
    """Kill a process"""
    try:
        proc = psutil.Process(pid)
        process_name = proc.name()
        
        # Send signal
        proc.send_signal(signal_type)
        
        logger.warning(
            f"Process {pid} ({process_name}) killed by {current_user['username']} "
            f"with signal {signal_type}"
        )
        
        return {
            "message": f"Signal {signal_type} sent to process {pid}",
            "pid": pid,
            "name": process_name
        }
    
    except psutil.NoSuchProcess:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Process {pid} not found"
        )
    except psutil.AccessDenied:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied to kill process {pid}"
        )
    except Exception as e:
        logger.error(f"Failed to kill process {pid}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to kill process: {str(e)}"
        )


@router.get("/search/by-name")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def search_processes(
    name: str,
    request: Request,
    current_user: dict = Depends(get_current_user)
) -> List[ProcessInfo]:
    """Search processes by name"""
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'status', 'username', 'create_time']):
            try:
                if name.lower() in proc.info['name'].lower():
                    processes.append(
                        ProcessInfo(
                            pid=proc.info['pid'],
                            name=proc.info['name'],
                            status=proc.info['status'],
                            cpu_percent=proc.cpu_percent(interval=0.1),
                            memory_percent=proc.memory_percent(),
                            username=proc.info.get('username', 'N/A'),
                            create_time=proc.info['create_time']
                        )
                    )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return processes
    
    except Exception as e:
        logger.error(f"Failed to search processes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search processes: {str(e)}"
        )
