from telethon import TelegramClient, events
from src.utils.logger import setup_logger, log_error
from src.core.database import get_db_session
from src.core.services.user_service import UserService
from src.core.models.user import UserRole
from typing import Callable, Awaitable, Any
import functools

# Initialize logger
logger = setup_logger("admin_handlers")

# Type for event handlers
EventHandler = Callable[[events.NewMessage.Event], Awaitable[Any]]

def register_admin_commands(client: TelegramClient) -> None:
    """
    Register admin-specific handlers
    
    Args:
        client: Telethon client instance
    """
    # Admin command access control decorator
    def admin_only(handler: EventHandler) -> EventHandler:
        """Decorator to restrict handler to admin users only"""
        @functools.wraps(handler)
        async def wrapped(event: events.NewMessage.Event) -> None:
            sender = await event.get_sender()
            
            with get_db_session() as session:
                user_service = UserService(session)
                user = user_service.get_by_telegram_id(sender.id)
                
                if not user or not user.is_admin:
                    await event.respond("⛔️ This command is only available to admins.")
                    return
                
                return await handler(event)
        
        return wrapped
    
    # Admin panel command
    @client.on(events.NewMessage(pattern="/admin"))
    @admin_only
    async def admin_panel_handler(event: events.NewMessage.Event) -> None:
        """Handle /admin command - Admin panel"""
        try:
            # Send admin panel message
            admin_message = (
                f"🛠️ **Admin Panel**\n\n"
                f"Welcome to the admin control panel. Here you can manage the system.\n\n"
                f"Please select an option:"
            )
            
            # Send admin panel message with keyboard
            from src.bot.keyboards.admin_keyboard import get_admin_keyboard
            await event.respond(admin_message, buttons=get_admin_keyboard())
        except Exception as e:
            log_error("Error in admin_panel_handler", e, event.sender_id)
            await event.respond("An error occurred. Please try again later.")
    
    # Location management command
    @client.on(events.NewMessage(pattern="/locations"))
    @admin_only
    async def locations_handler(event: events.NewMessage.Event) -> None:
        """Handle /locations command - Location management"""
        try:
            # Send locations management message
            locations_message = (
                f"📍 **Location Management**\n\n"
                f"Here you can manage delivery locations.\n\n"
                f"Please select an option:"
            )
            
            # Send locations message with keyboard
            from src.bot.keyboards.location_keyboard import get_location_management_keyboard
            await event.respond(locations_message, buttons=get_location_management_keyboard())
        except Exception as e:
            log_error("Error in locations_handler", e, event.sender_id)
            await event.respond("An error occurred. Please try again later.")
    
    # User management command
    @client.on(events.NewMessage(pattern="/users"))
    @admin_only
    async def users_handler(event: events.NewMessage.Event) -> None:
        """Handle /users command - User management"""
        try:
            # Send user management message
            users_message = (
                f"👥 **User Management**\n\n"
                f"Here you can manage users.\n\n"
                f"Please select an option:"
            )
            
            # Send users message with keyboard
            from src.bot.keyboards.user_keyboard import get_user_management_keyboard
            await event.respond(users_message, buttons=get_user_management_keyboard())
        except Exception as e:
            log_error("Error in users_handler", e, event.sender_id)
            await event.respond("An error occurred. Please try again later.")
    
    # Payment verification command
    @client.on(events.NewMessage(pattern="/payments"))
    @admin_only
    async def payments_handler(event: events.NewMessage.Event) -> None:
        """Handle /payments command - Payment verification"""
        try:
            # Get pending payments
            with get_db_session() as session:
                from src.core.services.payment_service import PaymentService
                payment_service = PaymentService(session)
                pending_payments = payment_service.get_cardholder_verified_payments(limit=5)
                
                if not pending_payments:
                    await event.respond("There are no payments pending admin verification.")
                    return
                
                # Send payment verification message
                payments_message = (
                    f"💳 **Payment Verification**\n\n"
                    f"You have {len(pending_payments)} payment(s) waiting for verification.\n\n"
                )
                
                # Send payments message with keyboard
                from src.bot.keyboards.payment_keyboard import get_admin_payment_keyboard
                await event.respond(payments_message, buttons=get_admin_payment_keyboard(pending_payments))
        except Exception as e:
            log_error("Error in payments_handler", e, event.sender_id)
            await event.respond("An error occurred. Please try again later.")
    
    logger.info("Admin handlers registered") 