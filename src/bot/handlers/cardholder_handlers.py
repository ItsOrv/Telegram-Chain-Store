from telethon import TelegramClient, events
from src.utils.logger import setup_logger, log_error
from src.core.database import get_db_session
from src.core.services.user_service import UserService
from src.core.services.payment_service import PaymentService
from src.core.models.user import UserRole
from typing import Callable, Awaitable, Any
import functools

# Initialize logger
logger = setup_logger("cardholder_handlers")

# Type for event handlers
EventHandler = Callable[[events.NewMessage.Event], Awaitable[Any]]

def register_cardholder_commands(client: TelegramClient) -> None:
    """
    Register cardholder-specific handlers
    
    Args:
        client: Telethon client instance
    """
    # Cardholder command access control decorator
    def cardholder_only(handler: EventHandler) -> EventHandler:
        """Decorator to restrict handler to cardholder users only"""
        @functools.wraps(handler)
        async def wrapped(event: events.NewMessage.Event) -> None:
            sender = await event.get_sender()
            
            with get_db_session() as session:
                user_service = UserService(session)
                user = user_service.get_by_telegram_id(sender.id)
                
                if not user or not user.is_cardholder:
                    await event.respond("⛔️ This command is only available to cardholders.")
                    return
                
                return await handler(event)
        
        return wrapped
    
    # Verify payments command
    @client.on(events.NewMessage(pattern="/verify"))
    @cardholder_only
    async def verify_payments_handler(event: events.NewMessage.Event) -> None:
        """Handle /verify command - verify pending payments"""
        try:
            sender = await event.get_sender()
            with get_db_session() as session:
                payment_service = PaymentService(session)
                pending_payments = payment_service.get_pending_payments()
                
                if not pending_payments:
                    await event.respond("✅ No pending payments to verify.")
                    return
                
                # Here we'd show the pending payments and let the cardholder verify them
                response = f"🔄 You have {len(pending_payments)} pending payment(s) to verify:\n\n"
                
                for i, payment in enumerate(pending_payments, 1):
                    response += (
                        f"{i}. Payment ID: {payment.id}\n"
                        f"   Amount: {payment.amount}\n"
                        f"   Status: {payment.status}\n"
                        f"   Created: {payment.created_at}\n\n"
                    )
                
                # Typically we'd add inline keyboard buttons here for verification actions
                await event.respond(response)
        except Exception as e:
            log_error("Error in verify_payments_handler", e, event.sender_id)
            await event.respond("An error occurred. Please try again later.")
    
    # Performance report command
    @client.on(events.NewMessage(pattern="/report"))
    @cardholder_only
    async def performance_report_handler(event: events.NewMessage.Event) -> None:
        """Handle /report command - view performance metrics"""
        try:
            sender = await event.get_sender()
            with get_db_session() as session:
                payment_service = PaymentService(session)
                
                # Get stats for verified payments by this cardholder
                # This is a placeholder - you'd implement actual reporting logic
                total_payments = 10  # Example value
                total_amount = 1000  # Example value
                recent_payments = 3   # Example value
                
                report = (
                    "📊 **Cardholder Performance Report** 📊\n\n"
                    f"Total Payments Verified: {total_payments}\n"
                    f"Total Amount Processed: ${total_amount}\n"
                    f"Recent Activity (24h): {recent_payments} payments\n\n"
                    "Thank you for your service as a cardholder!"
                )
                
                await event.respond(report)
        except Exception as e:
            log_error("Error in performance_report_handler", e, event.sender_id)
            await event.respond("An error occurred. Please try again later.")
    
    logger.info("Cardholder handlers registered") 