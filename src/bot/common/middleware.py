from telethon import TelegramClient, events
from src.config.settings import get_settings
from src.core.database import init_db, SessionLocal
from src.core.models import User
from src.bot.utils import get_user_role
from src.bot.handlers.support_handler import SupportHandler
from src.utils.logger import (
    APP_LOGGER as logger,
    log_user_action,
    log_error,
    log_ui_event,
    log_function_execution
)
import logging
import asyncio
from functools import wraps
from typing import Callable, Any
from datetime import datetime

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

@log_function_execution()
async def setup_bot():
    """Setup and return bot client"""
    try:
        # Initialize database
        logger.info("Initializing database...")
        init_db()
        
        # Initialize telegram client
        settings = get_settings()
        logger.info(f"Setting up Telegram client with API_ID: {settings.API_ID}")
        client = TelegramClient('bot_session', settings.API_ID, settings.API_HASH)
        await client.start(bot_token=settings.BOT_TOKEN)
        logger.info(f"Bot started with username: {settings.BOT_USERNAME}")
        
        # Add event handlers
        logger.info("Setting up event handlers...")
        from src.bot.common.handlers import setup_handlers
        setup_handlers(client)
        
        # Initialize support handler with SUPPORT_ID
        logger.info(f"Setting up support handler with SUPPORT_ID: {settings.SUPPORT_ID}")
        support_handler = SupportHandler(client)
        support_handler.set_admin_id(settings.SUPPORT_ID)
        
        # Initialize handlers
        logger.info("Initializing specialized handlers...")
        from src.bot.handlers.payment_method_handler import PaymentMethodHandler
        payment_handler = PaymentMethodHandler(client)
        
        from src.bot.handlers.charge_account_handler import ChargeAccountHandler
        charge_handler = ChargeAccountHandler(client)
        
        from src.bot.handlers.delivery_handler import DeliveryHandler
        delivery_handler = DeliveryHandler(client)
        
        logger.info("Bot setup completed successfully")
        return client
        
    except Exception as e:
        log_error("Error setting up bot", e)
        raise

@log_function_execution()
def run_bot():
    """Run the bot"""
    async def main():
        client = await setup_bot()
        logger.info("Bot is running and listening for events...")
        await client.run_until_disconnected()

    asyncio.run(main())

def restrict_access(allowed_roles: list):
    """Decorator to restrict access based on user role"""
    def decorator(func):
        @wraps(func)
        async def wrapped(event, *args, **kwargs):
            user_id = event.sender_id
            with SessionLocal() as db:
                role = get_user_role(db, user_id)
                if role not in allowed_roles:
                    logger.warning(f"Access denied for user {user_id} with role {role}. Required roles: {allowed_roles}")
                    log_user_action(user_id, "ACCESS_DENIED", {
                        "required_roles": allowed_roles,
                        "user_role": role,
                        "handler": func.__name__
                    })
                    await event.respond("⛔️ Access denied")
                    return
                
                log_user_action(user_id, "ACCESS_GRANTED", {
                    "role": role,
                    "handler": func.__name__
                })
            return await func(event, *args, **kwargs)
        return wrapped
    return decorator

def log_action(func: Callable[..., Any]):
    """Decorator to log user actions"""
    @wraps(func)
    async def wrapped(event, *args, **kwargs):
        user_id = event.sender_id
        sender = await event.get_sender()
        username = sender.username if sender.username else "Unknown"
        
        logger.info(
            f"Action: {func.__name__} | "
            f"User: {user_id} | "
            f"Username: {username}"
        )
        
        log_user_action(user_id, f"HANDLER:{func.__name__}", {
            "username": username,
            "event_type": event.__class__.__name__
        })
        
        return await func(event, *args, **kwargs)
    return wrapped

def rate_limit(max_requests: int = 5, window_seconds: int = 60):
    """Rate limiting decorator for Telethon events"""
    def decorator(func):
        requests = {}
        
        @wraps(func)
        async def wrapped(event, *args, **kwargs):
            user_id = event.sender_id
            current_time = datetime.now().timestamp()
            
            # Clean old requests
            requests[user_id] = [t for t in requests.get(user_id, [])
                               if current_time - t < window_seconds]
            
            if len(requests.get(user_id, [])) >= max_requests:
                logger.warning(f"Rate limit exceeded for user {user_id} on handler {func.__name__}")
                log_user_action(user_id, "RATE_LIMIT_EXCEEDED", {
                    "handler": func.__name__,
                    "max_requests": max_requests,
                    "window_seconds": window_seconds
                })
                await event.respond("Too many requests. Please wait.")
                return
            
            requests.setdefault(user_id, []).append(current_time)
            return await func(event, *args, **kwargs)
        return wrapped
    return decorator

def error_handler(func: Callable[..., Any]):
    """Error handling decorator"""
    @wraps(func)
    async def wrapped(event, *args, **kwargs):
        try:
            return await func(event, *args, **kwargs)
        except Exception as e:
            user_id = event.sender_id
            log_error(f"Error in handler {func.__name__}", e, user_id)
            await event.respond(
                "An error occurred. Please try again later."
            )
    return wrapped

def require_location(func: Callable[..., Any]):
    """Check if user has set their location"""
    @wraps(func)
    async def wrapped(event, *args, **kwargs):
        user_id = event.sender_id
        with SessionLocal() as db:
            user = db.query(User).filter(User.telegram_id == str(user_id)).first()
            if not (user and user.cities):
                logger.info(f"User {user_id} needs to set location before accessing {func.__name__}")
                log_user_action(user_id, "LOCATION_REQUIRED", {
                    "handler": func.__name__
                })
                await event.respond(
                    "Please set your location first using /setlocation"
                )
                return
                
            log_user_action(user_id, "LOCATION_VERIFIED", {
                "cities": [city.name for city in user.cities],
                "handler": func.__name__
            })
            
        return await func(event, *args, **kwargs)
    return wrapped

def track_user_activity(func: Callable[..., Any]):
    """Track user activity for analytics"""
    @wraps(func)
    async def wrapped(event, *args, **kwargs):
        user_id = event.sender_id
        action = func.__name__
        
        log_user_action(user_id, f"ACTIVITY:{action}", {
            "timestamp": datetime.now().isoformat(),
            "event_type": event.__class__.__name__
        })
        
        # Save activity to database
        with SessionLocal() as db:
            # Add activity tracking logic here
            pass
            
        return await func(event, *args, **kwargs)
    return wrapped

def log_callback_query(func: Callable[..., Any]):
    """Decorator to log callback query interactions (button clicks)"""
    @wraps(func)
    async def wrapped(event, *args, **kwargs):
        try:
            user_id = event.sender_id
            data = event.data.decode()
            
            log_ui_event(user_id, "BUTTON_CLICK", "callback_query", {
                "data": data,
                "handler": func.__name__
            })
            
            logger.info(f"Button click: User {user_id} clicked {data}")
            return await func(event, *args, **kwargs)
        except Exception as e:
            log_error(f"Error in callback_query handler {func.__name__}", e)
            raise
    return wrapped

def log_message(func: Callable[..., Any]):
    """Decorator to log incoming messages"""
    @wraps(func)
    async def wrapped(event, *args, **kwargs):
        try:
            user_id = event.sender_id
            text = event.text if hasattr(event, 'text') else "No text"
            
            log_ui_event(user_id, "MESSAGE", "text_message", {
                "text": text,
                "handler": func.__name__
            })
            
            logger.info(f"Message: User {user_id} sent: {text}")
            return await func(event, *args, **kwargs)
        except Exception as e:
            log_error(f"Error in message handler {func.__name__}", e)
            raise
    return wrapped
