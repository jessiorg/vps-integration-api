"""Input validation utilities"""

import re
from typing import Optional
from pathlib import Path


def validate_container_name(name: str) -> bool:
    """Validate Docker container name"""
    # Docker container names: alphanumeric, underscore, hyphen, period
    pattern = r'^[a-zA-Z0-9][a-zA-Z0-9_.-]*$'
    return bool(re.match(pattern, name)) and len(name) <= 255


def validate_image_name(image: str) -> bool:
    """Validate Docker image name"""
    # Basic validation for image names
    # Format: [registry/]repository[:tag]
    pattern = r'^[a-zA-Z0-9][a-zA-Z0-9_.-]*(/[a-zA-Z0-9][a-zA-Z0-9_.-]*)*(:[a-zA-Z0-9_.-]+)?$'
    return bool(re.match(pattern, image)) and len(image) <= 255


def validate_username(username: str) -> bool:
    """Validate username format"""
    # GitHub username format
    pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9-]){0,38}$'
    return bool(re.match(pattern, username))


def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_path(path: str, allow_absolute: bool = True) -> bool:
    """Validate file path"""
    try:
        p = Path(path)
        
        # Check for path traversal
        if ".." in str(p):
            return False
        
        # Check if absolute path is allowed
        if not allow_absolute and p.is_absolute():
            return False
        
        return True
    except Exception:
        return False


def validate_port(port: int) -> bool:
    """Validate port number"""
    return 1 <= port <= 65535


def validate_ipv4(ip: str) -> bool:
    """Validate IPv4 address"""
    pattern = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    return bool(re.match(pattern, ip))


def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing dangerous characters"""
    # Remove path separators and null bytes
    sanitized = filename.replace('/', '_').replace('\\', '_').replace('\0', '')
    # Remove leading/trailing dots and spaces
    sanitized = sanitized.strip('. ')
    # Limit length
    return sanitized[:255]


def validate_env_var_name(name: str) -> bool:
    """Validate environment variable name"""
    # Standard env var format: uppercase letters, digits, underscores
    pattern = r'^[A-Z_][A-Z0-9_]*$'
    return bool(re.match(pattern, name))
