import asyncio
import sys
import traceback
import logging
import os
from pathlib import Path

from src.bot.client import BotClient
from src.bot.setup import register_handlers
from src.core.database import Database, create_tables
from src.utils.logger import setup_logger, log_error
from src.core.config import load_settings, validate_settings

# Import cart models first to ensure they're available for relationships
from src.core.models.cart import CartItem, Cart
# Then import all other models through the package __init__
from src.core.models import Base

# Initialize logger
logger = setup_logger("main")

async def setup() -> tuple[Database, BotClient]:
    """
    Initialize application components
    
    Returns:
        Tuple containing Database and BotClient instances
    """
    try:
        # Ensure logs directory exists
        Path("logs").mkdir(exist_ok=True)
        
        # Ensure data directory exists
        Path("data").mkdir(exist_ok=True)
        
        logger.info("Starting Chain Store Bot...")
        
        # Load application settings
        settings = load_settings()
        logger.info("Settings loaded from environment")
        
        # Validate settings
        validate_settings(settings)
        logger.info("Settings validated successfully")
        
        # Initialize database
        logger.info("Initializing database...")
        database = Database(settings.database)
        await database.connect()
        logger.info("Database initialization completed")
        
        # Initialize bot client
        logger.info("Initializing bot client...")
        client = BotClient(
            settings.bot.api_id,
            settings.bot.api_hash,
            settings.bot.bot_token
        )
        logger.info("Bot client initialized")
        
        # Register message handlers
        logger.info("Registering message handlers...")
        await register_handlers(client)
        logger.info("Message handlers registered")
        
        # Return initialized components
        return database, client
    except Exception as e:
        log_error("Setup failed", e)
        raise

async def main() -> None:
    """
    Main entry point of the application
    """
    database = None
    client = None
    
    try:
        # Setup application
        database, client = await setup()
        
        # Start the bot
        await client.start()
        logger.info("Bot started")
        
        # Send startup message to admin
        config = load_settings()
        admin_id = config.bot.admin_id
        if admin_id:
            try:
                await client.send_message(
                    admin_id,
                    "✅ Bot has been started successfully!"
                )
                logger.info(f"Startup message sent to admin ID: {admin_id}")
            except Exception as e:
                logger.error(f"Failed to send startup message to admin: {str(e)}")
        
        # Run the bot until disconnected
        await client.run_until_disconnected()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        log_error("An unexpected error occurred", e)
    finally:
        # Ensure graceful shutdown
        if client and client.is_connected():
            logger.info("Disconnecting bot client...")
            await client.disconnect()
            logger.info("Bot client disconnected")
        
        if database:
            logger.info("Closing database connection...")
            await database.disconnect()
            logger.info("Database connection closed")
        
        logger.info("Bot has been shut down")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        traceback.print_exc()
        sys.exit(1)
