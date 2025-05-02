from telethon import events, Button
from src.utils.logger import setup_logger, log_error
from src.core.database import get_db_session
from src.core.services.location_service import LocationService
from src.core.services.user_service import UserService
from src.bot.handlers.callback_router import register_callback
from typing import List, Dict, Any

# Initialize logger
logger = setup_logger("province_management_handler")

def register_province_management_callbacks():
    """Register province management callback handlers"""
    logger.info("Registering province management callbacks")
    
    @register_callback("admin:locations:provinces")
    async def handle_provinces_management(event: events.CallbackQuery.Event, params: List[str]) -> None:
        """Handle provinces management callback"""
        try:
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
                
                if not params:
                    # Show provinces list
                    await list_provinces(event, location_service)
                    return
                
                action = params[0]  # add, edit, delete, search
                
                if action == "add":
                    # Add new province
                    await add_province(event, params[1:] if len(params) > 1 else [], user_service)
                
                elif action == "edit":
                    # Edit province
                    await edit_province(event, params[1:] if len(params) > 1 else [], location_service, user_service)
                
                elif action == "delete":
                    # Delete province
                    await delete_province(event, params[1:] if len(params) > 1 else [], location_service)
                
                elif action == "search":
                    # Search province
                    await search_province(event, params[1:] if len(params) > 1 else [], location_service, user_service)
                
                elif action == "back":
                    # Back to locations menu
                    from src.bot.keyboards.admin_keyboard import get_admin_locations_keyboard
                    await event.edit("🏙️ **مدیریت مکان‌های تحویل**", buttons=get_admin_locations_keyboard())
                
                else:
                    await event.answer("عملیات نامعتبر", alert=True)
                    await list_provinces(event, location_service)
        
        except Exception as e:
            log_error("Error in handle_provinces_management", e, event.sender_id)
            await event.answer("خطایی رخ داد. لطفاً دوباره تلاش کنید.", alert=True)

async def list_provinces(event: events.CallbackQuery.Event, location_service: LocationService) -> None:
    """List provinces"""
    try:
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
    
    except Exception as e:
        log_error("Error in list_provinces", e, event.sender_id)
        await event.answer("خطا در نمایش لیست استان‌ها. لطفاً دوباره تلاش کنید.", alert=True)

async def add_province(event: events.CallbackQuery.Event, params: List[str], user_service: UserService) -> None:
    """Handle adding a new province"""
    try:
        if params and params[0] == "submit":
            # This is called from message handler after user enters province name
            # Implementation will be in message_handler.py
            await event.answer("عملیات نامعتبر", alert=True)
            return
        
        # Set user state to add province and show instructions
        message = (
            "🏙️ **افزودن استان جدید**\n\n"
            "لطفاً نام استان را وارد کنید:"
        )
        
        # Set user state to wait for province name
        sender = await event.get_sender()
        user_service.set_user_state(sender.id, "add_province")
        
        await event.edit(message, buttons=[[Button.inline("« بازگشت", "admin:locations:provinces")]])
    
    except Exception as e:
        log_error("Error in add_province", e, event.sender_id)
        await event.answer("خطا در افزودن استان. لطفاً دوباره تلاش کنید.", alert=True)

async def edit_province(event: events.CallbackQuery.Event, params: List[str], location_service: LocationService, user_service: UserService) -> None:
    """Handle editing a province"""
    try:
        if not params:
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
        
        elif len(params) == 1:
            # Show edit form for specific province
            province_id = int(params[0])
            province = location_service.get_province_by_id(province_id)
            
            if not province:
                await event.answer("استان مورد نظر یافت نشد", alert=True)
                await edit_province(event, [], location_service, user_service)
                return
            
            message = (
                f"✏️ **ویرایش استان**\n\n"
                f"استان فعلی: {province.name}\n\n"
                f"لطفاً نام جدید استان را وارد کنید:"
            )
            
            # Set user state to wait for new province name
            sender = await event.get_sender()
            user_service.set_user_state(sender.id, f"edit_province:{province_id}")
            
            await event.edit(message, buttons=[[Button.inline("« بازگشت", "admin:locations:provinces")]])
        
        elif params[0] == "submit":
            # This is called from message handler after user enters new province name
            # Implementation will be in message_handler.py
            await event.answer("عملیات نامعتبر", alert=True)
            return
        
        else:
            await event.answer("عملیات نامعتبر", alert=True)
            await edit_province(event, [], location_service, user_service)
    
    except Exception as e:
        log_error("Error in edit_province", e, event.sender_id)
        await event.answer("خطا در ویرایش استان. لطفاً دوباره تلاش کنید.", alert=True)

async def delete_province(event: events.CallbackQuery.Event, params: List[str], location_service: LocationService) -> None:
    """Handle deleting a province"""
    try:
        if not params:
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
        
        elif len(params) == 1:
            # Show confirmation for specific province
            province_id = int(params[0])
            province = location_service.get_province_by_id(province_id)
            
            if not province:
                await event.answer("استان مورد نظر یافت نشد", alert=True)
                await delete_province(event, [], location_service)
                return
            
            message = (
                f"❌ **حذف استان**\n\n"
                f"آیا از حذف استان «{province.name}» اطمینان دارید؟\n\n"
                f"توجه: با حذف استان، تمام شهرها و مناطق مرتبط با آن نیز حذف خواهند شد."
            )
            
            buttons = [
                [
                    Button.inline("✅ بله، حذف شود", f"admin:locations:provinces:delete:{province_id}:confirm"),
                    Button.inline("❌ انصراف", "admin:locations:provinces")
                ]
            ]
            
            await event.edit(message, buttons=buttons)
        
        elif len(params) == 2 and params[1] == "confirm":
            # Confirm deletion
            province_id = int(params[0])
            
            try:
                # Check if province exists
                province = location_service.get_province_by_id(province_id)
                if not province:
                    await event.answer("استان مورد نظر یافت نشد", alert=True)
                    await delete_province(event, [], location_service)
                    return
                
                # Delete province and related cities, areas, and locations
                location_service.delete_province(province_id)
                
                await event.answer(f"استان {province.name} با موفقیت حذف شد")
                await list_provinces(event, location_service)
            
            except Exception as e:
                log_error(f"Error deleting province {province_id}", e, event.sender_id)
                await event.answer(f"خطا در حذف استان: {str(e)}", alert=True)
                await list_provinces(event, location_service)
        
        else:
            await event.answer("عملیات نامعتبر", alert=True)
            await delete_province(event, [], location_service)
    
    except Exception as e:
        log_error("Error in delete_province", e, event.sender_id)
        await event.answer("خطا در حذف استان. لطفاً دوباره تلاش کنید.", alert=True)

async def search_province(event: events.CallbackQuery.Event, params: List[str], location_service: LocationService, user_service: UserService) -> None:
    """Handle searching for a province"""
    try:
        if not params:
            # Show search form
            message = "🔍 **جستجوی استان**\n\nلطفاً نام استان را برای جستجو وارد کنید:"
            
            # Set user state to wait for search query
            sender = await event.get_sender()
            user_service.set_user_state(sender.id, "search_province")
            
            await event.edit(message, buttons=[[Button.inline("« بازگشت", "admin:locations:provinces")]])
        
        elif params[0] == "result":
            # This is called from message handler after user enters search query
            # Implementation will be in message_handler.py
            if len(params) < 2:
                await event.answer("عملیات نامعتبر", alert=True)
                await search_province(event, [], location_service, user_service)
                return
            
            query = params[1]
            provinces = location_service.search_provinces(query)
            
            message = f"🔍 **نتایج جستجو برای: {query}**\n\n"
            
            if not provinces:
                message += "هیچ استانی با این نام یافت نشد."
            else:
                message += "استان‌های یافت شده:\n\n"
                for i, province in enumerate(provinces, 1):
                    message += f"{i}. {province.name} (کد: {province.id})\n"
            
            buttons = [
                [
                    Button.inline("🔍 جستجوی جدید", "admin:locations:provinces:search"),
                    Button.inline("« بازگشت", "admin:locations:provinces")
                ]
            ]
            
            await event.edit(message, buttons=buttons)
        
        else:
            await event.answer("عملیات نامعتبر", alert=True)
            await search_province(event, [], location_service, user_service)
    
    except Exception as e:
        log_error("Error in search_province", e, event.sender_id)
        await event.answer("خطا در جستجوی استان. لطفاً دوباره تلاش کنید.", alert=True)

# This message handler function should be registered in message_handler.py
async def handle_province_management_messages(event, user, user_state, user_service, location_service):
    """Handle message responses for province management"""
    state_parts = user_state.split(":")
    state_action = state_parts[0]
    
    if state_action == "add_province":
        # Handle adding new province
        province_name = event.text.strip()
        
        if not province_name:
            await event.respond("❌ نام استان نمی‌تواند خالی باشد. لطفاً دوباره تلاش کنید.")
            return
        
        try:
            # Add new province
            new_province = location_service.add_province(province_name)
            
            # Clear user state
            user_service.clear_user_state(user.id)
            
            # Send confirmation message
            await event.respond(
                f"✅ استان «{province_name}» با موفقیت اضافه شد.\n\n"
                f"کد استان: {new_province.id}",
                buttons=[
                    [
                        Button.inline("➕ افزودن استان دیگر", "admin:locations:provinces:add"),
                        Button.inline("« بازگشت به لیست", "admin:locations:provinces")
                    ]
                ]
            )
        
        except Exception as e:
            log_error(f"Error adding province {province_name}", e, event.sender_id)
            await event.respond(f"❌ خطا در افزودن استان: {str(e)}")
    
    elif state_action == "edit_province":
        # Handle editing province
        if len(state_parts) < 2:
            await event.respond("❌ وضعیت نامعتبر. لطفاً دوباره از منوی ویرایش استان اقدام کنید.")
            user_service.clear_user_state(user.id)
            return
        
        province_id = int(state_parts[1])
        new_name = event.text.strip()
        
        if not new_name:
            await event.respond("❌ نام استان نمی‌تواند خالی باشد. لطفاً دوباره تلاش کنید.")
            return
        
        try:
            # Get province
            province = location_service.get_province_by_id(province_id)
            
            if not province:
                await event.respond("❌ استان مورد نظر یافت نشد. لطفاً دوباره از منوی ویرایش استان اقدام کنید.")
                user_service.clear_user_state(user.id)
                return
            
            old_name = province.name
            
            # Update province
            location_service.update_province(province_id, new_name)
            
            # Clear user state
            user_service.clear_user_state(user.id)
            
            # Send confirmation message
            await event.respond(
                f"✅ نام استان از «{old_name}» به «{new_name}» با موفقیت تغییر یافت.",
                buttons=[
                    [
                        Button.inline("✏️ ویرایش استان دیگر", "admin:locations:provinces:edit"),
                        Button.inline("« بازگشت به لیست", "admin:locations:provinces")
                    ]
                ]
            )
        
        except Exception as e:
            log_error(f"Error updating province {province_id}", e, event.sender_id)
            await event.respond(f"❌ خطا در ویرایش استان: {str(e)}")
    
    elif state_action == "search_province":
        # Handle province search
        query = event.text.strip()
        
        if not query:
            await event.respond("❌ عبارت جستجو نمی‌تواند خالی باشد. لطفاً دوباره تلاش کنید.")
            return
        
        # Clear user state
        user_service.clear_user_state(user.id)
        
        # Search provinces
        provinces = location_service.search_provinces(query)
        
        message = f"🔍 **نتایج جستجو برای: {query}**\n\n"
        
        if not provinces:
            message += "هیچ استانی با این نام یافت نشد."
        else:
            message += "استان‌های یافت شده:\n\n"
            for i, province in enumerate(provinces, 1):
                message += f"{i}. {province.name} (کد: {province.id})\n"
        
        await event.respond(
            message,
            buttons=[
                [
                    Button.inline("🔍 جستجوی جدید", "admin:locations:provinces:search"),
                    Button.inline("« بازگشت به لیست", "admin:locations:provinces")
                ]
            ]
        )
    
    else:
        # Unknown state
        await event.respond("❌ وضعیت نامعتبر. لطفاً دوباره از منوی مدیریت استان‌ها اقدام کنید.")
        user_service.clear_user_state(user.id) 