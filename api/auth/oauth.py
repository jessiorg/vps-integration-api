"""GitHub OAuth Authentication"""

import httpx
import logging
from typing import Optional, Dict
from fastapi import HTTPException, status

from api.config import settings

logger = logging.getLogger(__name__)


class GitHubOAuth:
    """GitHub OAuth handler"""
    
    def __init__(self):
        self.client_id = settings.github_client_id
        self.client_secret = settings.github_client_secret
        self.redirect_uri = settings.github_redirect_uri
        self.authorize_url = settings.github_authorize_url
        self.token_url = settings.github_token_url
        self.user_api_url = settings.github_user_api_url
    
    def get_authorization_url(self, state: Optional[str] = None) -> str:
        """Generate GitHub authorization URL"""
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "read:user user:email",
        }
        if state:
            params["state"] = state
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{self.authorize_url}?{query_string}"
    
    async def exchange_code_for_token(self, code: str) -> str:
        """Exchange authorization code for access token"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.token_url,
                    headers={"Accept": "application/json"},
                    data={
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "code": code,
                        "redirect_uri": self.redirect_uri,
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                if "access_token" not in data:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Failed to get access token from GitHub"
                    )
                
                return data["access_token"]
            
            except httpx.HTTPError as e:
                logger.error(f"GitHub OAuth error: {e}")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="GitHub authentication service unavailable"
                )
    
    async def get_user_info(self, access_token: str) -> Dict:
        """Get user information from GitHub"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    self.user_api_url,
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Accept": "application/json"
                    }
                )
                response.raise_for_status()
                user_data = response.json()
                
                # Verify user is in allowed list
                username = user_data.get("login")
                if settings.allowed_users and username not in settings.allowed_users:
                    logger.warning(f"Unauthorized access attempt by user: {username}")
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="User not authorized to access this API"
                    )
                
                return {
                    "username": username,
                    "email": user_data.get("email"),
                    "name": user_data.get("name"),
                    "avatar_url": user_data.get("avatar_url"),
                    "github_id": user_data.get("id"),
                }
            
            except httpx.HTTPError as e:
                logger.error(f"Failed to get user info: {e}")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Failed to retrieve user information"
                )


# Global OAuth instance
github_oauth = GitHubOAuth()
