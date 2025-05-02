from telethon import events, Button
from src.utils.logger import setup_logger, log_error
from src.core.database import get_db_session
from src.core.services.user_service import UserService
from src.core.services.backup_service import BackupService
from src.bot.handlers.callback_router import register_callback
from typing import List, Dict, Any
import os
import datetime

# Initialize logger
logger = setup_logger("database_management_handler")

def register_database_management_callbacks():
    """Register database management callback handlers"""
    logger.info("Registering database management callbacks")
    
    @register_callback("admin:database")
    async def handle_admin_database(event: events.CallbackQuery.Event, params: List[str]) -> None:
        """Handle admin database management callback"""
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
                
                if not params:
                    # Show database management keyboard
                    from src.bot.keyboards.admin_keyboard import DatabaseManagementKeyboards
                    keyboard = DatabaseManagementKeyboards.get_database_management_keyboard()
                    
                    message = (
                        "📂 **مدیریت پایگاه داده**\n\n"
                        "از این بخش می‌توانید پایگاه داده سیستم را مدیریت کنید.\n"
                        "لطفاً یکی از گزینه‌های زیر را انتخاب کنید:"
                    )
                    
                    await event.edit(message, buttons=keyboard)
                    return
                
                action = params[0]  # backup, restore, optimize, stats, cleanup, etc.
                
                if action == "backup":
                    # Handle database backup
                    if len(params) > 1:
                        backup_type = params[1]  # full, structure, data, settings
                        await handle_database_backup(event, backup_type, user)
                    else:
                        # Show backup options
                        from src.bot.keyboards.admin_keyboard import DatabaseManagementKeyboards
                        keyboard = DatabaseManagementKeyboards.get_backup_options()
                        
                        message = (
                            "📤 **پشتیبان‌گیری از پایگاه داده**\n\n"
                            "لطفاً نوع پشتیبان‌گیری را انتخاب کنید:"
                        )
                        
                        await event.edit(message, buttons=keyboard)
                
                elif action == "restore":
                    # Handle database restore
                    if len(params) > 1:
                        if params[1] == "view":
                            # View backup details
                            if len(params) > 2:
                                backup_id = int(params[2])
                                await handle_view_backup(event, backup_id, session)
                            else:
                                await event.answer("شناسه پشتیبان نامعتبر است", alert=True)
                                await handle_database_restore_list(event, session)
                        elif params[1] == "confirm":
                            # Confirm restore
                            if len(params) > 2:
                                backup_id = int(params[2])
                                await handle_confirm_restore(event, backup_id, user, session)
                            else:
                                await event.answer("شناسه پشتیبان نامعتبر است", alert=True)
                                await handle_database_restore_list(event, session)
                        elif params[1] == "cancel":
                            # Cancel restore
                            await handle_database_restore_list(event, session)
                        else:
                            await event.answer("عملیات نامعتبر", alert=True)
                            await handle_database_restore_list(event, session)
                    else:
                        # Show restore options (list of backups)
                        await handle_database_restore_list(event, session)
                
                elif action == "optimize":
                    # Handle database optimization
                    await handle_database_optimize(event, session)
                
                elif action == "stats":
                    # Handle database statistics
                    await handle_database_stats(event, session)
                
                elif action == "cleanup":
                    # Handle database cleanup
                    if len(params) > 1 and params[1] == "confirm":
                        await handle_confirm_cleanup(event, session)
                    else:
                        await handle_database_cleanup(event)
                
                elif action == "back":
                    # Back to admin panel
                    from src.bot.keyboards.admin_keyboard import AdminKeyboards
                    keyboard = AdminKeyboards.get_admin_main_menu()
                    
                    message = (
                        "🛠️ **پنل مدیریت**\n\n"
                        f"خوش آمدید به پنل مدیریت، {user.first_name}.\n"
                        "از اینجا می‌توانید سیستم را مدیریت کنید.\n\n"
                        "لطفاً یک گزینه را انتخاب کنید:"
                    )
                    
                    await event.edit(message, buttons=keyboard)
                
                else:
                    await event.answer("عملیات نامعتبر", alert=True)
                    from src.bot.keyboards.admin_keyboard import DatabaseManagementKeyboards
                    keyboard = DatabaseManagementKeyboards.get_database_management_keyboard()
                    await event.edit("📂 **مدیریت پایگاه داده**", buttons=keyboard)
        
        except Exception as e:
            log_error("Error in handle_admin_database", e, event.sender_id)
            await event.answer("خطایی رخ داد. لطفاً دوباره تلاش کنید.", alert=True)

async def handle_database_backup(event: events.CallbackQuery.Event, backup_type: str, user: Any) -> None:
    """Handle database backup based on type"""
    try:
        # Get backup service
        with get_db_session() as session:
            backup_service = BackupService(session)
            
            # Create backup message
            if backup_type == "full":
                message = "در حال پشتیبان‌گیری کامل از پایگاه داده... لطفاً صبر کنید."
                await event.edit(message)
                
                # Perform full backup
                backup_id = backup_service.create_full_backup(user.id)
                
                await event.edit(
                    f"✅ **پشتیبان‌گیری موفقیت‌آمیز**\n\n"
                    f"پشتیبان‌گیری کامل با شناسه {backup_id} با موفقیت انجام شد.\n"
                    f"تاریخ: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
                    f"می‌توانید این پشتیبان را از بخش بازیابی پشتیبان مشاهده کنید.",
                    buttons=[[Button.inline("« بازگشت", "admin:database")]]
                )
            
            elif backup_type == "structure":
                message = "در حال پشتیبان‌گیری از ساختار پایگاه داده... لطفاً صبر کنید."
                await event.edit(message)
                
                # Perform structure backup
                backup_id = backup_service.create_structure_backup(user.id)
                
                await event.edit(
                    f"✅ **پشتیبان‌گیری موفقیت‌آمیز**\n\n"
                    f"پشتیبان‌گیری از ساختار با شناسه {backup_id} با موفقیت انجام شد.\n"
                    f"تاریخ: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
                    f"می‌توانید این پشتیبان را از بخش بازیابی پشتیبان مشاهده کنید.",
                    buttons=[[Button.inline("« بازگشت", "admin:database")]]
                )
            
            elif backup_type == "data":
                message = "در حال پشتیبان‌گیری از داده‌های پایگاه داده... لطفاً صبر کنید."
                await event.edit(message)
                
                # Perform data backup
                backup_id = backup_service.create_data_backup(user.id)
                
                await event.edit(
                    f"✅ **پشتیبان‌گیری موفقیت‌آمیز**\n\n"
                    f"پشتیبان‌گیری از داده‌ها با شناسه {backup_id} با موفقیت انجام شد.\n"
                    f"تاریخ: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
                    f"می‌توانید این پشتیبان را از بخش بازیابی پشتیبان مشاهده کنید.",
                    buttons=[[Button.inline("« بازگشت", "admin:database")]]
                )
            
            elif backup_type == "settings":
                message = "در حال پشتیبان‌گیری از تنظیمات... لطفاً صبر کنید."
                await event.edit(message)
                
                # Perform settings backup
                backup_id = backup_service.create_settings_backup(user.id)
                
                await event.edit(
                    f"✅ **پشتیبان‌گیری موفقیت‌آمیز**\n\n"
                    f"پشتیبان‌گیری از تنظیمات با شناسه {backup_id} با موفقیت انجام شد.\n"
                    f"تاریخ: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
                    f"می‌توانید این پشتیبان را از بخش بازیابی پشتیبان مشاهده کنید.",
                    buttons=[[Button.inline("« بازگشت", "admin:database")]]
                )
            
            else:
                await event.answer("نوع پشتیبان‌گیری نامعتبر است", alert=True)
                from src.bot.keyboards.admin_keyboard import DatabaseManagementKeyboards
                keyboard = DatabaseManagementKeyboards.get_backup_options()
                await event.edit("📤 **پشتیبان‌گیری از پایگاه داده**", buttons=keyboard)
    
    except Exception as e:
        log_error("Error in handle_database_backup", e, event.sender_id)
        await event.answer("خطا در پشتیبان‌گیری. لطفاً دوباره تلاش کنید.", alert=True)
        from src.bot.keyboards.admin_keyboard import DatabaseManagementKeyboards
        keyboard = DatabaseManagementKeyboards.get_backup_options()
        await event.edit("📤 **پشتیبان‌گیری از پایگاه داده**", buttons=keyboard)

async def handle_database_restore_list(event: events.CallbackQuery.Event, session) -> None:
    """Handle listing database backups for restore"""
    try:
        # Get backup service
        backup_service = BackupService(session)
        
        # Get backups
        backups = backup_service.get_backups()
        
        if not backups:
            await event.edit(
                "📥 **بازیابی پایگاه داده**\n\n"
                "هیچ پشتیبانی در سیستم ثبت نشده است.",
                buttons=[[Button.inline("« بازگشت", "admin:database")]]
            )
            return
        
        message = "📥 **بازیابی پایگاه داده**\n\nلطفاً پشتیبان مورد نظر را برای بازیابی انتخاب کنید:\n\n"
        
        # Create keyboard with restore options
        from src.bot.keyboards.admin_keyboard import DatabaseManagementKeyboards
        keyboard = DatabaseManagementKeyboards.get_restore_options(backups)
        
        await event.edit(message, buttons=keyboard)
    
    except Exception as e:
        log_error("Error in handle_database_restore_list", e, event.sender_id)
        await event.answer("خطا در نمایش پشتیبان‌ها. لطفاً دوباره تلاش کنید.", alert=True)
        from src.bot.keyboards.admin_keyboard import DatabaseManagementKeyboards
        keyboard = DatabaseManagementKeyboards.get_database_management_keyboard()
        await event.edit("📂 **مدیریت پایگاه داده**", buttons=keyboard)

async def handle_view_backup(event: events.CallbackQuery.Event, backup_id: int, session) -> None:
    """Handle viewing backup details"""
    try:
        # Get backup service
        backup_service = BackupService(session)
        
        # Get backup
        backup = backup_service.get_backup_by_id(backup_id)
        
        if not backup:
            await event.answer("پشتیبان مورد نظر یافت نشد", alert=True)
            await handle_database_restore_list(event, session)
            return
        
        # Get creator info
        user_service = UserService(session)
        creator = user_service.get_by_id(backup.created_by) if backup.created_by else None
        creator_name = f"{creator.first_name} {creator.last_name or ''}" if creator else "نامشخص"
        
        # Format backup type
        backup_type_text = {
            "full": "کامل",
            "structure": "ساختار",
            "data": "داده‌ها",
            "settings": "تنظیمات"
        }.get(backup.backup_type, backup.backup_type)
        
        message = (
            f"📋 **اطلاعات پشتیبان #{backup.id}**\n\n"
            f"📊 نوع: {backup_type_text}\n"
            f"📅 تاریخ ایجاد: {backup.created_at.strftime('%Y-%m-%d %H:%M')}\n"
            f"👤 ایجاد شده توسط: {creator_name}\n"
            f"💾 حجم: {backup.size / (1024*1024):.2f} مگابایت\n\n"
            f"📝 توضیحات: {backup.description or 'ندارد'}\n\n"
            f"⚠️ **هشدار**: بازیابی پشتیبان منجر به جایگزینی داده‌های فعلی سیستم با داده‌های پشتیبان می‌شود."
        )
        
        # Create confirmation keyboard
        from src.bot.keyboards.admin_keyboard import DatabaseManagementKeyboards
        keyboard = DatabaseManagementKeyboards.get_restore_confirmation(backup.id)
        
        await event.edit(message, buttons=keyboard)
    
    except Exception as e:
        log_error("Error in handle_view_backup", e, event.sender_id)
        await event.answer("خطا در نمایش اطلاعات پشتیبان. لطفاً دوباره تلاش کنید.", alert=True)
        await handle_database_restore_list(event, session)

async def handle_confirm_restore(event: events.CallbackQuery.Event, backup_id: int, user: Any, session) -> None:
    """Handle confirming database restore"""
    try:
        # Get backup service
        backup_service = BackupService(session)
        
        # Get backup
        backup = backup_service.get_backup_by_id(backup_id)
        
        if not backup:
            await event.answer("پشتیبان مورد نظر یافت نشد", alert=True)
            await handle_database_restore_list(event, session)
            return
        
        message = "در حال بازیابی پایگاه داده... لطفاً صبر کنید."
        await event.edit(message)
        
        # Perform restore
        result = backup_service.restore_backup(backup_id, user.id)
        
        if result:
            await event.edit(
                f"✅ **بازیابی موفقیت‌آمیز**\n\n"
                f"پایگاه داده با موفقیت از پشتیبان #{backup_id} بازیابی شد.\n"
                f"تاریخ: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
                f"برای اعمال تغییرات کامل، لطفاً بات را ری‌استارت کنید.",
                buttons=[[Button.inline("« بازگشت", "admin:database")]]
            )
        else:
            await event.edit(
                f"❌ **خطا در بازیابی**\n\n"
                f"بازیابی پایگاه داده از پشتیبان #{backup_id} با خطا مواجه شد.\n"
                f"لطفاً دوباره تلاش کنید یا با پشتیبانی تماس بگیرید.",
                buttons=[[Button.inline("« بازگشت", "admin:database")]]
            )
    
    except Exception as e:
        log_error("Error in handle_confirm_restore", e, event.sender_id)
        await event.answer("خطا در بازیابی پایگاه داده. لطفاً دوباره تلاش کنید.", alert=True)
        await handle_database_restore_list(event, session)

async def handle_database_optimize(event: events.CallbackQuery.Event, session) -> None:
    """Handle database optimization"""
    try:
        # Get backup service
        backup_service = BackupService(session)
        
        message = "در حال بهینه‌سازی پایگاه داده... لطفاً صبر کنید."
        await event.edit(message)
        
        # Perform optimization
        result = backup_service.optimize_database()
        
        if result:
            await event.edit(
                "✅ **بهینه‌سازی موفقیت‌آمیز**\n\n"
                "پایگاه داده با موفقیت بهینه‌سازی شد.\n"
                f"تاریخ: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
                "این عملیات موجب افزایش سرعت و کارایی سیستم می‌شود.",
                buttons=[[Button.inline("« بازگشت", "admin:database")]]
            )
        else:
            await event.edit(
                "❌ **خطا در بهینه‌سازی**\n\n"
                "بهینه‌سازی پایگاه داده با خطا مواجه شد.\n"
                "لطفاً دوباره تلاش کنید یا با پشتیبانی تماس بگیرید.",
                buttons=[[Button.inline("« بازگشت", "admin:database")]]
            )
    
    except Exception as e:
        log_error("Error in handle_database_optimize", e, event.sender_id)
        await event.answer("خطا در بهینه‌سازی پایگاه داده. لطفاً دوباره تلاش کنید.", alert=True)
        from src.bot.keyboards.admin_keyboard import DatabaseManagementKeyboards
        keyboard = DatabaseManagementKeyboards.get_database_management_keyboard()
        await event.edit("📂 **مدیریت پایگاه داده**", buttons=keyboard)

async def handle_database_stats(event: events.CallbackQuery.Event, session) -> None:
    """Handle database statistics"""
    try:
        # Get services
        from src.core.services.user_service import UserService
        from src.core.services.product_service import ProductService
        from src.core.services.order_service import OrderService
        from src.core.services.payment_service import PaymentService
        from src.core.services.location_service import LocationService
        
        user_service = UserService(session)
        product_service = ProductService(session)
        order_service = OrderService(session)
        payment_service = PaymentService(session)
        location_service = LocationService(session)
        
        # Get database size
        db_size = 0
        db_path = os.environ.get("DB_NAME", "chainstore.db")
        if os.path.exists(db_path):
            db_size = os.path.getsize(db_path) / (1024 * 1024)  # Convert to MB
        
        # Get counts
        total_users = user_service.count_users()
        total_products = product_service.count_products()
        total_orders = order_service.count_orders()
        total_payments = payment_service.count_payments()
        total_locations = location_service.count_locations()
        
        # Get backups count
        backup_service = BackupService(session)
        total_backups = backup_service.count_backups()
        
        # Get database creation/modification time
        db_creation_time = "نامشخص"
        if os.path.exists(db_path):
            timestamp = os.path.getctime(db_path)
            db_creation_time = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M')
        
        message = (
            "📊 **آمار پایگاه داده**\n\n"
            f"💾 حجم پایگاه داده: {db_size:.2f} مگابایت\n"
            f"📅 تاریخ ایجاد: {db_creation_time}\n\n"
            f"👥 تعداد کاربران: {total_users}\n"
            f"📦 تعداد محصولات: {total_products}\n"
            f"🛒 تعداد سفارشات: {total_orders}\n"
            f"💳 تعداد پرداخت‌ها: {total_payments}\n"
            f"📍 تعداد مکان‌ها: {total_locations}\n"
            f"📤 تعداد پشتیبان‌ها: {total_backups}\n\n"
            f"این آمار به‌روزرسانی شده تا تاریخ {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} می‌باشد."
        )
        
        await event.edit(message, buttons=[[Button.inline("« بازگشت", "admin:database")]])
    
    except Exception as e:
        log_error("Error in handle_database_stats", e, event.sender_id)
        await event.answer("خطا در دریافت آمار پایگاه داده. لطفاً دوباره تلاش کنید.", alert=True)
        from src.bot.keyboards.admin_keyboard import DatabaseManagementKeyboards
        keyboard = DatabaseManagementKeyboards.get_database_management_keyboard()
        await event.edit("📂 **مدیریت پایگاه داده**", buttons=keyboard)

async def handle_database_cleanup(event: events.CallbackQuery.Event) -> None:
    """Handle database cleanup confirmation"""
    try:
        message = (
            "❌ **حذف داده‌های قدیمی**\n\n"
            "این عملیات باعث حذف داده‌های زیر می‌شود:\n"
            "• لاگ‌ها و رویدادهای قدیمی‌تر از 3 ماه\n"
            "• پشتیبان‌های قدیمی‌تر از 6 ماه\n"
            "• پیام‌های پاک شده و موقت\n"
            "• داده‌های موقت ذخیره شده\n\n"
            "⚠️ آیا از انجام این عملیات اطمینان دارید؟"
        )
        
        buttons = [
            [
                Button.inline("✅ بله، حذف شود", "admin:database:cleanup:confirm"),
                Button.inline("❌ انصراف", "admin:database")
            ]
        ]
        
        await event.edit(message, buttons=buttons)
    
    except Exception as e:
        log_error("Error in handle_database_cleanup", e, event.sender_id)
        await event.answer("خطا در نمایش تأیید پاک‌سازی. لطفاً دوباره تلاش کنید.", alert=True)
        from src.bot.keyboards.admin_keyboard import DatabaseManagementKeyboards
        keyboard = DatabaseManagementKeyboards.get_database_management_keyboard()
        await event.edit("📂 **مدیریت پایگاه داده**", buttons=keyboard)

async def handle_confirm_cleanup(event: events.CallbackQuery.Event, session) -> None:
    """Handle confirming database cleanup"""
    try:
        # Get backup service
        backup_service = BackupService(session)
        
        message = "در حال پاک‌سازی داده‌های قدیمی... لطفاً صبر کنید."
        await event.edit(message)
        
        # Perform cleanup
        results = backup_service.cleanup_old_data()
        
        # Parse results
        logs_removed = results.get("logs_removed", 0)
        backups_removed = results.get("backups_removed", 0)
        temp_removed = results.get("temp_removed", 0)
        
        await event.edit(
            "✅ **پاک‌سازی موفقیت‌آمیز**\n\n"
            f"• {logs_removed} رکورد لاگ قدیمی حذف شد\n"
            f"• {backups_removed} پشتیبان قدیمی حذف شد\n"
            f"• {temp_removed} فایل موقت پاک شد\n\n"
            f"تاریخ: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
            "پاک‌سازی با موفقیت انجام شد و فضای پایگاه داده آزاد شد.",
            buttons=[[Button.inline("« بازگشت", "admin:database")]]
        )
    
    except Exception as e:
        log_error("Error in handle_confirm_cleanup", e, event.sender_id)
        await event.answer("خطا در پاک‌سازی داده‌ها. لطفاً دوباره تلاش کنید.", alert=True)
        from src.bot.keyboards.admin_keyboard import DatabaseManagementKeyboards
        keyboard = DatabaseManagementKeyboards.get_database_management_keyboard()
        await event.edit("📂 **مدیریت پایگاه داده**", buttons=keyboard) 