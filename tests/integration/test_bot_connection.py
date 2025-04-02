import pytest
import asyncio
import logging
from telethon import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty
from src.config.settings import get_settings
from src.bot.telethon_client import TelethonClient
from src.core.database import init_db, SessionLocal
from src.core.models import User, UserRole

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()

@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def client():
    """Create a test client"""
    try:
        logger.info("Initializing test client")
        client = TelegramClient(
            'test_bot_session',
            settings.API_ID,
            settings.API_HASH
        )
        await client.start(bot_token=settings.BOT_TOKEN)
        logger.info("Test client initialized successfully")
        yield client
        await client.disconnect()
    except Exception as e:
        logger.error(f"Failed to initialize test client: {e}")
        raise

@pytest.mark.asyncio
async def test_bot_connection(client):
    """Test that the bot can connect to Telegram API"""
    try:
        # Verify the bot is connected
        assert client.is_connected(), "Bot is not connected"
        
        # Get bot info
        me = await client.get_me()
        logger.info(f"Connected as {me.username} (ID: {me.id})")
        
        # Verify bot info
        assert me.bot, "Not connected as a bot"
        assert me.username == settings.BOT_USERNAME, "Bot username mismatch"
        
        logger.info("Bot connection test passed")
    except Exception as e:
        logger.error(f"Bot connection test failed: {e}")
        raise

@pytest.mark.asyncio
async def test_telethon_client_singleton():
    """Test that TelethonClient works as a singleton"""
    try:
        # Initialize the client
        await TelethonClient.initialize()
        
        # Get the client instance
        client1 = await TelethonClient.get_client()
        client2 = await TelethonClient.get_client()
        
        # Verify both instances are the same
        assert client1 is client2, "TelethonClient is not working as a singleton"
        
        # Verify the client is connected
        assert client1.is_connected(), "TelethonClient is not connected"
        
        # Close the client
        await TelethonClient.close()
        
        logger.info("TelethonClient singleton test passed")
    except Exception as e:
        logger.error(f"TelethonClient singleton test failed: {e}")
        raise

@pytest.mark.asyncio
async def test_admin_message(client):
    """Test sending a message to admin"""
    try:
        # Send a test message to admin
        message = "This is a test message from the bot connection test"
        result = await TelethonClient.send_message_to_admin(message)
        
        # Verify the message was sent
        assert result, "Failed to send message to admin"
        
        logger.info("Admin message test passed")
    except Exception as e:
        logger.error(f"Admin message test failed: {e}")
        raise

@pytest.mark.asyncio
async def test_database_connection():
    """Test database connection and basic operations"""
    try:
        # Initialize the database
        init_db()
        
        # Create a test user
        with SessionLocal() as db:
            # Check if test user exists
            test_user = db.query(User).filter(User.telegram_id == "99999999").first()
            
            if not test_user:
                # Create a test user
                test_user = User(
                    telegram_id="99999999",
                    username="test_user",
                    role=UserRole.CUSTOMER,
                    status="ACTIVE"
                )
                db.add(test_user)
                db.commit()
                logger.info("Test user created")
            else:
                logger.info("Test user already exists")
            
            # Verify the user was created
            user = db.query(User).filter(User.telegram_id == "99999999").first()
            assert user is not None, "Test user not found in database"
            assert user.username == "test_user", "Test user username mismatch"
            
            # Clean up
            db.delete(user)
            db.commit()
            logger.info("Test user deleted")
        
        logger.info("Database connection test passed")
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        raise

if __name__ == "__main__":
    # Run the tests
    pytest.main(['-xvs', __file__])