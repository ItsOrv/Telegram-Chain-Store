from telethon import TelegramClient, events, Button
from src.utils.logger import setup_logger, log_error
from typing import List, Dict, Any, Callable, Awaitable
from src.core.database import get_db_session
import functools

# Initialize logger
logger = setup_logger("callback_router")

# Type for callback handlers
CallbackHandler = Callable[[events.CallbackQuery.Event, List[str]], Awaitable[Any]]

# Dictionary to store callback handlers
callback_handlers: Dict[str, CallbackHandler] = {}

def register_callback(action: str) -> Callable[[CallbackHandler], CallbackHandler]:
    """
    Decorator to register a callback handler for a specific action
    
    Args:
        action: The action identifier for the callback
        
    Returns:
        Decorator function
    """
    def decorator(handler: CallbackHandler) -> CallbackHandler:
        callback_handlers[action] = handler
        return handler
    
    return decorator

async def route_callback(event: events.CallbackQuery.Event, action: str, params: List[str]) -> None:
    """
    Route a callback query to the appropriate handler
    
    Args:
        event: The callback query event
        action: The action identifier from the callback data
        params: Additional parameters from the callback data
    """
    if action in callback_handlers:
        await callback_handlers[action](event, params)
    else:
        logger.warning(f"No handler registered for callback action: {action}")
        await event.answer("This action is not supported.", alert=True)

def register_callback_handlers(client: TelegramClient) -> None:
    """
    Register callback handlers for the bot
    
    Args:
        client: Telethon client instance
    """
    # Register product callbacks
    from src.bot.handlers.product_callbacks import register_product_callbacks
    register_product_callbacks()
    
    # Register cart callbacks
    from src.bot.handlers.cart_callbacks import register_cart_callbacks
    register_cart_callbacks()
    
    # Register order callbacks
    from src.bot.handlers.order_callbacks import register_order_callbacks
    register_order_callbacks()
    
    # Register payment callbacks
    from src.bot.handlers.payment_callbacks import register_payment_callbacks
    register_payment_callbacks()
    
    # Register user callbacks
    from src.bot.handlers.user_callbacks import register_user_callbacks
    register_user_callbacks()
    
    # Register admin callbacks
    from src.bot.handlers.admin_callbacks import register_admin_callbacks
    register_admin_callbacks()
    
    # Register location callbacks
    from src.bot.handlers.location_callbacks import register_location_callbacks
    register_location_callbacks()
    
    # Register province management callbacks
    from src.bot.handlers.province_management_handler import register_province_management_callbacks
    register_province_management_callbacks()
    
    # Register seller management callbacks
    from src.bot.handlers.seller_management_handler import register_seller_management_callbacks
    register_seller_management_callbacks()
    
    # Register pending payments callbacks
    from src.bot.handlers.pending_payments_handler import register_pending_payments_callbacks
    register_pending_payments_callbacks()
    
    # Register database management callbacks
    from src.bot.handlers.database_management_handler import register_database_management_callbacks
    register_database_management_callbacks()
    
    # Register navigation callback handler
    @register_callback("navigation")
    async def handle_navigation(event: events.CallbackQuery.Event, params: List[str]) -> None:
        """Handle navigation actions"""
        try:
            if not params:
                await event.answer("مقصد نامعتبر است", alert=True)
                return
                
            destination = params[0]
            
            if destination == "main_menu":
                # Show main menu
                from src.bot.keyboards.main_keyboard import get_start_keyboard
                await event.edit("منوی اصلی", buttons=get_start_keyboard())
                
            elif destination == "admin_menu":
                # Show admin menu
                from src.bot.keyboards.admin_keyboard import get_admin_keyboard
                await event.edit("پنل مدیریت", buttons=get_admin_keyboard())
                
            else:
                await event.answer("مقصد ناشناخته", alert=True)
                
        except Exception as e:
            log_error(f"Error in handle_navigation with destination {params[0] if params else 'unknown'}", e)
            await event.answer("خطا در انتقال به صفحه مورد نظر. لطفاً دوباره تلاش کنید.", alert=True)
    
    # Register user action callback handler
    @register_callback("user")
    async def handle_user_actions(event: events.CallbackQuery.Event, params: List[str]) -> None:
        """Handle user profile and settings actions"""
        try:
            if not params:
                await event.answer("Invalid user action", alert=True)
                return
                
            action = params[0]
            sender = await event.get_sender()
            
            with get_db_session() as session:
                from src.core.services.user_service import UserService
                user_service = UserService(session)
                user = user_service.get_by_telegram_id(sender.id)
                
                if not user:
                    await event.answer("Please start the bot first", alert=True)
                    return
                    
                if action == "profile":
                    # Show user profile
                    message = (
                        f"👤 **Your Profile**\n\n"
                        f"Name: {user.first_name} {user.last_name or ''}\n"
                        f"Username: @{user.username or 'Not set'}\n"
                        f"Role: {user.role}\n"
                        f"Status: {user.status}\n"
                        f"Joined: {user.created_at.strftime('%Y-%m-%d')}\n"
                    )
                    
                    from src.bot.keyboards.profile_keyboard import get_profile_keyboard
                    keyboard = get_profile_keyboard()
                    
                    await event.edit(message, buttons=keyboard)
                    
                elif action == "settings":
                    # Show user settings
                    from src.bot.keyboards.user_keyboard import get_user_settings_keyboard
                    keyboard = get_user_settings_keyboard()
                    
                    message = (
                        f"⚙️ **Settings**\n\n"
                        f"Configure your account settings."
                    )
                    
                    await event.edit(message, buttons=keyboard)
                    
                else:
                    await event.answer("Unknown action", alert=True)
                    
        except Exception as e:
            log_error(f"Error in handle_user_actions", e, event.sender_id)
            await event.answer("An error occurred. Please try again later.", alert=True)

    # Register location callback handler
    @register_callback("location")
    async def handle_location_actions(event: events.CallbackQuery.Event, params: List[str]) -> None:
        """Handle location-related actions"""
        try:
            if not params:
                await event.answer("Invalid location action", alert=True)
                return
                
            action = params[0]
            sender = await event.get_sender()
            
            with get_db_session() as session:
                from src.core.services.location_service import LocationService
                location_service = LocationService(session)
                
                from src.core.services.user_service import UserService
                user_service = UserService(session)
                user = user_service.get_by_telegram_id(sender.id)
                
                if not user:
                    await event.answer("Please start the bot first", alert=True)
                    return
                
                if action == "list":
                    # List available locations
                    city_id = int(params[1]) if len(params) > 1 else None
                    
                    if city_id:
                        # Show locations in city
                        locations = location_service.get_locations_by_city(city_id)
                        city = location_service.get_city_by_id(city_id)
                        
                        message = f"📍 **Locations in {city.name}**\n\n"
                        
                        if not locations:
                            message += "No locations available in this city yet."
                        else:
                            for i, location in enumerate(locations, 1):
                                message += (
                                    f"{i}. {location.name}\n"
                                    f"   {location.address}\n"
                                    f"   Area: {location.area}\n\n"
                                )
                        
                        from src.bot.keyboards.location_keyboard import get_locations_keyboard
                        keyboard = get_locations_keyboard(city_id)
                        
                        await event.edit(message, buttons=keyboard)
                    else:
                        # Show cities
                        cities = location_service.get_cities()
                        
                        message = "🏙️ **Available Cities**\n\nSelect a city to view available locations:\n\n"
                        
                        if not cities:
                            message += "No cities available yet."
                        else:
                            for i, city in enumerate(cities, 1):
                                message += f"{i}. {city.name}\n"
                        
                        from src.bot.keyboards.location_keyboard import get_cities_keyboard
                        keyboard = get_cities_keyboard(cities)
                        
                        await event.edit(message, buttons=keyboard)
                
                elif action == "select":
                    # Select location
                    if len(params) < 2:
                        await event.answer("Invalid location", alert=True)
                        return
                        
                    location_id = int(params[1])
                    location = location_service.get_location_by_id(location_id)
                    
                    if not location:
                        await event.answer("Location not found", alert=True)
                        return
                    
                    # Update user's selected location
                    user_service.update_selected_location(user.id, location_id)
                    
                    await event.answer(f"Selected location: {location.name}", alert=True)
                    
                    # Return to main menu
                    from src.bot.keyboards.main_keyboard import get_start_keyboard
                    await event.edit("Location selected. What would you like to do next?", buttons=get_start_keyboard())
                    
                else:
                    await event.answer("Invalid location action", alert=True)
                    
        except Exception as e:
            log_error(f"Error in handle_location_actions", e, event.sender_id)
            await event.answer("An error occurred. Please try again later.", alert=True)
    
    # Register the callback handler with the client
    @client.on(events.CallbackQuery())
    async def callback_handler(event: events.CallbackQuery.Event) -> None:
        try:
            # Parse callback data
            data = event.data.decode('utf-8')
            parts = data.split(':')
            
            if not parts:
                logger.warning("Empty callback data received")
                await event.answer("Invalid callback data", alert=True)
                return
                
            action = parts[0]
            params = parts[1:] if len(parts) > 1 else []
            
            # Log the callback
            logger.info(f"Callback received: action={action}, params={params}, user_id={event.sender_id}")
            
            # Route to the appropriate handler
            await route_callback(event, action, params)
            
        except Exception as e:
            log_error(f"Error processing callback: {str(e)}", e, event.sender_id)
            await event.answer("An error occurred processing your request. Please try again later.", alert=True)
            # Try to show an error message in chat
            try:
                await event.edit("⚠️ An error occurred processing your request. Please try again later.")
            except:
                pass

async def handle_info(event: events.CallbackQuery.Event, info_type: str) -> None:
    """
    Handle showing informational content
    
    Args:
        event: The callback query event
        info_type: Type of information to show
    """
    try:
        if info_type == "help":
            # Show help information
            message = (
                "ℹ️ **Help**\n\n"
                "Here are some useful commands:\n\n"
                "/start - Start the bot\n"
                "/help - Show this help message\n"
                "/settings - Configure your account settings\n"
                "/cancel - Cancel current operation\n\n"
                "For more help, contact our support team."
            )
            
            await event.edit(message, buttons=[
                [Button.inline("« Back", "navigation:main_menu")]
            ])
            
        elif info_type == "about":
            # Show about information
            message = (
                "ℹ️ **About**\n\n"
                "This is a Telegram Chain Store Bot that allows users to buy and sell products safely "
                "using a secure delivery system through public drop-off points.\n\n"
                "Version: 1.0.0\n"
                "Developed by: Chain Store Team\n"
            )
            
            await event.edit(message, buttons=[
                [Button.inline("« Back", "navigation:main_menu")]
            ])
            
        elif info_type == "terms":
            # Show terms and conditions
            message = (
                "📜 **Terms & Conditions**\n\n"
                "By using this bot, you agree to our terms and conditions:\n\n"
                "• All transactions are final\n"
                "• We are not responsible for lost or damaged items\n"
                "• Users must verify receipt of items\n"
                "• Sellers must deliver items within 24 hours\n"
                "• Both buyers and sellers must follow the verification protocol\n\n"
                "For full terms, visit our website."
            )
            
            await event.edit(message, buttons=[
                [Button.inline("« Back", "navigation:main_menu")]
            ])
            
        else:
            await event.answer("Invalid information type", alert=True)
            
    except Exception as e:
        log_error(f"Error in handle_info", e, event.sender_id)
        await event.answer("An error occurred. Please try again later.", alert=True) 