from telethon import events
from src.utils.logger import setup_logger, log_error
from src.core.database import get_db_session
from src.core.services.user_service import UserService
from src.bot.handlers.callback_router import register_callback
from typing import List
from src.core.models.user import UserRole, UserStatus

# Initialize logger
logger = setup_logger("user_callbacks")

def register_user_callbacks():
    """Register user-related callback handlers"""
    logger.info("Registering user callbacks")
    
    @register_callback("profile")
    async def handle_profile_actions(event: events.CallbackQuery.Event, params: List[str]) -> None:
        """Handle profile actions callback"""
        try:
            if len(params) < 1:
                await event.answer("Invalid action", alert=True)
                return
                
            action = params[0]  # edit, wallet, language, etc.
            sender = await event.get_sender()
            
            with get_db_session() as session:
                user_service = UserService(session)
                user = user_service.get_by_telegram_id(sender.id)
                
                if not user:
                    await event.answer("Please start the bot first", alert=True)
                    return
                
                if action == "edit":
                    # Send edit profile form
                    message = (
                        "✏️ **Edit Profile**\n\n"
                        "What would you like to update?"
                    )
                    
                    from src.bot.keyboards.profile_keyboard import get_edit_profile_keyboard
                    keyboard = get_edit_profile_keyboard()
                    
                    await event.edit(message, buttons=keyboard)
                
                elif action == "wallet":
                    # Show wallet details
                    message = (
                        f"💰 **Your Wallet**\n\n"
                        f"Current Balance: ${user.balance:.2f}\n\n"
                        f"What would you like to do with your wallet?"
                    )
                    
                    from src.bot.keyboards.profile_keyboard import get_wallet_keyboard
                    keyboard = get_wallet_keyboard()
                    
                    await event.edit(message, buttons=keyboard)
                
                elif action == "language":
                    # Show language options
                    message = (
                        f"🌐 **Language Settings**\n\n"
                        f"Current language: {user.language.upper()}\n\n"
                        f"Select your preferred language:"
                    )
                    
                    from src.bot.keyboards.profile_keyboard import get_language_keyboard
                    keyboard = get_language_keyboard()
                    
                    await event.edit(message, buttons=keyboard)
                
                elif action == "orders":
                    # Redirect to orders
                    from src.bot.handlers.order_handler import handle_user_orders
                    await handle_user_orders(event)
                
                elif action == "back":
                    # Go back to profile main view
                    profile_message = (
                        f"👤 **Your Profile**\n\n"
                        f"**ID:** {user.id}\n"
                        f"**Role:** {user.role}\n"
                        f"**Status:** {user.status}\n"
                        f"**Balance:** ${user.balance:.2f}\n"
                        f"**Joined:** {user.created_at.strftime('%Y-%m-%d')}\n"
                        f"**Last Login:** {user.last_login.strftime('%Y-%m-%d %H:%M') if user.last_login else 'N/A'}\n"
                    )
                    
                    from src.bot.keyboards.profile_keyboard import get_profile_keyboard
                    keyboard = get_profile_keyboard()
                    
                    await event.edit(profile_message, buttons=keyboard)
                
                else:
                    await event.answer("Invalid action", alert=True)
                
        except Exception as e:
            log_error("Error in handle_profile_actions", e, event.sender_id)
            await event.answer("An error occurred. Please try again later.", alert=True)
    
    @register_callback("edit_profile")
    async def handle_edit_profile(event: events.CallbackQuery.Event, params: List[str]) -> None:
        """Handle edit profile callback"""
        try:
            if len(params) < 1:
                await event.answer("Invalid field", alert=True)
                return
                
            field = params[0]  # name, phone, email, etc.
            sender = await event.get_sender()
            
            with get_db_session() as session:
                user_service = UserService(session)
                user = user_service.get_by_telegram_id(sender.id)
                
                if not user:
                    await event.answer("Please start the bot first", alert=True)
                    return
                
                # Set user state to wait for input
                user_service.set_user_state(user.id, f"edit_profile:{field}")
                
                # Prepare field-specific message
                if field == "name":
                    current = f"{user.first_name} {user.last_name or ''}"
                    message = f"Your current name: {current}\n\nPlease enter your new name:"
                
                elif field == "phone":
                    current = user.phone_number or "Not set"
                    message = f"Your current phone: {current}\n\nPlease enter your new phone number:"
                
                elif field == "email":
                    current = user.email or "Not set"
                    message = f"Your current email: {current}\n\nPlease enter your new email address:"
                
                else:
                    await event.answer("Invalid field", alert=True)
                    return
                
                # Send input prompt
                from src.bot.keyboards.profile_keyboard import get_cancel_edit_keyboard
                keyboard = get_cancel_edit_keyboard()
                
                await event.edit(f"✏️ **Edit {field.capitalize()}**\n\n{message}", buttons=keyboard)
                
        except Exception as e:
            log_error("Error in handle_edit_profile", e, event.sender_id)
            await event.answer("An error occurred. Please try again later.", alert=True)
    
    @register_callback("wallet")
    async def handle_wallet_actions(event: events.CallbackQuery.Event, params: List[str]) -> None:
        """Handle wallet actions callback"""
        try:
            if len(params) < 1:
                await event.answer("Invalid action", alert=True)
                return
                
            action = params[0]  # add_funds, history, withdraw, etc.
            sender = await event.get_sender()
            
            with get_db_session() as session:
                user_service = UserService(session)
                user = user_service.get_by_telegram_id(sender.id)
                
                if not user:
                    await event.answer("Please start the bot first", alert=True)
                    return
                
                if action == "add_funds":
                    # Show add funds options
                    message = (
                        f"💵 **Add Funds to Wallet**\n\n"
                        f"Current Balance: ${user.balance:.2f}\n\n"
                        f"Select a payment method to add funds:"
                    )
                    
                    from src.bot.keyboards.payment_keyboard import get_add_funds_keyboard
                    keyboard = get_add_funds_keyboard()
                    
                    await event.edit(message, buttons=keyboard)
                
                elif action == "history":
                    # Show transaction history
                    from src.core.services.payment_service import PaymentService
                    payment_service = PaymentService(session)
                    transactions = payment_service.get_user_transactions(user.id, limit=5)
                    
                    message = (
                        f"📊 **Transaction History**\n\n"
                        f"Current Balance: ${user.balance:.2f}\n\n"
                    )
                    
                    if not transactions:
                        message += "No recent transactions."
                    else:
                        message += "Recent transactions:\n\n"
                        
                        for i, tx in enumerate(transactions, 1):
                            message += (
                                f"{i}. {tx.transaction_type} - ${tx.amount:.2f}\n"
                                f"   Date: {tx.created_at.strftime('%Y-%m-%d %H:%M')}\n"
                                f"   Status: {tx.status}\n\n"
                            )
                    
                    from src.bot.keyboards.profile_keyboard import get_wallet_history_keyboard
                    keyboard = get_wallet_history_keyboard()
                    
                    await event.edit(message, buttons=keyboard)
                
                elif action == "withdraw":
                    # Show withdraw options
                    message = (
                        f"💸 **Withdraw Funds**\n\n"
                        f"Current Balance: ${user.balance:.2f}\n\n"
                        f"Withdraw functionality coming soon!"
                    )
                    
                    from src.bot.keyboards.profile_keyboard import get_back_to_wallet_keyboard
                    keyboard = get_back_to_wallet_keyboard()
                    
                    await event.edit(message, buttons=keyboard)
                
                elif action == "back":
                    # Go back to profile
                    await handle_profile_actions(event, ["back"])
                
                else:
                    await event.answer("Invalid action", alert=True)
                
        except Exception as e:
            log_error("Error in handle_wallet_actions", e, event.sender_id)
            await event.answer("An error occurred. Please try again later.", alert=True)
    
    @register_callback("language")
    async def handle_language_change(event: events.CallbackQuery.Event, params: List[str]) -> None:
        """Handle language change callback"""
        try:
            if len(params) < 1:
                await event.answer("Invalid language", alert=True)
                return
                
            language = params[0]  # en, fa, etc.
            sender = await event.get_sender()
            
            with get_db_session() as session:
                user_service = UserService(session)
                user = user_service.get_by_telegram_id(sender.id)
                
                if not user:
                    await event.answer("Please start the bot first", alert=True)
                    return
                
                # Update language
                user_service.update_language(user.id, language)
                
                # Send confirmation
                messages = {
                    "en": "✅ Language set to English",
                    "fa": "✅ زبان به فارسی تغییر یافت",
                    "ar": "✅ تم تعيين اللغة إلى العربية",
                    "ru": "✅ Язык изменен на русский"
                }
                
                message = messages.get(language, "✅ Language updated")
                
                # Go back to profile
                await event.answer(message)
                await handle_profile_actions(event, ["back"])
                
        except Exception as e:
            log_error("Error in handle_language_change", e, event.sender_id)
            await event.answer("An error occurred. Please try again later.", alert=True)
            
    logger.info("User callbacks registered") 