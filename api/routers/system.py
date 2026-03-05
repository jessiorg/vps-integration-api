"""System Monitoring Router"""

import platform
import psutil
import logging
from typing import Dict, List
from fastapi import APIRouter, Depends, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from pydantic import BaseModel

from api.auth.security import get_current_user
from api.config import settings

logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)

router = APIRouter()


class SystemInfo(BaseModel):
    hostname: str
    platform: str
    platform_release: str
    architecture: str
    processor: str
    cpu_count: int
    cpu_freq: dict
    memory_total: int
    memory_total_gb: float
    disk_total: int
    disk_total_gb: float
    boot_time: float


class CPUInfo(BaseModel):
    usage_percent: float
    count: int
    per_cpu_percent: List[float]
    freq_current: float
    freq_min: float
    freq_max: float


class MemoryInfo(BaseModel):
    total: int
    available: int
    used: int
    percent: float
    total_gb: float
    used_gb: float
    available_gb: float


class DiskInfo(BaseModel):
    total: int
    used: int
    free: int
    percent: float
    total_gb: float
    used_gb: float
    free_gb: float


class NetworkStats(BaseModel):
    bytes_sent: int
    bytes_recv: int
    packets_sent: int
    packets_recv: int
    errin: int
    errout: int
    dropin: int
    dropout: int


@router.get("/info", response_model=SystemInfo)
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def get_system_info(
    request: Request,
    current_user: dict = Depends(get_current_user)
) -> SystemInfo:
    """Get system information"""
    try:
        cpu_freq = psutil.cpu_freq()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return SystemInfo(
            hostname=platform.node(),
            platform=platform.system(),
            platform_release=platform.release(),
            architecture=platform.machine(),
            processor=platform.processor() or "Unknown",
            cpu_count=psutil.cpu_count(),
            cpu_freq={
                "current": cpu_freq.current if cpu_freq else 0,
                "min": cpu_freq.min if cpu_freq else 0,
                "max": cpu_freq.max if cpu_freq else 0
            },
            memory_total=memory.total,
            memory_total_gb=round(memory.total / (1024**3), 2),
            disk_total=disk.total,
            disk_total_gb=round(disk.total / (1024**3), 2),
            boot_time=psutil.boot_time()
        )
    except Exception as e:
        logger.error(f"Failed to get system info: {e}")
        raise


@router.get("/cpu", response_model=CPUInfo)
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def get_cpu_info(
    request: Request,
    current_user: dict = Depends(get_current_user)
) -> CPUInfo:
    """Get CPU usage information"""
    try:
        cpu_freq = psutil.cpu_freq()
        return CPUInfo(
            usage_percent=psutil.cpu_percent(interval=1),
            count=psutil.cpu_count(),
            per_cpu_percent=psutil.cpu_percent(interval=1, percpu=True),
            freq_current=cpu_freq.current if cpu_freq else 0,
            freq_min=cpu_freq.min if cpu_freq else 0,
            freq_max=cpu_freq.max if cpu_freq else 0
        )
    except Exception as e:
        logger.error(f"Failed to get CPU info: {e}")
        raise


@router.get("/memory", response_model=MemoryInfo)
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def get_memory_info(
    request: Request,
    current_user: dict = Depends(get_current_user)
) -> MemoryInfo:
    """Get memory usage information"""
    try:
        memory = psutil.virtual_memory()
        return MemoryInfo(
            total=memory.total,
            available=memory.available,
            used=memory.used,
            percent=memory.percent,
            total_gb=round(memory.total / (1024**3), 2),
            used_gb=round(memory.used / (1024**3), 2),
            available_gb=round(memory.available / (1024**3), 2)
        )
    except Exception as e:
        logger.error(f"Failed to get memory info: {e}")
        raise


@router.get("/disk", response_model=DiskInfo)
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def get_disk_info(
    request: Request,
    path: str = "/",
    current_user: dict = Depends(get_current_user)
) -> DiskInfo:
    """Get disk usage information"""
    try:
        disk = psutil.disk_usage(path)
        return DiskInfo(
            total=disk.total,
            used=disk.used,
            free=disk.free,
            percent=disk.percent,
            total_gb=round(disk.total / (1024**3), 2),
            used_gb=round(disk.used / (1024**3), 2),
            free_gb=round(disk.free / (1024**3), 2)
        )
    except Exception as e:
        logger.error(f"Failed to get disk info for {path}: {e}")
        raise


@router.get("/network", response_model=NetworkStats)
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def get_network_stats(
    request: Request,
    current_user: dict = Depends(get_current_user)
) -> NetworkStats:
    """Get network statistics"""
    try:
        net_io = psutil.net_io_counters()
        return NetworkStats(
            bytes_sent=net_io.bytes_sent,
            bytes_recv=net_io.bytes_recv,
            packets_sent=net_io.packets_sent,
            packets_recv=net_io.packets_recv,
            errin=net_io.errin,
            errout=net_io.errout,
            dropin=net_io.dropin,
            dropout=net_io.dropout
        )
    except Exception as e:
        logger.error(f"Failed to get network stats: {e}")
        raise


@router.get("/uptime")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def get_uptime(
    request: Request,
    current_user: dict = Depends(get_current_user)
) -> Dict:
    """Get system uptime"""
    try:
        boot_time = psutil.boot_time()
        import time
        uptime_seconds = time.time() - boot_time
        
        days = int(uptime_seconds // 86400)
        hours = int((uptime_seconds % 86400) // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        
        return {
            "boot_time": boot_time,
            "uptime_seconds": uptime_seconds,
            "uptime_formatted": f"{days}d {hours}h {minutes}m"
        }
    except Exception as e:
        logger.error(f"Failed to get uptime: {e}")
        raise
