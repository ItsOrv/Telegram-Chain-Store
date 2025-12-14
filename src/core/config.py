import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Try to import the unified settings system
try:
    from src.config.settings import get_settings as get_pydantic_settings
    _USE_PYDANTIC_SETTINGS = True
except ImportError:
    _USE_PYDANTIC_SETTINGS = False

@dataclass
class DatabaseConfig:
    """Database configuration settings"""
    type: str  # sqlite, mysql, postgresql
    host: str = "localhost"
    port: int = 5432
    username: str = ""
    password: str = ""
    database: str = ""
    
    @classmethod
    def from_env(cls):
        """Load database configuration from environment variables"""
        db_type = os.getenv("DB_TYPE", "sqlite").lower()
        
        # If SQLite, we don't need most of the connection parameters
        if db_type == "sqlite":
            return cls(
                type=db_type,
                database=os.getenv("DB_NAME", "chainstore")
            )
            
        # For MySQL or PostgreSQL
        return cls(
            type=db_type,
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5432" if db_type == "postgresql" else "3306")),
            username=os.getenv("DB_USER", ""),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "chainstore")
        )

@dataclass
class BotConfig:
    """Telegram bot configuration settings"""
    api_id: int
    api_hash: str
    bot_token: str
    admin_id: Optional[int] = None
    
    @classmethod
    def from_env(cls):
        """Load bot configuration from environment variables"""
        admin_id = os.getenv("BOT_ADMIN_ID") or os.getenv("HEAD_ADMIN_ID")
        return cls(
            api_id=int(os.getenv("API_ID", "0")),
            api_hash=os.getenv("API_HASH", ""),
            bot_token=os.getenv("BOT_TOKEN", ""),
            admin_id=int(admin_id) if admin_id else None
        )

@dataclass
class Settings:
    """Application settings"""
    database: DatabaseConfig
    bot: BotConfig
    debug: bool = False
    
    @classmethod
    def from_env(cls):
        """Load all settings from environment variables"""
        return cls(
            database=DatabaseConfig.from_env(),
            bot=BotConfig.from_env(),
            debug=os.getenv("DEBUG", "false").lower() == "true"
        )

def load_settings() -> Settings:
    """
    Load configuration settings from environment variables
    Uses pydantic settings if available, otherwise falls back to dataclass-based config
    
    Returns:
        Settings object containing all configuration
    """
    # Try to use pydantic settings if available
    if _USE_PYDANTIC_SETTINGS:
        try:
            pydantic_settings = get_pydantic_settings()
            # Convert pydantic settings to dataclass format for compatibility
            db_config = DatabaseConfig(
                type=os.getenv("DB_TYPE", "mysql").lower(),
                host=pydantic_settings.DB_HOST,
                port=pydantic_settings.DB_PORT,
                username=pydantic_settings.DB_USER,
                password=pydantic_settings.DB_PASSWORD,
                database=pydantic_settings.DB_NAME
            )
            bot_config = BotConfig(
                api_id=pydantic_settings.API_ID,
                api_hash=pydantic_settings.API_HASH,
                bot_token=pydantic_settings.BOT_TOKEN,
                admin_id=pydantic_settings.HEAD_ADMIN_ID
            )
            return Settings(
                database=db_config,
                bot=bot_config,
                debug=pydantic_settings.DEBUG
            )
        except Exception:
            # Fall back to original implementation if conversion fails
            pass
    
    # Fallback to original implementation
    return Settings.from_env()

# Validate required settings
def validate_settings(settings: Settings) -> bool:
    """
    Validate that all required settings are provided
    
    Args:
        settings: The settings to validate
        
    Returns:
        True if all required settings are valid
    
    Raises:
        ValueError: If any required setting is missing
    """
    if settings.bot.api_id == 0:
        raise ValueError("API_ID is required")
    
    if not settings.bot.api_hash:
        raise ValueError("API_HASH is required")
    
    if not settings.bot.bot_token:
        raise ValueError("BOT_TOKEN is required")
    
    # For non-SQLite databases, check credentials
    if settings.database.type.lower() not in ["sqlite"] and (
        not settings.database.username or 
        not settings.database.password
    ):
        raise ValueError(f"Database credentials are required for {settings.database.type}")
    
    return True 