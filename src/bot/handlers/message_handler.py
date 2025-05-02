from telethon import events
from src.utils.logger import setup_logger, log_error
from src.core.database import get_db_session
from src.core.services.user_service import UserService
from src.core.services.location_service import LocationService
from typing import Dict, Any, List, Callable, Awaitable
import re

# Initialize logger
logger = setup_logger("message_handler")

# Dictionary to track user states
user_states: Dict[int, str] = {}

async def register_message_handlers(client):
    """Register message handlers for the bot"""
    logger.info("Registering message handlers")
    
    @client.on(events.NewMessage())
    async def handle_text_messages(event):
        """Handle all text messages based on user state"""
        try:
            # Ignore commands
            if event.message.text.startswith('/'):
                return
                
            sender = await event.get_sender()
            user_id = sender.id
            
            with get_db_session() as session:
                user_service = UserService(session)
                user = user_service.get_by_telegram_id(user_id)
                
                if not user:
                    logger.warning(f"Message from unknown user {user_id}")
                    return
                
                # Get user state
                user_state = user_service.get_user_state(user_id)
                
                if not user_state:
                    # User has no active state, ignore message
                    return
                
                # Log the message and state
                logger.info(f"Message from user {user_id} with state {user_state}: {event.message.text}")
                
                # Handle message based on state
                if user_state.startswith("add_province") or user_state.startswith("edit_province") or user_state.startswith("search_province"):
                    # Province management messages
                    location_service = LocationService(session)
                    from src.bot.handlers.province_management_handler import handle_province_management_messages
                    await handle_province_management_messages(event, user, user_state, user_service, location_service)
                
                elif user_state.startswith("add_city") or user_state.startswith("edit_city") or user_state.startswith("search_city"):
                    # City management messages
                    location_service = LocationService(session)
                    # This would call a function in a city management handler
                    # await handle_city_management_messages(event, user, user_state, user_service, location_service)
                    await event.respond("شهر مدیریت در حال پیاده‌سازی است.")
                    user_service.clear_user_state(user.id)
                
                elif user_state.startswith("add_seller") or user_state.startswith("edit_seller") or user_state.startswith("search_seller"):
                    # Seller management messages
                    from src.bot.handlers.seller_management_handler import handle_seller_management_messages
                    if 'handle_seller_management_messages' in globals():
                        await handle_seller_management_messages(event, user, user_state, user_service)
                    else:
                        await event.respond("مدیریت فروشنده در حال پیاده‌سازی است.")
                        user_service.clear_user_state(user.id)
                
                elif user_state.startswith("add_payment_note"):
                    # Payment note messages
                    from src.bot.handlers.pending_payments_handler import handle_payment_note_messages
                    if 'handle_payment_note_messages' in globals():
                        await handle_payment_note_messages(event, user, user_state, user_service)
                    else:
                        await event.respond("مدیریت یادداشت پرداخت در حال پیاده‌سازی است.")
                        user_service.clear_user_state(user.id)
                
                elif user_state.startswith("add_product") or user_state.startswith("edit_product"):
                    # Product management messages
                    from src.bot.handlers.product_handler import handle_product_management_messages
                    if 'handle_product_management_messages' in globals():
                        await handle_product_management_messages(event, user, user_state, user_service)
                    else:
                        await event.respond("مدیریت محصول در حال پیاده‌سازی است.")
                        user_service.clear_user_state(user.id)
                
                else:
                    # Unknown state
                    logger.warning(f"Unknown user state: {user_state}")
                    await event.respond("وضعیت نامعتبر است. لطفاً از منوها استفاده کنید.")
                    user_service.clear_user_state(user.id)
        
        except Exception as e:
            log_error("Error in handle_text_messages", e, event.sender_id if hasattr(event, 'sender_id') else None)
            await event.respond("خطایی رخ داد. لطفاً دوباره تلاش کنید.")

def update_user_state(user_id: int, state: str) -> None:
    """Update the state of a user"""
    user_states[user_id] = state
    logger.info(f"Updated user {user_id} state to {state}")

def get_user_state(user_id: int) -> str:
    """Get the current state of a user"""
    return user_states.get(user_id, "")

def clear_user_state(user_id: int) -> None:
    """Clear the state of a user"""
    if user_id in user_states:
        del user_states[user_id]
        logger.info(f"Cleared state for user {user_id}") 