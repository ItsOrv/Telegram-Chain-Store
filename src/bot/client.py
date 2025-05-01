from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.errors import (
    AccessTokenExpiredError, 
    AccessTokenInvalidError,
    ApiIdInvalidError,
    SessionPasswordNeededError
)
import logging
import traceback
from typing import Optional, Dict, Any, List
from src.core.config import load_settings, BotConfig
from src.utils.logger import setup_logger

# Initialize logger
logger = setup_logger("bot_client")

class BotClient(TelegramClient):
    """
    Telegram bot client with enhanced functionality
    """
    def __init__(self, api_id: int, api_hash: str, bot_token: str):
        """
        Initialize the bot client
        
        Args:
            api_id: Telegram API ID
            api_hash: Telegram API hash
            bot_token: Bot token from BotFather
        """
        logger.info("Initializing Telegram bot client")
        super().__init__(
            StringSession(),
            api_id=api_id,
            api_hash=api_hash,
            device_model="Server",
            system_version="Linux",
            app_version="1.0.0",
            lang_code="en"
        )
        
        # Store bot token for later use
        self.bot_token = bot_token
        self.me = None
    
    async def start(self):
        """
        Start the bot client and sign in with the bot token
        """
        try:
            logger.info("Connecting to Telegram...")
            await super().connect()
            
            # Sign in with bot token if not already authorized
            if not await self.is_user_authorized():
                logger.info("Signing in with bot token")
                await super().start(bot_token=self.bot_token)
            
            # Get bot info
            self.me = await self.get_me()
            if not self.me or not self.me.bot:
                logger.error("Authentication failed: Not a bot account")
                raise ValueError("The provided token is not for a bot account")
                
            logger.info(f"Bot started successfully: @{self.me.username} (ID: {self.me.id})")
            return True
        
        except ApiIdInvalidError:
            logger.error("Authentication failed: Invalid API ID/Hash")
            raise
        except (AccessTokenExpiredError, AccessTokenInvalidError):
            logger.error("Authentication failed: Bot token invalid or expired")
            raise
        except Exception as e:
            logger.error(f"Failed to start bot: {str(e)}")
            logger.debug(traceback.format_exc())
            raise
    
    async def send_message_to_admin(self, admin_id: int, message: str) -> bool:
        """
        Send a message to the admin
        
        Args:
            admin_id: Admin's Telegram user ID
            message: Message to send
            
        Returns:
            bool: Whether the message was sent successfully
        """
        try:
            if not admin_id:
                logger.warning("No admin ID provided, can't send admin message")
                return False
                
            await self.send_message(admin_id, message)
            logger.info(f"Message sent to admin: {message[:50]}...")
            return True
        except Exception as e:
            logger.error(f"Failed to send message to admin: {str(e)}")
            return False

    @classmethod
    async def close(cls) -> None:
        """
        Safely close the client connection
        """
        if cls._instance and cls._instance.is_connected():
            try:
                await cls._instance.disconnect()
                cls._instance = None
                logger.info("Bot connection closed successfully")
            except Exception as e:
                logger.error(f"Error closing bot connection: {str(e)}")
                raise 