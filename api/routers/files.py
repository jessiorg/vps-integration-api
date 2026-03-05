"""File Operations Router"""

import os
import logging
from pathlib import Path
from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from pydantic import BaseModel

from api.auth.security import get_current_user
from api.config import settings

logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)

router = APIRouter()


class FileWrite(BaseModel):
    path: str
    content: str
    mode: str = "w"  # w, a, wb


class FileRead(BaseModel):
    content: str
    size: int
    path: str


class DirectoryListing(BaseModel):
    name: str
    path: str
    is_file: bool
    is_dir: bool
    size: int
    modified: float


def validate_path(path: str) -> Path:
    """Validate file path for security"""
    # Resolve to absolute path
    abs_path = Path(path).resolve()
    
    # Check if path is in forbidden list
    for forbidden in settings.forbidden_paths:
        forbidden_path = Path(forbidden).resolve()
        try:
            abs_path.relative_to(forbidden_path)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access to {path} is forbidden"
            )
        except ValueError:
            # Not in forbidden path
            pass
    
    # Check if path is in allowed list (if configured)
    if settings.allowed_paths:
        allowed = False
        for allowed_path in settings.allowed_paths:
            allowed_path_resolved = Path(allowed_path).resolve()
            try:
                abs_path.relative_to(allowed_path_resolved)
                allowed = True
                break
            except ValueError:
                continue
        
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access to {path} is not allowed"
            )
    
    return abs_path


@router.get("/read", response_model=FileRead)
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def read_file(
    path: str,
    request: Request,
    current_user: dict = Depends(get_current_user)
) -> FileRead:
    """Read file contents"""
    try:
        validated_path = validate_path(path)
        
        if not validated_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File {path} not found"
            )
        
        if not validated_path.is_file():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{path} is not a file"
            )
        
        # Check file size
        file_size = validated_path.stat().st_size
        if file_size > settings.max_file_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds maximum allowed size ({settings.max_file_size} bytes)"
            )
        
        content = validated_path.read_text()
        logger.info(f"File read by {current_user['username']}: {path}")
        
        return FileRead(
            content=content,
            size=file_size,
            path=str(validated_path)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to read file {path}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to read file: {str(e)}"
        )


@router.post("/write")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def write_file(
    file_data: FileWrite,
    request: Request,
    current_user: dict = Depends(get_current_user)
) -> Dict:
    """Write content to file"""
    try:
        validated_path = validate_path(file_data.path)
        
        # Check content size
        content_size = len(file_data.content.encode('utf-8'))
        if content_size > settings.max_file_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Content size exceeds maximum allowed size ({settings.max_file_size} bytes)"
            )
        
        # Create parent directories if they don't exist
        validated_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write file
        if file_data.mode == "wb":
            validated_path.write_bytes(file_data.content.encode('utf-8'))
        else:
            validated_path.write_text(file_data.content)
        
        logger.info(f"File written by {current_user['username']}: {file_data.path}")
        
        return {
            "message": "File written successfully",
            "path": str(validated_path),
            "size": content_size
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to write file {file_data.path}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to write file: {str(e)}"
        )


@router.delete("/delete")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def delete_file(
    path: str,
    request: Request,
    current_user: dict = Depends(get_current_user)
) -> Dict:
    """Delete a file"""
    try:
        validated_path = validate_path(path)
        
        if not validated_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File {path} not found"
            )
        
        if not validated_path.is_file():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{path} is not a file"
            )
        
        validated_path.unlink()
        logger.info(f"File deleted by {current_user['username']}: {path}")
        
        return {
            "message": "File deleted successfully",
            "path": str(validated_path)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete file {path}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete file: {str(e)}"
        )


@router.get("/list", response_model=List[DirectoryListing])
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def list_directory(
    path: str,
    request: Request,
    current_user: dict = Depends(get_current_user)
) -> List[DirectoryListing]:
    """List directory contents"""
    try:
        validated_path = validate_path(path)
        
        if not validated_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Directory {path} not found"
            )
        
        if not validated_path.is_dir():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{path} is not a directory"
            )
        
        items = []
        for item in validated_path.iterdir():
            stat = item.stat()
            items.append(
                DirectoryListing(
                    name=item.name,
                    path=str(item),
                    is_file=item.is_file(),
                    is_dir=item.is_dir(),
                    size=stat.st_size,
                    modified=stat.st_mtime
                )
            )
        
        logger.info(f"Directory listed by {current_user['username']}: {path}")
        return items
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list directory {path}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list directory: {str(e)}"
        )


@router.get("/exists")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def check_file_exists(
    path: str,
    request: Request,
    current_user: dict = Depends(get_current_user)
) -> Dict:
    """Check if file or directory exists"""
    try:
        validated_path = validate_path(path)
        exists = validated_path.exists()
        
        return {
            "path": str(validated_path),
            "exists": exists,
            "is_file": validated_path.is_file() if exists else None,
            "is_dir": validated_path.is_dir() if exists else None
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to check file existence {path}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check file existence: {str(e)}"
        )
