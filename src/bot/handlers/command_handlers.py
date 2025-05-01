from telethon import TelegramClient, events
from src.utils.logger import setup_logger, log_error
from src.core.database import get_db_session
from src.core.services.user_service import UserService
from src.core.models.user import UserRole
from src.config.settings import get_settings
from typing import Callable, Awaitable, Any
import functools

# Initialize logger
logger = setup_logger("command_handlers")

# Get settings
settings = get_settings()

# Type for event handlers
EventHandler = Callable[[events.NewMessage.Event], Awaitable[Any]]

def register_basic_commands(client: TelegramClient) -> None:
    """
    Register basic command handlers
    
    Args:
        client: Telethon client instance
    """
    # Start command handler
    @client.on(events.NewMessage(pattern="/start"))
    async def start_handler(event: events.NewMessage.Event) -> None:
        """Handle /start command"""
        try:
            # Get user info
            sender = await event.get_sender()
            
            # Create or update user in database
            with get_db_session() as session:
                user_service = UserService(session)
                user = user_service.get_by_telegram_id(sender.id)
                
                if not user:
                    # Check if user is the admin
                    is_admin = (sender.id == settings.HEAD_ADMIN_ID)
                    
                    # Create new user with BUYER role by default or ADMIN if it matches HEAD_ADMIN_ID
                    user_data = {
                        "telegram_id": sender.id,
                        "username": sender.username,
                        "first_name": sender.first_name,
                        "last_name": sender.last_name if hasattr(sender, "last_name") else None,
                        "role": UserRole.ADMIN if is_admin else UserRole.BUYER
                    }
                    
                    user = user_service.create_user(user_data)
                    
                    welcome_message = (
                        f"👋 Welcome to Chain Store Bot!\n\n"
                        f"This is a secure marketplace with manual payment verification "
                        f"and location-based delivery.\n\n"
                    )
                    
                    if is_admin:
                        welcome_message += "You have been registered as an admin."
                    else:
                        welcome_message += "You have been registered as a customer."
                else:
                    # Update last login time
                    user_service.update_last_login(user.id)
                    
                    welcome_message = (
                        f"👋 Welcome back to Chain Store Bot!\n\n"
                        f"Your current role: {user.role}\n"
                        f"Your current balance: {user.balance}\n\n"
                        f"Use /help to see available commands."
                    )
            
            # Send welcome message with the appropriate keyboard based on user role
            from src.bot.keyboards.main_keyboard import (
                get_start_keyboard, 
                get_admin_start_keyboard, 
                get_seller_start_keyboard,
                get_cardholder_start_keyboard
            )
            
            # Select the appropriate keyboard based on user role
            if user.is_admin:
                keyboard = get_admin_start_keyboard()
            elif user.is_seller:
                keyboard = get_seller_start_keyboard()
            elif user.is_cardholder:
                keyboard = get_cardholder_start_keyboard()
            else:  # Default to buyer keyboard
                keyboard = get_start_keyboard()
                
            await event.respond(welcome_message, buttons=keyboard)
        except Exception as e:
            log_error("Error in start_handler", e, event.sender_id)
            await event.respond("An error occurred. Please try again later.")
    
    # Help command handler
    @client.on(events.NewMessage(pattern="/help"))
    async def help_handler(event: events.NewMessage.Event) -> None:
        """Handle /help command"""
        try:
            # Get user info
            sender = await event.get_sender()
            
            # Get user role
            with get_db_session() as session:
                user_service = UserService(session)
                user = user_service.get_by_telegram_id(sender.id)
                
                if not user:
                    await event.respond(
                        "You need to start the bot first. Please use /start command."
                    )
                    return
                
                # Generate help message based on user role
                if user.is_admin:
                    help_message = get_admin_help_message()
                elif user.is_seller:
                    help_message = get_seller_help_message()
                elif user.is_cardholder:
                    help_message = get_cardholder_help_message()
                else:  # Default to buyer
                    help_message = get_buyer_help_message()
                
                await event.respond(help_message)
        except Exception as e:
            log_error("Error in help_handler", e, event.sender_id)
            await event.respond("An error occurred. Please try again later.")
    
    # Profile command handler
    @client.on(events.NewMessage(pattern="/profile"))
    async def profile_handler(event: events.NewMessage.Event) -> None:
        """Handle /profile command"""
        try:
            # Get user info
            sender = await event.get_sender()
            
            # Get user profile
            with get_db_session() as session:
                user_service = UserService(session)
                user = user_service.get_by_telegram_id(sender.id)
                
                if not user:
                    await event.respond(
                        "You need to start the bot first. Please use /start command."
                    )
                    return
                
                # Generate profile message
                profile_message = (
                    f"👤 **Your Profile**\n\n"
                    f"**ID:** {user.id}\n"
                    f"**Role:** {user.role}\n"
                    f"**Status:** {user.status}\n"
                    f"**Balance:** {user.balance}\n"
                    f"**Joined:** {user.joined_at.strftime('%Y-%m-%d')}\n"
                    f"**Last Login:** {user.last_login.strftime('%Y-%m-%d %H:%M')}\n"
                )
                
                # Send profile message
                from src.bot.keyboards.profile_keyboard import get_profile_keyboard
                await event.respond(profile_message, buttons=get_profile_keyboard())
        except Exception as e:
            log_error("Error in profile_handler", e, event.sender_id)
            await event.respond("An error occurred. Please try again later.")
    
    logger.info("Basic command handlers registered")

# Help message functions
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
        "/browse - Browse products\n"
        "/cart - View your cart\n"
        "/myorders - View your orders\n"
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
        "/profile - View your profile\n"
        "/help - Show this help message\n\n"
        "As a cardholder, you can:\n"
        "- Verify payments (first step)\n"
        "- View your verification history\n"
    ) 