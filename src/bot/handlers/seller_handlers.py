from telethon import TelegramClient, events
from src.utils.logger import setup_logger, log_error
from src.core.database import get_db_session
from src.core.services.user_service import UserService
from src.core.models.user import UserRole
from typing import Callable, Awaitable, Any
import functools

# Initialize logger
logger = setup_logger("seller_handlers")

# Type for event handlers
EventHandler = Callable[[events.NewMessage.Event], Awaitable[Any]]

def register_seller_commands(client: TelegramClient) -> None:
    """
    Register seller-specific handlers
    
    Args:
        client: Telethon client instance
    """
    # Seller command access control decorator
    def seller_only(handler: EventHandler) -> EventHandler:
        """Decorator to restrict handler to seller users only"""
        @functools.wraps(handler)
        async def wrapped(event: events.NewMessage.Event) -> None:
            sender = await event.get_sender()
            
            with get_db_session() as session:
                user_service = UserService(session)
                user = user_service.get_by_telegram_id(sender.id)
                
                if not user or not user.is_seller:
                    await event.respond("⛔️ This command is only available to sellers.")
                    return
                
                return await handler(event)
        
        return wrapped
    
    # Add product command
    @client.on(events.NewMessage(pattern="/addproduct"))
    @seller_only
    async def add_product_handler(event: events.NewMessage.Event) -> None:
        """Handle /addproduct command"""
        try:
            # Get product handler functionality
            from src.bot.handlers.product_handler import handle_add_product
            await handle_add_product(event)
        except Exception as e:
            log_error("Error in add_product_handler", e, event.sender_id)
            await event.respond("An error occurred. Please try again later.")
    
    # My products command
    @client.on(events.NewMessage(pattern="/myproducts"))
    @seller_only
    async def my_products_handler(event: events.NewMessage.Event) -> None:
        """Handle /myproducts command"""
        try:
            # Get product handler functionality
            from src.bot.handlers.product_handler import handle_my_products
            await handle_my_products(event)
        except Exception as e:
            log_error("Error in my_products_handler", e, event.sender_id)
            await event.respond("An error occurred. Please try again later.")
    
    # My orders command (seller perspective)
    @client.on(events.NewMessage(pattern="/mysales"))
    @seller_only
    async def my_sales_handler(event: events.NewMessage.Event) -> None:
        """Handle /mysales command"""
        try:
            # Get order handler functionality
            from src.bot.handlers.order_handler import handle_my_sales
            await handle_my_sales(event)
        except Exception as e:
            log_error("Error in my_sales_handler", e, event.sender_id)
            await event.respond("An error occurred. Please try again later.")
    
    logger.info("Seller handlers registered") 