from telethon import events, Button
from src.utils.logger import setup_logger, log_error
from src.core.database import get_db_session
from src.core.services.location_service import LocationService
from src.core.services.user_service import UserService
from src.bot.handlers.callback_router import register_callback
from typing import List, Dict, Any

# Initialize logger
logger = setup_logger("location_callbacks")

def register_location_callbacks():
    """Register location-related callback handlers"""
    logger.info("Registering location callbacks")
    
    @register_callback("admin:locations")
    async def handle_admin_locations(event: events.CallbackQuery.Event, params: List[str]) -> None:
        """Handle admin locations management callback"""
        try:
            if not params:
                # Show main locations management keyboard
                from src.bot.keyboards.admin_keyboard import get_admin_locations_keyboard
                await event.edit("🏙️ **مدیریت مکان‌های تحویل**\n\nاز این بخش می‌توانید مکان‌های تحویل، شهرها، استان‌ها و مناطق را مدیریت کنید.", 
                                buttons=get_admin_locations_keyboard())
                return
                
            action = params[0]  # provinces, cities, areas, etc.
            sender = await event.get_sender()
            
            with get_db_session() as session:
                user_service = UserService(session)
                user = user_service.get_by_telegram_id(sender.id)
                
                if not user:
                    await event.answer("لطفا ابتدا ربات را استارت کنید", alert=True)
                    return
                
                # Check if user is admin
                if not user.is_admin:
                    await event.answer("شما مجوز دسترسی به پنل مدیریت را ندارید", alert=True)
                    return
                
                location_service = LocationService(session)
                
                if action == "provinces":
                    # Handle provinces management
                    await handle_provinces_management(event, params[1:] if len(params) > 1 else [], location_service)
                
                elif action == "cities":
                    # Handle cities management
                    await handle_cities_management(event, params[1:] if len(params) > 1 else [], location_service)
                
                elif action == "areas":
                    # Handle areas management
                    await handle_areas_management(event, params[1:] if len(params) > 1 else [], location_service)
                
                elif action == "places":
                    # Handle places management
                    await handle_places_management(event, params[1:] if len(params) > 1 else [], location_service)
                
                elif action == "add":
                    # Handle adding new location
                    await handle_add_location(event, params[1:] if len(params) > 1 else [], location_service, user)
                
                elif action == "list":
                    # Handle listing locations
                    await handle_list_locations(event, params[1:] if len(params) > 1 else [], location_service)
                
                elif action == "delete":
                    # Handle deleting location
                    await handle_delete_location(event, params[1:] if len(params) > 1 else [], location_service, user)
                
                elif action == "edit":
                    # Handle editing location
                    await handle_edit_location(event, params[1:] if len(params) > 1 else [], location_service, user)
                
                else:
                    await event.answer("عملیات نامعتبر", alert=True)
        
        except Exception as e:
            log_error("Error in handle_admin_locations", e, event.sender_id)
            await event.answer("خطایی رخ داد. لطفاً دوباره تلاش کنید.", alert=True)

async def handle_provinces_management(event: events.CallbackQuery.Event, params: List[str], location_service: LocationService) -> None:
    """Handle provinces management"""
    try:
        if not params:
            # Show provinces list
            provinces = location_service.get_provinces()
            
            message = "🏙️ **مدیریت استان‌ها**\n\n"
            
            if not provinces:
                message += "هیچ استانی در سیستم ثبت نشده است."
            else:
                message += "لیست استان‌های موجود:\n\n"
                for i, province in enumerate(provinces, 1):
                    message += f"{i}. {province.name} (کد: {province.id})\n"
            
            # Create keyboard for provinces management
            buttons = [
                [
                    Button.inline("➕ افزودن استان", "admin:locations:provinces:add"),
                    Button.inline("🔍 جستجوی استان", "admin:locations:provinces:search")
                ],
                [
                    Button.inline("✏️ ویرایش استان", "admin:locations:provinces:edit"),
                    Button.inline("❌ حذف استان", "admin:locations:provinces:delete")
                ],
                [
                    Button.inline("« بازگشت", "admin:locations")
                ]
            ]
            
            await event.edit(message, buttons=buttons)
        
        else:
            action = params[0]  # add, edit, delete, search
            
            if action == "add":
                # Set user state to add province and show instructions
                await event.edit("🏙️ **افزودن استان جدید**\n\nلطفاً نام استان را وارد کنید:", 
                               buttons=[[Button.inline("« بازگشت", "admin:locations:provinces")]])
                
                # Set user state to wait for province name
                from src.core.services.user_service import UserService
                with get_db_session() as session:
                    user_service = UserService(session)
                    sender = await event.get_sender()
                    user_service.set_user_state(sender.id, "add_province")
            
            elif action == "edit":
                if len(params) > 1:
                    province_id = int(params[1])
                    province = location_service.get_province_by_id(province_id)
                    
                    if province:
                        # Set user state to edit province and show instructions
                        await event.edit(f"✏️ **ویرایش استان**\n\nاستان فعلی: {province.name}\n\nلطفاً نام جدید استان را وارد کنید:", 
                                       buttons=[[Button.inline("« بازگشت", "admin:locations:provinces")]])
                        
                        # Set user state to wait for new province name
                        from src.core.services.user_service import UserService
                        with get_db_session() as session:
                            user_service = UserService(session)
                            sender = await event.get_sender()
                            user_service.set_user_state(sender.id, f"edit_province:{province_id}")
                    else:
                        await event.answer("استان مورد نظر یافت نشد", alert=True)
                        await handle_provinces_management(event, [], location_service)
                else:
                    # Show province selection for editing
                    provinces = location_service.get_provinces()
                    
                    message = "✏️ **ویرایش استان**\n\nاستان مورد نظر برای ویرایش را انتخاب کنید:"
                    
                    buttons = []
                    for province in provinces:
                        buttons.append([Button.inline(
                            f"{province.name}", 
                            f"admin:locations:provinces:edit:{province.id}"
                        )])
                    
                    buttons.append([Button.inline("« بازگشت", "admin:locations:provinces")])
                    
                    await event.edit(message, buttons=buttons)
            
            elif action == "delete":
                if len(params) > 1:
                    province_id = int(params[1])
                    
                    if len(params) > 2 and params[2] == "confirm":
                        # Confirm deletion
                        try:
                            location_service.delete_province(province_id)
                            await event.answer("استان با موفقیت حذف شد")
                            await handle_provinces_management(event, [], location_service)
                        except Exception as e:
                            await event.answer(f"خطا در حذف استان: {str(e)}", alert=True)
                            await handle_provinces_management(event, [], location_service)
                    else:
                        # Ask for confirmation
                        province = location_service.get_province_by_id(province_id)
                        
                        if province:
                            message = f"❌ **حذف استان**\n\nآیا از حذف استان «{province.name}» اطمینان دارید؟\n\nتوجه: با حذف استان، تمام شهرها و مناطق مرتبط با آن نیز حذف خواهند شد."
                            
                            buttons = [
                                [
                                    Button.inline("✅ بله، حذف شود", f"admin:locations:provinces:delete:{province_id}:confirm"),
                                    Button.inline("❌ انصراف", "admin:locations:provinces")
                                ]
                            ]
                            
                            await event.edit(message, buttons=buttons)
                        else:
                            await event.answer("استان مورد نظر یافت نشد", alert=True)
                            await handle_provinces_management(event, [], location_service)
                else:
                    # Show province selection for deletion
                    provinces = location_service.get_provinces()
                    
                    message = "❌ **حذف استان**\n\nاستان مورد نظر برای حذف را انتخاب کنید:"
                    
                    buttons = []
                    for province in provinces:
                        buttons.append([Button.inline(
                            f"{province.name}", 
                            f"admin:locations:provinces:delete:{province.id}"
                        )])
                    
                    buttons.append([Button.inline("« بازگشت", "admin:locations:provinces")])
                    
                    await event.edit(message, buttons=buttons)
            
            elif action == "search":
                # Set user state to search province and show instructions
                await event.edit("🔍 **جستجوی استان**\n\nلطفاً نام استان را برای جستجو وارد کنید:", 
                               buttons=[[Button.inline("« بازگشت", "admin:locations:provinces")]])
                
                # Set user state to wait for search query
                from src.core.services.user_service import UserService
                with get_db_session() as session:
                    user_service = UserService(session)
                    sender = await event.get_sender()
                    user_service.set_user_state(sender.id, "search_province")
            
            else:
                await event.answer("عملیات نامعتبر", alert=True)
                await handle_provinces_management(event, [], location_service)
    
    except Exception as e:
        log_error("Error in handle_provinces_management", e, event.sender_id)
        await event.answer("خطایی رخ داد. لطفاً دوباره تلاش کنید.", alert=True)

async def handle_cities_management(event: events.CallbackQuery.Event, params: List[str], location_service: LocationService) -> None:
    """Handle cities management"""
    try:
        if not params:
            # Show provinces for city selection
            provinces = location_service.get_provinces()
            
            message = "🏘️ **مدیریت شهرها**\n\nابتدا استان مورد نظر را انتخاب کنید:"
            
            buttons = []
            for province in provinces:
                buttons.append([Button.inline(
                    f"{province.name}", 
                    f"admin:locations:cities:province:{province.id}"
                )])
            
            buttons.append([Button.inline("« بازگشت", "admin:locations")])
            
            await event.edit(message, buttons=buttons)
        
        else:
            action = params[0]
            
            if action == "province":
                if len(params) > 1:
                    province_id = int(params[1])
                    province = location_service.get_province_by_id(province_id)
                    
                    if province:
                        # Show cities in this province
                        cities = location_service.get_cities_by_province(province_id)
                        
                        message = f"🏘️ **شهرهای استان {province.name}**\n\n"
                        
                        if not cities:
                            message += "هیچ شهری در این استان ثبت نشده است."
                        else:
                            message += "لیست شهرهای موجود:\n\n"
                            for i, city in enumerate(cities, 1):
                                message += f"{i}. {city.name} (کد: {city.id})\n"
                        
                        # Create keyboard for cities management
                        buttons = [
                            [
                                Button.inline("➕ افزودن شهر", f"admin:locations:cities:add:{province_id}"),
                                Button.inline("🔍 جستجوی شهر", f"admin:locations:cities:search:{province_id}")
                            ],
                            [
                                Button.inline("✏️ ویرایش شهر", f"admin:locations:cities:edit:{province_id}"),
                                Button.inline("❌ حذف شهر", f"admin:locations:cities:delete:{province_id}")
                            ],
                            [
                                Button.inline("« بازگشت", "admin:locations:cities")
                            ]
                        ]
                        
                        await event.edit(message, buttons=buttons)
                    else:
                        await event.answer("استان مورد نظر یافت نشد", alert=True)
                        await handle_cities_management(event, [], location_service)
                else:
                    await event.answer("شناسه استان نامعتبر است", alert=True)
                    await handle_cities_management(event, [], location_service)
            
            # Add handlers for add, edit, delete, search cities (similar to provinces)
            elif action == "add":
                if len(params) > 1:
                    province_id = int(params[1])
                    province = location_service.get_province_by_id(province_id)
                    
                    if province:
                        # Set user state to add city and show instructions
                        await event.edit(f"🏘️ **افزودن شهر جدید در استان {province.name}**\n\nلطفاً نام شهر را وارد کنید:", 
                                       buttons=[[Button.inline("« بازگشت", f"admin:locations:cities:province:{province_id}")]])
                        
                        # Set user state to wait for city name
                        from src.core.services.user_service import UserService
                        with get_db_session() as session:
                            user_service = UserService(session)
                            sender = await event.get_sender()
                            user_service.set_user_state(sender.id, f"add_city:{province_id}")
                    else:
                        await event.answer("استان مورد نظر یافت نشد", alert=True)
                        await handle_cities_management(event, [], location_service)
                else:
                    await event.answer("شناسه استان نامعتبر است", alert=True)
                    await handle_cities_management(event, [], location_service)
            
            # Add more actions for cities management...
    
    except Exception as e:
        log_error("Error in handle_cities_management", e, event.sender_id)
        await event.answer("خطایی رخ داد. لطفاً دوباره تلاش کنید.", alert=True)

async def handle_areas_management(event: events.CallbackQuery.Event, params: List[str], location_service: LocationService) -> None:
    """Handle areas management"""
    try:
        if not params:
            # Show cities for area selection
            provinces = location_service.get_provinces()
            
            message = "📍 **مدیریت مناطق**\n\nابتدا استان مورد نظر را انتخاب کنید:"
            
            buttons = []
            for province in provinces:
                buttons.append([Button.inline(
                    f"{province.name}", 
                    f"admin:locations:areas:province:{province.id}"
                )])
            
            buttons.append([Button.inline("« بازگشت", "admin:locations")])
            
            await event.edit(message, buttons=buttons)
        
        # Add more detailed handlers for areas management...
    
    except Exception as e:
        log_error("Error in handle_areas_management", e, event.sender_id)
        await event.answer("خطایی رخ داد. لطفاً دوباره تلاش کنید.", alert=True)

async def handle_places_management(event: events.CallbackQuery.Event, params: List[str], location_service: LocationService) -> None:
    """Handle delivery places management"""
    try:
        if not params:
            # Show cities for place selection
            provinces = location_service.get_provinces()
            
            message = "🏠 **مدیریت مکان‌های تحویل**\n\nابتدا استان مورد نظر را انتخاب کنید:"
            
            buttons = []
            for province in provinces:
                buttons.append([Button.inline(
                    f"{province.name}", 
                    f"admin:locations:places:province:{province.id}"
                )])
            
            buttons.append([Button.inline("« بازگشت", "admin:locations")])
            
            await event.edit(message, buttons=buttons)
        
        # Add more detailed handlers for places management...
    
    except Exception as e:
        log_error("Error in handle_places_management", e, event.sender_id)
        await event.answer("خطایی رخ داد. لطفاً دوباره تلاش کنید.", alert=True)

async def handle_add_location(event: events.CallbackQuery.Event, params: List[str], location_service: LocationService, user: Any) -> None:
    """Handle adding a new location"""
    try:
        # Show location type selection
        message = "➕ **افزودن مکان جدید**\n\nچه نوع مکانی می‌خواهید اضافه کنید؟"
        
        buttons = [
            [
                Button.inline("🏙️ استان", "admin:locations:provinces:add"),
                Button.inline("🏘️ شهر", "admin:locations:cities")
            ],
            [
                Button.inline("📍 منطقه", "admin:locations:areas"),
                Button.inline("🏠 نقطه تحویل", "admin:locations:places")
            ],
            [
                Button.inline("« بازگشت", "admin:locations")
            ]
        ]
        
        await event.edit(message, buttons=buttons)
    
    except Exception as e:
        log_error("Error in handle_add_location", e, event.sender_id)
        await event.answer("خطایی رخ داد. لطفاً دوباره تلاش کنید.", alert=True)

async def handle_list_locations(event: events.CallbackQuery.Event, params: List[str], location_service: LocationService) -> None:
    """Handle listing locations"""
    try:
        message = "📋 **لیست مکان‌ها**\n\nچه نوع مکان‌هایی را می‌خواهید مشاهده کنید؟"
        
        buttons = [
            [
                Button.inline("🏙️ استان‌ها", "admin:locations:provinces"),
                Button.inline("🏘️ شهرها", "admin:locations:cities")
            ],
            [
                Button.inline("📍 مناطق", "admin:locations:areas"),
                Button.inline("🏠 نقاط تحویل", "admin:locations:places")
            ],
            [
                Button.inline("« بازگشت", "admin:locations")
            ]
        ]
        
        await event.edit(message, buttons=buttons)
    
    except Exception as e:
        log_error("Error in handle_list_locations", e, event.sender_id)
        await event.answer("خطایی رخ داد. لطفاً دوباره تلاش کنید.", alert=True)

async def handle_delete_location(event: events.CallbackQuery.Event, params: List[str], location_service: LocationService, user: Any) -> None:
    """Handle deleting location"""
    try:
        message = "🗑️ **حذف مکان**\n\nچه نوع مکانی را می‌خواهید حذف کنید؟"
        
        buttons = [
            [
                Button.inline("🏙️ استان", "admin:locations:provinces:delete"),
                Button.inline("🏘️ شهر", "admin:locations:cities")
            ],
            [
                Button.inline("📍 منطقه", "admin:locations:areas"),
                Button.inline("🏠 نقطه تحویل", "admin:locations:places")
            ],
            [
                Button.inline("« بازگشت", "admin:locations")
            ]
        ]
        
        await event.edit(message, buttons=buttons)
    
    except Exception as e:
        log_error("Error in handle_delete_location", e, event.sender_id)
        await event.answer("خطایی رخ داد. لطفاً دوباره تلاش کنید.", alert=True)

async def handle_edit_location(event: events.CallbackQuery.Event, params: List[str], location_service: LocationService, user: Any) -> None:
    """Handle editing location"""
    try:
        message = "✏️ **ویرایش مکان**\n\nچه نوع مکانی را می‌خواهید ویرایش کنید؟"
        
        buttons = [
            [
                Button.inline("🏙️ استان", "admin:locations:provinces:edit"),
                Button.inline("🏘️ شهر", "admin:locations:cities")
            ],
            [
                Button.inline("📍 منطقه", "admin:locations:areas"),
                Button.inline("🏠 نقطه تحویل", "admin:locations:places")
            ],
            [
                Button.inline("« بازگشت", "admin:locations")
            ]
        ]
        
        await event.edit(message, buttons=buttons)
    
    except Exception as e:
        log_error("Error in handle_edit_location", e, event.sender_id)
        await event.answer("خطایی رخ داد. لطفاً دوباره تلاش کنید.", alert=True) 