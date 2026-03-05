"""Configuration Management"""

import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    api_workers: int = Field(default=4, env="API_WORKERS")
    api_reload: bool = Field(default=False, env="API_RELOAD")
    log_level: str = Field(default="info", env="LOG_LEVEL")
    
    # Application
    app_name: str = Field(default="VPS Integration API", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    
    # Security
    secret_key: str = Field(..., env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    
    # GitHub OAuth
    github_client_id: str = Field(..., env="GITHUB_CLIENT_ID")
    github_client_secret: str = Field(..., env="GITHUB_CLIENT_SECRET")
    github_redirect_uri: str = Field(..., env="GITHUB_REDIRECT_URI")
    github_authorize_url: str = Field(
        default="https://github.com/login/oauth/authorize",
        env="GITHUB_AUTHORIZE_URL"
    )
    github_token_url: str = Field(
        default="https://github.com/login/oauth/access_token",
        env="GITHUB_TOKEN_URL"
    )
    github_user_api_url: str = Field(
        default="https://api.github.com/user",
        env="GITHUB_USER_API_URL"
    )
    
    # Allowed Users
    allowed_users: List[str] = Field(default=[], env="ALLOWED_USERS")
    
    # CORS
    cors_origins: List[str] = Field(default=["*"], env="CORS_ORIGINS")
    cors_credentials: bool = Field(default=True, env="CORS_CREDENTIALS")
    cors_methods: List[str] = Field(default=["*"], env="CORS_METHODS")
    cors_headers: List[str] = Field(default=["*"], env="CORS_HEADERS")
    
    # Rate Limiting
    rate_limit_enabled: bool = Field(default=True, env="RATE_LIMIT_ENABLED")
    rate_limit_per_minute: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    
    # Docker
    docker_socket: str = Field(default="/var/run/docker.sock", env="DOCKER_SOCKET")
    docker_api_version: str = Field(default="auto", env="DOCKER_API_VERSION")
    
    # File Operations
    allowed_paths: List[str] = Field(
        default=["/data", "/var/log", "/tmp"],
        env="ALLOWED_PATHS"
    )
    forbidden_paths: List[str] = Field(
        default=["/etc/passwd", "/etc/shadow", "/root", "/etc/ssh"],
        env="FORBIDDEN_PATHS"
    )
    max_file_size: int = Field(default=10485760, env="MAX_FILE_SIZE")  # 10MB
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
        @classmethod
        def parse_env_var(cls, field_name: str, raw_val: str):
            if field_name in ["allowed_users", "cors_origins", "cors_methods", "cors_headers", "allowed_paths", "forbidden_paths"]:
                return [x.strip() for x in raw_val.split(",") if x.strip()]
            return raw_val


# Global settings instance
settings = Settings()
