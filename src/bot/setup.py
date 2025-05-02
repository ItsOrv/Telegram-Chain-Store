from telethon import TelegramClient, events
from typing import Dict, Any, Callable, List, Awaitable
from src.utils.logger import setup_logger, log_error
from src.core.database import get_db_session
from src.core.services.user_service import UserService
from src.core.models.user import User, UserRole
from src.config.settings import get_settings
from src.bot.handlers.command_handlers import register_basic_commands
from src.bot.handlers.admin_handlers import register_admin_commands
from src.bot.handlers.seller_handlers import register_seller_commands
from src.bot.handlers.buyer_handlers import register_buyer_commands
from src.bot.handlers.cardholder_handlers import register_cardholder_commands
from src.bot.handlers.callback_router import register_callback_handlers
from src.bot.handlers.message_handler import register_message_handlers
import importlib
import inspect
import functools

# Initialize logger
logger = setup_logger("bot_setup")

# Get settings
settings = get_settings()

# Type for event handlers
EventHandler = Callable[[events.NewMessage.Event], Awaitable[Any]]

async def register_handlers(client: TelegramClient) -> None:
    """
    Register all message handlers for the bot
    
    Args:
        client: Telethon client instance
    """
    try:
        logger.info("Registering command handlers...")
        
        # Register basic handlers
        register_basic_commands(client)
        
        # Register role-specific handlers
        register_admin_commands(client)
        register_seller_commands(client)
        register_buyer_commands(client)
        register_cardholder_commands(client)
        
        # Register general handlers
        register_callback_handlers(client)
        
        # Register message handlers for text input
        await register_message_handlers(client)
        
        # Register inline handlers if exists
        try:
            from src.bot.handlers.inline_handlers import register_inline_handlers
            register_inline_handlers(client)
        except ImportError:
            logger.warning("Inline handlers module not found or not implemented yet")
        
        logger.info("All handlers registered successfully")
    except Exception as e:
        log_error("Failed to register handlers", e)
        raise

# Helper functions for generating role-specific help messages
def get_admin_help_message() -> str:
    """Get help message for admin users"""
    return (
        "🛠️ **Admin Commands**\n\n"
        "/admin - Open admin panel\n"
        "/locations - Manage delivery locations\n"
        "/users - Manage users\n"
        "/payments - Verify payments\n"
        "/profile - View your profile\n"
        "/help - Show this help message\n\n"
        "As an admin, you can:\n"
        "- Add and manage delivery locations\n"
        "- Manage users and their roles\n"
        "- Verify payments (final step)\n"
        "- View system statistics\n"
    )

def get_seller_help_message() -> str:
    """Get help message for seller users"""
    return (
        "🏪 **Seller Commands**\n\n"
        "/addproduct - Add a new product\n"
        "/myproducts - View your products\n"
        "/mysales - View your sales\n"
        "/profile - View your profile\n"
        "/wallet - Manage your wallet\n"
        "/help - Show this help message\n\n"
        "As a seller, you can:\n"
        "- Add and manage products\n"
        "- Receive orders from buyers\n"
        "- Deliver products to designated locations\n"
        "- Track your sales and earnings\n"
    )

def get_buyer_help_message() -> str:
    """Get help message for buyer users"""
    return (
        "🛒 **Buyer Commands**\n\n"
        "/products - Browse products\n"
        "/cart - View your cart\n"
        "/orders - View your orders\n"
        "/wallet - Manage your wallet\n"
        "/profile - View your profile\n"
        "/help - Show this help message\n\n"
        "As a buyer, you can:\n"
        "- Browse and purchase products\n"
        "- Pay via wallet or direct payment\n"
        "- Track your orders\n"
        "- Pick up products from designated locations\n"
    )

def get_cardholder_help_message() -> str:
    """Get help message for cardholder users"""
    return (
        "💳 **Cardholder Commands**\n\n"
        "/verify - Verify pending payments\n"
        "/report - View your performance report\n"
        "/profile - View your profile\n"
        "/help - Show this help message\n\n"
        "As a cardholder, you can:\n"
        "- Verify payments (first step)\n"
        "- View your verification history\n"
        "- Track your performance metrics\n"
    ) 