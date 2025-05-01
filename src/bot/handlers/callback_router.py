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
                    await event.answer("Unknown action", alert=True)
                    
        except Exception as e:
            log_error(f"Error in handle_location_actions", e, event.sender_id)
            await event.answer("An error occurred. Please try again later.", alert=True)
    
    # The main callback handler
    @client.on(events.CallbackQuery())
    async def callback_handler(event: events.CallbackQuery.Event) -> None:
        """Handle callback queries from inline buttons"""
        try:
            # The callback data is a string that needs to be parsed
            data = event.data.decode('utf-8')
            
            # Parse callback data format: action:param1:param2...
            parts = data.split(':')
            action = parts[0]
            params = parts[1:] if len(parts) > 1 else []
            
            # Route callback to appropriate handler
            await route_callback(event, action, params)
        except Exception as e:
            sender = await event.get_sender()
            log_error(f"Error in callback_handler with data {event.data.decode('utf-8')}", e, sender.id)
            await event.answer("An error occurred. Please try again later.", alert=True)
    
    logger.info("Callback handlers registered")

async def handle_info(event: events.CallbackQuery.Event, info_type: str) -> None:
    """
    Handle information display actions
    
    Args:
        event: Callback query event
        info_type: Type of information to display
    """
    try:
        if info_type == "terms":
            # Display terms and conditions
            terms_text = (
                "**شرایط و قوانین**\n\n"
                "با استفاده از این ربات، شما موافقت می‌کنید که از قوانین زیر پیروی کنید:\n\n"
                "1. تمام تراکنش‌ها به صورت دستی تایید می‌شوند\n"
                "2. تحویل کالا فقط در مکان‌های تعیین شده انجام می‌شود\n"
                "3. مدیران ربات مسئولیتی در قبال سوء استفاده ندارند\n"
                "4. فروش کالاهای ممنوعه مجاز نیست\n\n"
                "برای مشاهده قوانین کامل، لطفاً به وب‌سایت ما مراجعه کنید."
            )
            await event.edit(terms_text, buttons=[Button.inline("« بازگشت", "navigation:main_menu")])
            
        elif info_type == "about":
            # Display about information
            about_text = (
                "**درباره ربات Chain Store**\n\n"
                "این ربات یک بازارچه امن با سیستم تایید پرداخت دستی "
                "و سیستم تحویل مبتنی بر مکان فراهم می‌کند.\n\n"
                "نسخه: 1.0.0\n"
                "ارتباط: @admin_contact"
            )
            await event.edit(about_text, buttons=[Button.inline("« بازگشت", "navigation:main_menu")])
            
        elif info_type == "help":
            # Display help information
            help_text = (
                "**راهنمای استفاده**\n\n"
                "نحوه استفاده از ربات:\n\n"
                "1. **ثبت‌نام** به عنوان خریدار، فروشنده یا کاردار\n"
                "2. **مشاهده محصولات** اگر خریدار هستید\n"
                "3. **افزودن محصول** اگر فروشنده هستید\n"
                "4. **تایید پرداخت‌ها** اگر کاردار هستید\n\n"
                "از دستور /help برای راهنمای اختصاصی هر نقش استفاده کنید."
            )
            await event.edit(help_text, buttons=[Button.inline("« بازگشت", "navigation:main_menu")])
            
        else:
            await event.answer("نوع اطلاعات ناشناخته است", alert=True)
            
    except Exception as e:
        log_error(f"Error in handle_info with info_type {info_type}", e)
        await event.answer("خطا در نمایش اطلاعات. لطفاً دوباره تلاش کنید.", alert=True) 