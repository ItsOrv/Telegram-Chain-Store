from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import (
    AccessTokenExpiredError, 
    AccessTokenInvalidError,
    ApiIdInvalidError
)
from src.config.settings import settings
import logging
import traceback
import re

logger = logging.getLogger(__name__)

class TelethonClient:
    _instance = None
    session_name = "bot_session"

    @classmethod
    async def initialize(cls) -> None:
        """Initialize the Telegram client"""
        if cls._instance is None:
            try:
                logger.debug(f"Creating Telethon client with API_ID={settings.API_ID}")
                logger.debug(f"Using bot token starting with: {settings.BOT_TOKEN.split(':')[0]}")
                
                # Create client instance
                cls._instance = TelegramClient(
                    StringSession(),  # Using string session instead of file
                    api_id=int(settings.API_ID),  # API ID should be int from settings
                    api_hash=str(settings.API_HASH),
                    device_model="Desktop",
                    system_version="Windows 10",
                    app_version="1.0",
                    lang_code="en",
                    system_lang_code="en"
                )

                logger.debug("Starting client...")
                await cls._instance.connect()
                
                if not await cls._instance.is_user_authorized():
                    logger.debug("Signing in with bot token...")
                    await cls._instance.start(bot_token=settings.BOT_TOKEN)

                # Verify bot account
                me = await cls._instance.get_me()
                if not me or not me.bot:
                    raise ValueError("Not a valid bot account")
                
                logger.info(f"Bot initialized: @{me.username} (ID: {me.id})")
                
            except ApiIdInvalidError:
                logger.error("Invalid API ID/Hash combination")
                raise
            except (AccessTokenExpiredError, AccessTokenInvalidError):
                logger.error("Bot token is invalid or expired")
                raise
            except Exception as e:
                cls._instance = None
                logger.error(f"Failed to initialize bot: {str(e)}")
                logger.debug(f"Full error: {traceback.format_exc()}")
                raise

    @classmethod
    async def get_client(cls) -> TelegramClient:
        """Get or create client instance"""
        if cls._instance is None or not cls._instance.is_connected():
            await cls.initialize()
        return cls._instance

    @classmethod
    async def send_message_to_admin(cls, message: str) -> bool:
        """Send message to admin"""
        try:
            if cls._instance is None or not cls._instance.is_connected():
                await cls.initialize()
                
            result = await cls._instance.send_message(
                settings.HEAD_ADMIN_ID,
                message
            )
            logger.info(f"Message sent to admin successfully: {message[:20]}...")
            return True
        except Exception as e:
            logger.error(f"Failed to send message to admin: {str(e)}")
            return False

    @classmethod
    async def close(cls) -> None:
        """Safely close the client connection"""
        if cls._instance and cls._instance.is_connected():
            try:
                await cls._instance.disconnect()
                cls._instance = None
                logger.info("Bot connection closed successfully")
            except Exception as e:
                logger.error(f"Error closing bot connection: {str(e)}")
                raise
