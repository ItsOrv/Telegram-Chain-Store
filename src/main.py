import asyncio
import logging
import sys
import traceback
from src.core.database import init_db
from src.bot.common.middleware import setup_bot
from src.utils.logger import APP_LOGGER as logger, log_error

print("Starting bot initialization...")

async def main():
    """Main entry point for the Telegram Chain Store bot"""
    try:
        print("Inside main function")
        logger.info("=" * 50)
        logger.info("Starting Telegram Chain Store Bot")
        logger.info("=" * 50)
        
        # Initialize the database
        print("Initializing database...")
        logger.info("Initializing the database...")
        init_db()
        print("Database initialized")
        logger.info("Database initialized successfully")

        # Setup and start the bot
        print("Setting up bot...")
        logger.info("Setting up the bot...")
        client = await setup_bot()
        print("Bot setup completed")
        logger.info("Bot setup completed")
        logger.info("Bot is running and waiting for user interactions...")
        print("Bot is running...")
        await client.run_until_disconnected()
    except Exception as e:
        print(f"Error in main: {e}")
        print(traceback.format_exc())
        log_error("Critical error in main application", e)
        logger.critical(f"Application crashed with error: {str(e)}")
        logger.critical(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    try:
        print("Starting asyncio event loop")
        logger.info("Initializing asyncio event loop")
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped by user")
        logger.info("Bot stopped by user (KeyboardInterrupt/SystemExit)")
    except Exception as e:
        print(f"Unhandled exception: {e}")
        print(traceback.format_exc())
        log_error("Unhandled exception at top level", e)
        logger.critical(f"Unhandled exception: {str(e)}")
        logger.critical(traceback.format_exc())
        sys.exit(1)
    finally:
        print("Bot shutdown complete")
        logger.info("Bot shutdown complete")
        logger.info("=" * 50)
