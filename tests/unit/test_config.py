import pytest
import asyncio
import traceback
from sqlalchemy import text
from src.config.settings import get_settings
from src.core.database import get_db, engine
from src.bot.telethon_client import TelethonClient
import logging
import sys
from datetime import datetime
from pathlib import Path
from src.config import redis_config
from src.config import settings
import os

# تنظیم لاگر
def setup_logger():
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / f"test_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # فایل handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    
    # کنسول handler با رنگ
    class ColoredFormatter(logging.Formatter):
        COLORS = {
            'DEBUG': '\033[94m',    # آبی
            'INFO': '\033[92m',     # سبز
            'WARNING': '\033[93m',   # زرد
            'ERROR': '\033[91m',     # قرمز
            'CRITICAL': '\033[95m',  # بنفش
            'ENDC': '\033[0m'        # ریست رنگ
        }
        
        def format(self, record):
            if record.levelname in self.COLORS:
                record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['ENDC']}"
            return super().format(record)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(ColoredFormatter(
        '%(levelname)s - %(message)s'
    ))
    
    # تنظیم لاگر
    logger = logging.getLogger('config_test')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logger()

@pytest.mark.asyncio
async def test_settings():
    """تست تنظیمات"""
    try:
        # Verify .env file before testing
        env_file = Path(__file__).parent.parent / ".env"
        logger.debug(f"Loading settings from env file: {env_file.absolute()}")
        
        with open(env_file, 'r', encoding='utf-8') as f:
            env_content = f.read()
            logger.debug("ENV file content verification:")
            for line in env_content.splitlines():
                if line.startswith('BOT_TOKEN='):
                    logger.debug(f"Found BOT_TOKEN in .env: {line.split('=')[0]}=<token>")
        
        settings = get_settings()
        expected_bot_token = "7634461250:AAG4ozIrGq9Jc0t6_GFtAk2OmK770Qi2DyQ"
        
        # Direct comparison for debugging
        if settings.BOT_TOKEN != expected_bot_token:
            logger.error(f"""Token mismatch details:
Expected length: {len(expected_bot_token)}
Got length: {len(settings.BOT_TOKEN)}
First 10 chars match: {settings.BOT_TOKEN[:10] == expected_bot_token[:10]}
            """)
        
        assert settings.BOT_TOKEN == expected_bot_token, (
            f"BOT_TOKEN mismatch! \nExpected: {expected_bot_token}\nGot: {settings.BOT_TOKEN}"
        )
        
        # چک کردن تنظیمات تلگرام
        telegram_settings = {
            'API_ID': settings.API_ID,
            'API_HASH': settings.API_HASH[:10] + '...',  # Only show first 10 chars of API_HASH
            'BOT_TOKEN': settings.BOT_TOKEN.split(':')[0] + ':' + '***',  # Only show bot ID
            'BOT_USERNAME': settings.BOT_USERNAME
        }
        
        for key, value in telegram_settings.items():
            if not value:
                raise ValueError(f"Missing {key} in settings")
            logger.debug(f"{key}: {value}")
            
        # Log raw values for debugging
        logger.debug(f"Raw BOT_TOKEN from settings: {settings.BOT_TOKEN}")
        logger.debug(f"Raw BOT_TOKEN type: {type(settings.BOT_TOKEN)}")
        
        logger.info("✅ Settings loaded successfully")
        
    except Exception as e:
        logger.error(f"❌ Settings test failed: {str(e)}")
        logger.debug(f"Error details:\n{traceback.format_exc()}")
        raise

@pytest.mark.asyncio
async def test_database():
    """تست دیتابیس"""
    try:
        logger.info("Testing database connection...")
        db = next(get_db())
        
        # تست اتصال ساده
        result = db.execute(text("SELECT 1"))
        assert result.scalar() == 1
        
        # تست اطلاعات دیتابیس با دستورات جداگانه
        db_name = db.execute(text("SELECT DATABASE()")).scalar()
        db_user = db.execute(text("SELECT USER()")).scalar()
        db_version = db.execute(text("SELECT VERSION()")).scalar()
        
        logger.info(f"""
Database connection successful:
- Database: {db_name}
- User: {db_user}
- MySQL Version: {db_version}
        """)
        
    except Exception as e:
        logger.error(f"❌ Database test failed")
        logger.debug(f"Error details:\n{traceback.format_exc()}")
        raise
    finally:
        db.close()

@pytest.mark.asyncio
async def test_telegram():
    """تست اتصال به تلگرام"""
    try:
        logger.info("Testing Telegram connection...")
        settings = get_settings()
        client = await TelethonClient.get_client()
        
        # گرفتن اطلاعات بات
        me = await client.get_me()
        assert me is not None and me.bot, "Invalid bot account"
        
        # نمایش اطلاعات بات
        logger.info(f"""
Telegram connection successful:
- Bot Username: @{me.username}
- Bot ID: {me.id}
- First Name: {me.first_name}
- Bot: {me.bot}
        """)
        
        # تست ارسال پیام به ادمین
        test_message = "🔄 Bot Test Message\nThis is a test message from the configuration test."
        admin_id = settings.HEAD_ADMIN_ID
        logger.info(f"Sending test message to admin (ID: {admin_id})...")
        
        success = await TelethonClient.send_message_to_admin(test_message)
        if success:
            logger.info("✅ Test message sent to admin successfully")
        else:
            logger.error("❌ Failed to send test message to admin")
            
    except Exception as e:
        logger.error(f"❌ Telegram test failed")
        logger.error(f"Error message: {str(e)}")
        logger.debug(f"Error details:\n{traceback.format_exc()}")
        raise
    finally:
        await TelethonClient.close()

@pytest.mark.asyncio
async def test_redis():
    """تست اتصال به ردیس"""
    try:
        logger.info("Testing Redis connection...")
        redis_manager = redis_config.redis_config
        
        # Get client and test connection
        client = redis_manager.client
        logger.debug("Testing Redis ping...")
        response = client.ping()
        assert response == True, "Redis ping failed"
        
        # Test basic operations
        test_key = "test:connection"
        test_value = "working"
        client.set(test_key, test_value)
        retrieved = client.get(test_key)
        assert retrieved == test_value, f"Redis get/set failed. Expected {test_value}, got {retrieved}"
        
        # Cleanup
        client.delete(test_key)
        logger.info("✅ Redis connection and operations successful")
        
    except Exception as e:
        logger.error(f"❌ Redis test failed: {str(e)}")
        logger.debug(f"Error details:\n{traceback.format_exc()}")
        raise

async def run_all_tests():
    """اجرای تمام تست‌ها"""
    logger.info("\n🔄 Running configuration tests...\n")
    
    try:
        await test_settings()
        await test_database()
        await test_telegram()
        await test_redis()
        logger.info("\n✨ All tests passed successfully!")
        
    except Exception as e:
        logger.error(f"\n❌ Tests failed")
        logger.error(f"Final error: {str(e)}")
    finally:
        # نمایش مسیر فایل لاگ
        log_files = list(Path("logs").glob("test_*.log"))
        if log_files:
            latest_log = max(log_files, key=lambda x: x.stat().st_mtime)
            logger.info(f"\nComplete test log available at: {latest_log}")

if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError as e:
        if "There is no current event loop" in str(e):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
    loop.run_until_complete(run_all_tests())
