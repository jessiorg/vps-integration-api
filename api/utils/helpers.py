"""Helper utility functions"""

import os
import hashlib
import secrets
from typing import Optional
from datetime import datetime


def generate_token(length: int = 32) -> str:
    """Generate a secure random token"""
    return secrets.token_urlsafe(length)


def generate_api_key() -> str:
    """Generate an API key"""
    return f"vps_{secrets.token_urlsafe(32)}"


def hash_string(text: str) -> str:
    """Create SHA256 hash of a string"""
    return hashlib.sha256(text.encode()).hexdigest()


def format_bytes(bytes_value: int) -> str:
    """Format bytes to human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} PB"


def format_uptime(seconds: float) -> str:
    """Format uptime in seconds to human-readable format"""
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if secs > 0 or not parts:
        parts.append(f"{secs}s")
    
    return " ".join(parts)


def is_valid_path(path: str) -> bool:
    """Check if path is valid and safe"""
    try:
        # Resolve to absolute path
        abs_path = os.path.abspath(path)
        
        # Check for path traversal attempts
        if ".." in path or path != abs_path:
            return False
        
        return True
    except Exception:
        return False


def get_file_extension(filename: str) -> Optional[str]:
    """Get file extension from filename"""
    parts = filename.rsplit('.', 1)
    return parts[1].lower() if len(parts) > 1 else None


def timestamp_to_datetime(timestamp: float) -> datetime:
    """Convert Unix timestamp to datetime"""
    return datetime.fromtimestamp(timestamp)


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers, return default if division by zero"""
    try:
        return numerator / denominator if denominator != 0 else default
    except (TypeError, ZeroDivisionError):
        return default
