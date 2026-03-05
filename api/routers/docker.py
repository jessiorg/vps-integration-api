"""Docker Management Router"""

import logging
from typing import List, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from pydantic import BaseModel
import docker
from docker.errors import DockerException, NotFound, APIError

from api.auth.security import get_current_user
from api.config import settings

logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)

router = APIRouter()

# Docker client
try:
    docker_client = docker.DockerClient(base_url=f"unix://{settings.docker_socket}")
except Exception as e:
    logger.error(f"Failed to initialize Docker client: {e}")
    docker_client = None


class ContainerInfo(BaseModel):
    id: str
    name: str
    status: str
    image: str
    created: str
    ports: dict


class ContainerCreate(BaseModel):
    image: str
    name: Optional[str] = None
    command: Optional[str] = None
    environment: Optional[Dict[str, str]] = None
    ports: Optional[Dict[str, int]] = None
    volumes: Optional[Dict[str, Dict[str, str]]] = None
    detach: bool = True


def get_docker_client():
    """Get Docker client or raise exception"""
    if docker_client is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Docker service unavailable"
        )
    return docker_client


@router.get("/containers", response_model=List[ContainerInfo])
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def list_containers(
    request: Request,
    all: bool = False,
    current_user: dict = Depends(get_current_user),
    client: docker.DockerClient = Depends(get_docker_client)
) -> List[ContainerInfo]:
    """List Docker containers"""
    try:
        containers = client.containers.list(all=all)
        return [
            ContainerInfo(
                id=container.id,
                name=container.name,
                status=container.status,
                image=container.image.tags[0] if container.image.tags else container.image.id,
                created=container.attrs['Created'],
                ports=container.attrs['NetworkSettings']['Ports'] or {}
            )
            for container in containers
        ]
    except DockerException as e:
        logger.error(f"Docker error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list containers: {str(e)}"
        )


@router.get("/containers/{container_id}")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def get_container(
    container_id: str,
    request: Request,
    current_user: dict = Depends(get_current_user),
    client: docker.DockerClient = Depends(get_docker_client)
) -> Dict:
    """Get container details"""
    try:
        container = client.containers.get(container_id)
        return {
            "id": container.id,
            "name": container.name,
            "status": container.status,
            "image": container.image.tags[0] if container.image.tags else container.image.id,
            "created": container.attrs['Created'],
            "state": container.attrs['State'],
            "network_settings": container.attrs['NetworkSettings'],
            "mounts": container.attrs['Mounts'],
            "config": container.attrs['Config']
        }
    except NotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Container {container_id} not found"
        )
    except DockerException as e:
        logger.error(f"Docker error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get container: {str(e)}"
        )


@router.post("/containers/{container_id}/start")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def start_container(
    container_id: str,
    request: Request,
    current_user: dict = Depends(get_current_user),
    client: docker.DockerClient = Depends(get_docker_client)
) -> Dict:
    """Start a container"""
    try:
        container = client.containers.get(container_id)
        container.start()
        logger.info(f"Container {container_id} started by {current_user['username']}")
        return {"message": f"Container {container_id} started successfully"}
    except NotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Container {container_id} not found"
        )
    except APIError as e:
        logger.error(f"Failed to start container: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start container: {str(e)}"
        )


@router.post("/containers/{container_id}/stop")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def stop_container(
    container_id: str,
    request: Request,
    timeout: int = 10,
    current_user: dict = Depends(get_current_user),
    client: docker.DockerClient = Depends(get_docker_client)
) -> Dict:
    """Stop a container"""
    try:
        container = client.containers.get(container_id)
        container.stop(timeout=timeout)
        logger.info(f"Container {container_id} stopped by {current_user['username']}")
        return {"message": f"Container {container_id} stopped successfully"}
    except NotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Container {container_id} not found"
        )
    except APIError as e:
        logger.error(f"Failed to stop container: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop container: {str(e)}"
        )


@router.post("/containers/{container_id}/restart")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def restart_container(
    container_id: str,
    request: Request,
    timeout: int = 10,
    current_user: dict = Depends(get_current_user),
    client: docker.DockerClient = Depends(get_docker_client)
) -> Dict:
    """Restart a container"""
    try:
        container = client.containers.get(container_id)
        container.restart(timeout=timeout)
        logger.info(f"Container {container_id} restarted by {current_user['username']}")
        return {"message": f"Container {container_id} restarted successfully"}
    except NotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Container {container_id} not found"
        )
    except APIError as e:
        logger.error(f"Failed to restart container: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to restart container: {str(e)}"
        )


@router.delete("/containers/{container_id}")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def remove_container(
    container_id: str,
    request: Request,
    force: bool = False,
    current_user: dict = Depends(get_current_user),
    client: docker.DockerClient = Depends(get_docker_client)
) -> Dict:
    """Remove a container"""
    try:
        container = client.containers.get(container_id)
        container.remove(force=force)
        logger.info(f"Container {container_id} removed by {current_user['username']}")
        return {"message": f"Container {container_id} removed successfully"}
    except NotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Container {container_id} not found"
        )
    except APIError as e:
        logger.error(f"Failed to remove container: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove container: {str(e)}"
        )


@router.get("/containers/{container_id}/logs")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def get_container_logs(
    container_id: str,
    request: Request,
    lines: int = 100,
    current_user: dict = Depends(get_current_user),
    client: docker.DockerClient = Depends(get_docker_client)
) -> Dict:
    """Get container logs"""
    try:
        container = client.containers.get(container_id)
        logs = container.logs(tail=lines, timestamps=True).decode('utf-8')
        return {
            "container_id": container_id,
            "logs": logs
        }
    except NotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Container {container_id} not found"
        )
    except DockerException as e:
        logger.error(f"Failed to get logs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get container logs: {str(e)}"
        )


@router.get("/containers/{container_id}/stats")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def get_container_stats(
    container_id: str,
    request: Request,
    current_user: dict = Depends(get_current_user),
    client: docker.DockerClient = Depends(get_docker_client)
) -> Dict:
    """Get container stats"""
    try:
        container = client.containers.get(container_id)
        stats = container.stats(stream=False)
        return stats
    except NotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Container {container_id} not found"
        )
    except DockerException as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get container stats: {str(e)}"
        )


@router.post("/containers")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def create_container(
    container_data: ContainerCreate,
    request: Request,
    current_user: dict = Depends(get_current_user),
    client: docker.DockerClient = Depends(get_docker_client)
) -> Dict:
    """Create a new container"""
    try:
        container = client.containers.run(
            image=container_data.image,
            name=container_data.name,
            command=container_data.command,
            environment=container_data.environment,
            ports=container_data.ports,
            volumes=container_data.volumes,
            detach=container_data.detach
        )
        logger.info(f"Container created by {current_user['username']}: {container.id}")
        return {
            "message": "Container created successfully",
            "container_id": container.id,
            "name": container.name
        }
    except APIError as e:
        logger.error(f"Failed to create container: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create container: {str(e)}"
        )


@router.get("/images")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def list_images(
    request: Request,
    current_user: dict = Depends(get_current_user),
    client: docker.DockerClient = Depends(get_docker_client)
) -> List[Dict]:
    """List Docker images"""
    try:
        images = client.images.list()
        return [
            {
                "id": image.id,
                "tags": image.tags,
                "created": image.attrs['Created'],
                "size": image.attrs['Size']
            }
            for image in images
        ]
    except DockerException as e:
        logger.error(f"Failed to list images: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list images: {str(e)}"
        )
