"""Authentication Router"""

import logging
from datetime import timedelta
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from api.auth.oauth import github_oauth
from api.auth.security import create_access_token, get_current_user
from api.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user: dict


@router.get("/github")
async def github_login():
    """Initiate GitHub OAuth flow"""
    auth_url = github_oauth.get_authorization_url()
    return RedirectResponse(url=auth_url)


@router.get("/github/callback")
async def github_callback(code: str = None, error: str = None):
    """GitHub OAuth callback"""
    
    if error:
        logger.error(f"GitHub OAuth error: {error}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"GitHub authentication failed: {error}"
        )
    
    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authorization code not provided"
        )
    
    try:
        # Exchange code for access token
        access_token = await github_oauth.exchange_code_for_token(code)
        
        # Get user information
        user_info = await github_oauth.get_user_info(access_token)
        
        # Create JWT token
        token_data = {
            "sub": user_info["username"],
            "email": user_info.get("email"),
            "name": user_info.get("name"),
        }
        
        jwt_token = create_access_token(
            data=token_data,
            expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
        )
        
        # Return token and user info
        return TokenResponse(
            access_token=jwt_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
            user=user_info
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed"
        )


@router.get("/verify")
async def verify_token(current_user: dict = Depends(get_current_user)):
    """Verify JWT token and return user info"""
    return {
        "valid": True,
        "user": current_user
    }


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """Logout (client should discard token)"""
    logger.info(f"User logged out: {current_user['username']}")
    return {"message": "Logged out successfully"}
