from telethon import TelegramClient, events
from src.utils.logger import setup_logger, log_error
from src.core.database import get_db_session
from src.core.services.user_service import UserService
from src.core.models.user import UserRole
from typing import Callable, Awaitable, Any
import functools

# Initialize logger
logger = setup_logger("buyer_handlers")

# Type for event handlers
EventHandler = Callable[[events.NewMessage.Event], Awaitable[Any]]

def register_buyer_commands(client: TelegramClient) -> None:
    """
    Register buyer-specific handlers
    
    Args:
        client: Telethon client instance
    """
    # Buyer commands are available to all users, but let's add a core structure
    
    # Products command to browse products
    @client.on(events.NewMessage(pattern="/products"))
    async def products_handler(event: events.NewMessage.Event) -> None:
        """Handle /products command - browse available products"""
        try:
            # Get product handler functionality
            from src.bot.handlers.product_handler import handle_browse_products
            await handle_browse_products(event)
        except Exception as e:
            log_error("Error in products_handler", e, event.sender_id)
            await event.respond("An error occurred. Please try again later.")
    
    # Cart command
    @client.on(events.NewMessage(pattern="/cart"))
    async def cart_handler(event: events.NewMessage.Event) -> None:
        """Handle /cart command - view and manage cart"""
        try:
            # Get cart handler functionality
            from src.bot.handlers.cart_handler import handle_view_cart
            await handle_view_cart(event)
        except Exception as e:
            log_error("Error in cart_handler", e, event.sender_id)
            await event.respond("An error occurred. Please try again later.")
    
    # Orders command (buyer perspective)
    @client.on(events.NewMessage(pattern="/orders"))
    async def orders_handler(event: events.NewMessage.Event) -> None:
        """Handle /orders command - view user orders"""
        try:
            # Get order handler functionality
            from src.bot.handlers.order_handler import handle_user_orders
            await handle_user_orders(event)
        except Exception as e:
            log_error("Error in orders_handler", e, event.sender_id)
            await event.respond("An error occurred. Please try again later.")
    
    # Wallet command
    @client.on(events.NewMessage(pattern="/wallet"))
    async def wallet_handler(event: events.NewMessage.Event) -> None:
        """Handle /wallet command - view and manage wallet"""
        try:
            # Get wallet handler functionality
            from src.bot.handlers.wallet_handler import handle_wallet
            await handle_wallet(event)
        except Exception as e:
            log_error("Error in wallet_handler", e, event.sender_id)
            await event.respond("An error occurred. Please try again later.")
    
    # Profile command
    @client.on(events.NewMessage(pattern="/profile"))
    async def profile_handler(event: events.NewMessage.Event) -> None:
        """Handle /profile command - view and edit profile"""
        try:
            # Get profile handler functionality
            from src.bot.handlers.profile_handler import handle_profile
            await handle_profile(event)
        except Exception as e:
            log_error("Error in profile_handler", e, event.sender_id)
            await event.respond("An error occurred. Please try again later.")
    
    # Help command
    @client.on(events.NewMessage(pattern="/help"))
    async def help_handler(event: events.NewMessage.Event) -> None:
        """Handle /help command - show available commands"""
        try:
            sender = await event.get_sender()
            with get_db_session() as session:
                user_service = UserService(session)
                user = user_service.get_by_telegram_id(sender.id)
                
                help_text = (
                    "🛍️ **Chain Store Bot - Help** 🛍️\n\n"
                    "**Basic Commands:**\n"
                    "/start - Start the bot\n"
                    "/products - Browse products\n"
                    "/cart - View your cart\n"
                    "/orders - View your orders\n"
                    "/wallet - Manage your wallet\n"
                    "/profile - View your profile\n"
                    "/help - Show this help message\n"
                )
                
                # Add role-specific commands if applicable
                if user:
                    if user.is_admin:
                        help_text += (
                            "\n**Admin Commands:**\n"
                            "/admin - Admin control panel\n"
                            "/users - Manage users\n"
                            "/locations - Manage delivery locations\n"
                            "/payments - Verify pending payments\n"
                        )
                    
                    if user.is_seller:
                        help_text += (
                            "\n**Seller Commands:**\n"
                            "/addproduct - Add a new product\n"
                            "/myproducts - View your products\n"
                            "/mysales - View received orders\n"
                        )
                    
                    if user.is_cardholder:
                        help_text += (
                            "\n**Cardholder Commands:**\n"
                            "/verify - Verify payments\n"
                            "/report - View performance report\n"
                        )
                
                await event.respond(help_text)
        except Exception as e:
            log_error("Error in help_handler", e, event.sender_id)
            await event.respond("An error occurred. Please try again later.")
    
    logger.info("Buyer handlers registered") 