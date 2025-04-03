from typing import Optional, List
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
import secrets
from pathlib import Path
import os
import logging
import urllib.parse

logger = logging.getLogger(__name__)

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

logger.debug(f"Loading .env file from: {ENV_FILE.absolute()}")

if not ENV_FILE.exists():
    raise FileNotFoundError(f"Environment file not found at {ENV_FILE}")

class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "Telegram Chain Store"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # Telegram Settings
    API_ID: int
    API_HASH: str
    BOT_TOKEN: str  # No default value
    BOT_USERNAME: str
    HEAD_ADMIN_ID: int  # Changed to int
    SUPPORT_ID: int  # اضافه کردن SUPPORT_ID
    SUPPORT_USERNAME: str
    PAYMENT_GATEWAY_TOKEN: Optional[str] = None
    
    # Database Settings
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str
    DB_PASSWORD: str = ""  # خالی برای auth_socket
    DB_NAME: str
    DB_CHARSET: str = "utf8mb4"
    DB_POOL_SIZE: int = 5
    DB_POOL_TIMEOUT: int = 30
    DB_MAX_OVERFLOW: int = 10
    DB_AUTH_SOCKET: bool = True  # فعال کردن auth_socket
    
    @property
    def DATABASE_URL(self) -> str:
        if self.DB_AUTH_SOCKET:
            return f"mysql+pymysql://{self.DB_USER}@localhost/{self.DB_NAME}?unix_socket=/var/run/mysqld/mysqld.sock&charset={self.DB_CHARSET}"
        else:
            password = urllib.parse.quote_plus(self.DB_PASSWORD)
            return f"mysql+pymysql://{self.DB_USER}:{password}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset={self.DB_CHARSET}"
    
    # Redis Settings
    REDIS_HOST: str = "127.0.0.1"  # Change from localhost to 127.0.0.1
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    REDIS_SSL: bool = False
    REDIS_SOCKET_TIMEOUT: int = 5
    
    # Security Settings
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    PASSWORD_MIN_LENGTH: int = 8
    TOKEN_EXPIRE_MINUTES: int = 60
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 5
    
    # Crypto Settings
    CRYPTO_WALLET_ADDRESS: str
    CRYPTO_NETWORK: str = "TRC20"
    CRYPTO_PAYMENT_TIMEOUT: int = 3600
    CRYPTO_MIN_AMOUNT: float = 10.0
    
    # Address Settings
    MAX_ADDRESSES_PER_CITY: int = 50
    ADDRESS_EXPIRY_HOURS: int = 24
    
    # Notification Settings
    ENABLE_NOTIFICATIONS: bool = True
    NOTIFICATION_DELAY: int = 0

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        env_file_encoding='utf-8',
        extra='ignore'
    )

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    try:
        settings = Settings()
        # Verify the loaded token
        logger.debug(f"Loaded BOT_TOKEN from env: {settings.BOT_TOKEN[:10]}...")
        return settings
    except Exception as e:
        logger.error(f"Failed to load settings: {e}")
        raise ValueError(f"Failed to load settings from {ENV_FILE}: {str(e)}")

# Clear the LRU cache for get_settings
get_settings.cache_clear() if hasattr(get_settings, 'cache_clear') else None

# Force new settings instance
settings = get_settings()
