from telethon import events, Button
from src.utils.logger import setup_logger, log_error
from src.core.database import get_db_session
from src.core.services.user_service import UserService
from src.core.services.product_service import ProductService
from src.core.services.order_service import OrderService
from src.core.services.wallet_service import WalletService
from src.bot.handlers.callback_router import register_callback
from typing import List, Dict, Any
from src.core.models.user import UserRole, UserStatus

# Initialize logger
logger = setup_logger("seller_management_handler")

def register_seller_management_callbacks():
    """Register seller management callback handlers"""
    logger.info("Registering seller management callbacks")
    
    @register_callback("admin:sellers")
    async def handle_admin_sellers(event: events.CallbackQuery.Event, params: List[str]) -> None:
        """Handle admin seller management callback"""
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
                    # Show seller management keyboard
                    from src.bot.keyboards.admin_keyboard import SellerManagementKeyboards
                    keyboard = SellerManagementKeyboards.get_seller_management_keyboard()
                    
                    message = (
                        "👨‍💼 **مدیریت فروشندگان**\n\n"
                        "از این بخش می‌توانید فروشندگان سیستم را مدیریت کنید.\n"
                        "لطفاً یکی از گزینه‌های زیر را انتخاب کنید:"
                    )
                    
                    await event.edit(message, buttons=keyboard)
                    return
                
                action = params[0]  # list, add, search, blocked, edit, etc.
                
                if action == "list":
                    # Show seller list
                    page = int(params[1]) if len(params) > 1 else 1
                    await handle_list_sellers(event, page, user_service)
                
                elif action == "add":
                    # Show add seller form
                    await handle_add_seller(event, user_service)
                
                elif action == "search":
                    # Show search form
                    await handle_search_seller(event, params[1:] if len(params) > 1 else [], user_service)
                
                elif action == "blocked":
                    # Show blocked sellers
                    page = int(params[1]) if len(params) > 1 else 1
                    await handle_blocked_sellers(event, page, user_service)
                
                elif action == "edit":
                    # Handle edit seller
                    if len(params) > 1:
                        seller_id = int(params[1])
                        await handle_edit_seller(event, seller_id, user_service)
                    else:
                        await event.answer("شناسه فروشنده نامعتبر است", alert=True)
                        from src.bot.keyboards.admin_keyboard import SellerManagementKeyboards
                        keyboard = SellerManagementKeyboards.get_seller_management_keyboard()
                        await event.edit("👨‍💼 **مدیریت فروشندگان**", buttons=keyboard)
                
                elif action == "products":
                    # Show seller products
                    if len(params) > 1:
                        seller_id = int(params[1])
                        page = int(params[2]) if len(params) > 2 else 1
                        await handle_seller_products(event, seller_id, page, user_service, session)
                    else:
                        await event.answer("شناسه فروشنده نامعتبر است", alert=True)
                        from src.bot.keyboards.admin_keyboard import SellerManagementKeyboards
                        keyboard = SellerManagementKeyboards.get_seller_management_keyboard()
                        await event.edit("👨‍💼 **مدیریت فروشندگان**", buttons=keyboard)
                
                elif action == "orders":
                    # Show seller orders
                    if len(params) > 1:
                        seller_id = int(params[1])
                        page = int(params[2]) if len(params) > 2 else 1
                        await handle_seller_orders(event, seller_id, page, user_service, session)
                    else:
                        await event.answer("شناسه فروشنده نامعتبر است", alert=True)
                        from src.bot.keyboards.admin_keyboard import SellerManagementKeyboards
                        keyboard = SellerManagementKeyboards.get_seller_management_keyboard()
                        await event.edit("👨‍💼 **مدیریت فروشندگان**", buttons=keyboard)
                
                elif action == "wallet":
                    # Show seller wallet
                    if len(params) > 1:
                        seller_id = int(params[1])
                        await handle_seller_wallet(event, seller_id, user_service, session)
                    else:
                        await event.answer("شناسه فروشنده نامعتبر است", alert=True)
                        from src.bot.keyboards.admin_keyboard import SellerManagementKeyboards
                        keyboard = SellerManagementKeyboards.get_seller_management_keyboard()
                        await event.edit("👨‍💼 **مدیریت فروشندگان**", buttons=keyboard)
                
                elif action == "block":
                    # Block seller
                    if len(params) > 1:
                        seller_id = int(params[1])
                        
                        if len(params) > 2 and params[2] == "confirm":
                            # Confirm block
                            seller = user_service.get_by_id(seller_id)
                            if seller and seller.role == UserRole.SELLER:
                                user_service.update_status(seller_id, UserStatus.BANNED)
                                await event.answer(f"فروشنده {seller.first_name} مسدود شد")
                                await handle_list_sellers(event, 1, user_service)
                            else:
                                await event.answer("فروشنده مورد نظر یافت نشد", alert=True)
                                from src.bot.keyboards.admin_keyboard import SellerManagementKeyboards
                                keyboard = SellerManagementKeyboards.get_seller_management_keyboard()
                                await event.edit("👨‍💼 **مدیریت فروشندگان**", buttons=keyboard)
                        else:
                            # Ask for confirmation
                            seller = user_service.get_by_id(seller_id)
                            if seller and seller.role == UserRole.SELLER:
                                message = f"🚫 **مسدود کردن فروشنده**\n\nآیا از مسدود کردن فروشنده «{seller.first_name} {seller.last_name or ''}» اطمینان دارید؟"
                                
                                buttons = [
                                    [
                                        Button.inline("✅ بله، مسدود شود", f"admin:sellers:block:{seller_id}:confirm"),
                                        Button.inline("❌ انصراف", f"admin:sellers:edit:{seller_id}")
                                    ]
                                ]
                                
                                await event.edit(message, buttons=buttons)
                            else:
                                await event.answer("فروشنده مورد نظر یافت نشد", alert=True)
                                from src.bot.keyboards.admin_keyboard import SellerManagementKeyboards
                                keyboard = SellerManagementKeyboards.get_seller_management_keyboard()
                                await event.edit("👨‍💼 **مدیریت فروشندگان**", buttons=keyboard)
                    else:
                        await event.answer("شناسه فروشنده نامعتبر است", alert=True)
                        from src.bot.keyboards.admin_keyboard import SellerManagementKeyboards
                        keyboard = SellerManagementKeyboards.get_seller_management_keyboard()
                        await event.edit("👨‍💼 **مدیریت فروشندگان**", buttons=keyboard)
                
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
                
                elif action == "back_to_menu":
                    # Back to seller management menu
                    from src.bot.keyboards.admin_keyboard import SellerManagementKeyboards
                    keyboard = SellerManagementKeyboards.get_seller_management_keyboard()
                    
                    message = (
                        "👨‍💼 **مدیریت فروشندگان**\n\n"
                        "از این بخش می‌توانید فروشندگان سیستم را مدیریت کنید.\n"
                        "لطفاً یکی از گزینه‌های زیر را انتخاب کنید:"
                    )
                    
                    await event.edit(message, buttons=keyboard)
                
                else:
                    await event.answer("عملیات نامعتبر", alert=True)
                    from src.bot.keyboards.admin_keyboard import SellerManagementKeyboards
                    keyboard = SellerManagementKeyboards.get_seller_management_keyboard()
                    await event.edit("👨‍💼 **مدیریت فروشندگان**", buttons=keyboard)
        
        except Exception as e:
            log_error("Error in handle_admin_sellers", e, event.sender_id)
            await event.answer("خطایی رخ داد. لطفاً دوباره تلاش کنید.", alert=True)

async def handle_list_sellers(event: events.CallbackQuery.Event, page: int, user_service: UserService) -> None:
    """Handle listing sellers"""
    try:
        # Get all sellers with pagination
        per_page = 5
        sellers = user_service.get_users_by_role(UserRole.SELLER, page=page, per_page=per_page)
        total_sellers = user_service.count_users_by_role(UserRole.SELLER)
        total_pages = (total_sellers + per_page - 1) // per_page
        
        message = f"👨‍💼 **لیست فروشندگان**\n\nصفحه {page} از {total_pages}\n\n"
        
        if not sellers:
            message += "هیچ فروشنده‌ای در سیستم ثبت نشده است."
        else:
            for i, seller in enumerate(sellers, 1):
                status_emoji = "✅" if seller.status == UserStatus.ACTIVE else "🚫"
                message += (
                    f"{i}. {status_emoji} {seller.first_name} {seller.last_name or ''}\n"
                    f"   👤 شناسه: {seller.id}\n"
                    f"   📱 یوزرنیم: @{seller.username or 'تنظیم نشده'}\n"
                    f"   📆 تاریخ ثبت‌نام: {seller.created_at.strftime('%Y-%m-%d')}\n\n"
                )
        
        # Create keyboard with pagination
        from src.bot.keyboards.admin_keyboard import SellerManagementKeyboards
        keyboard = SellerManagementKeyboards.get_seller_list_keyboard(page, total_pages)
        
        await event.edit(message, buttons=keyboard)
    
    except Exception as e:
        log_error("Error in handle_list_sellers", e, event.sender_id)
        await event.answer("خطایی رخ داد. لطفاً دوباره تلاش کنید.", alert=True)

async def handle_add_seller(event: events.CallbackQuery.Event, user_service: UserService) -> None:
    """Handle adding a new seller"""
    try:
        message = (
            "➕ **افزودن فروشنده جدید**\n\n"
            "برای افزودن فروشنده جدید، لطفاً یوزرنیم تلگرام شخص را وارد کنید.\n"
            "مثال: @username\n\n"
            "یا می‌توانید شناسه عددی تلگرام کاربر را وارد کنید."
        )
        
        # Set user state to add seller
        sender = await event.get_sender()
        user_service.set_user_state(sender.id, "add_seller")
        
        await event.edit(message, buttons=[[Button.inline("« بازگشت", "admin:sellers:back_to_menu")]])
    
    except Exception as e:
        log_error("Error in handle_add_seller", e, event.sender_id)
        await event.answer("خطایی رخ داد. لطفاً دوباره تلاش کنید.", alert=True)

async def handle_search_seller(event: events.CallbackQuery.Event, params: List[str], user_service: UserService) -> None:
    """Handle searching for a seller"""
    try:
        if not params:
            # Show search form
            message = (
                "🔍 **جستجوی فروشنده**\n\n"
                "برای جستجوی فروشنده، لطفاً نام، نام خانوادگی، یوزرنیم یا شناسه فروشنده را وارد کنید."
            )
            
            # Set user state to search seller
            sender = await event.get_sender()
            user_service.set_user_state(sender.id, "search_seller")
            
            await event.edit(message, buttons=[[Button.inline("« بازگشت", "admin:sellers:back_to_menu")]])
        
        else:
            # Show search results
            query = params[0]
            sellers = user_service.search_users_by_role(query, UserRole.SELLER)
            
            message = f"🔍 **نتایج جستجو برای: {query}**\n\n"
            
            if not sellers:
                message += "هیچ فروشنده‌ای با این مشخصات یافت نشد."
                await event.edit(message, buttons=[[Button.inline("« بازگشت", "admin:sellers:back_to_menu")]])
                return
            
            message += f"تعداد نتایج: {len(sellers)}\n\n"
            
            for i, seller in enumerate(sellers, 1):
                status_emoji = "✅" if seller.status == UserStatus.ACTIVE else "🚫"
                message += (
                    f"{i}. {status_emoji} {seller.first_name} {seller.last_name or ''}\n"
                    f"   👤 شناسه: {seller.id}\n"
                    f"   📱 یوزرنیم: @{seller.username or 'تنظیم نشده'}\n\n"
                )
                
                # Add action buttons for each seller
                if i <= 5:  # Limit number of action buttons to avoid message too long
                    buttons = []
                    buttons.append([
                        Button.inline(f"📝 ویرایش {seller.first_name}", f"admin:sellers:edit:{seller.id}"),
                        Button.inline(f"📦 محصولات", f"admin:sellers:products:{seller.id}")
                    ])
                    message += "\n"
            
            await event.edit(message, buttons=[[Button.inline("« بازگشت", "admin:sellers:back_to_menu")]])
    
    except Exception as e:
        log_error("Error in handle_search_seller", e, event.sender_id)
        await event.answer("خطایی رخ داد. لطفاً دوباره تلاش کنید.", alert=True)

async def handle_blocked_sellers(event: events.CallbackQuery.Event, page: int, user_service: UserService) -> None:
    """Handle listing blocked sellers"""
    try:
        # Get blocked sellers with pagination
        per_page = 5
        blocked_sellers = user_service.get_users_by_role_and_status(
            UserRole.SELLER, UserStatus.BANNED, page=page, per_page=per_page
        )
        total_blocked = user_service.count_users_by_role_and_status(UserRole.SELLER, UserStatus.BANNED)
        total_pages = (total_blocked + per_page - 1) // per_page
        
        message = f"🚫 **فروشندگان مسدود شده**\n\nصفحه {page} از {total_pages}\n\n"
        
        if not blocked_sellers:
            message += "هیچ فروشنده مسدودی در سیستم ثبت نشده است."
        else:
            for i, seller in enumerate(blocked_sellers, 1):
                message += (
                    f"{i}. {seller.first_name} {seller.last_name or ''}\n"
                    f"   👤 شناسه: {seller.id}\n"
                    f"   📱 یوزرنیم: @{seller.username or 'تنظیم نشده'}\n"
                    f"   📆 تاریخ مسدودی: {seller.updated_at.strftime('%Y-%m-%d')}\n\n"
                )
                
                # Add unblock button for each seller
                if i <= 5:  # Limit number of action buttons
                    buttons = []
                    buttons.append([
                        Button.inline(f"✅ رفع مسدودی {seller.first_name}", f"admin:sellers:unblock:{seller.id}")
                    ])
                    message += "\n"
        
        # Create keyboard with pagination
        buttons = []
        
        # Pagination buttons
        pagination = []
        if page > 1:
            pagination.append(Button.inline("« صفحه قبل", f"admin:sellers:blocked:{page-1}"))
        
        if page < total_pages:
            pagination.append(Button.inline("صفحه بعد »", f"admin:sellers:blocked:{page+1}"))
            
        if pagination:
            buttons.append(pagination)
            
        # Back button
        buttons.append([Button.inline("« بازگشت", "admin:sellers:back_to_menu")])
        
        await event.edit(message, buttons=buttons)
    
    except Exception as e:
        log_error("Error in handle_blocked_sellers", e, event.sender_id)
        await event.answer("خطایی رخ داد. لطفاً دوباره تلاش کنید.", alert=True)

async def handle_edit_seller(event: events.CallbackQuery.Event, seller_id: int, user_service: UserService) -> None:
    """Handle editing a seller"""
    try:
        seller = user_service.get_by_id(seller_id)
        
        if not seller or seller.role != UserRole.SELLER:
            await event.answer("فروشنده مورد نظر یافت نشد", alert=True)
            await handle_list_sellers(event, 1, user_service)
            return
        
        # Show seller details and edit options
        status_text = "فعال" if seller.status == UserStatus.ACTIVE else "مسدود"
        message = (
            f"📝 **ویرایش اطلاعات فروشنده**\n\n"
            f"👤 نام: {seller.first_name} {seller.last_name or ''}\n"
            f"📱 یوزرنیم: @{seller.username or 'تنظیم نشده'}\n"
            f"🆔 شناسه: {seller.id}\n"
            f"📊 وضعیت: {status_text}\n"
            f"📆 تاریخ ثبت‌نام: {seller.created_at.strftime('%Y-%m-%d')}\n\n"
            f"برای ویرایش هر بخش، دکمه مربوطه را انتخاب کنید:"
        )
        
        # Create keyboard with edit options
        buttons = [
            [
                Button.inline("📝 ویرایش نام", f"admin:sellers:edit_name:{seller_id}"),
                Button.inline("📱 ویرایش یوزرنیم", f"admin:sellers:edit_username:{seller_id}")
            ],
            [
                Button.inline("📦 مشاهده محصولات", f"admin:sellers:products:{seller_id}"),
                Button.inline("🛒 مشاهده سفارشات", f"admin:sellers:orders:{seller_id}")
            ]
        ]
        
        # Add block/unblock button based on current status
        if seller.status == UserStatus.ACTIVE:
            buttons.append([Button.inline("🚫 مسدود کردن فروشنده", f"admin:sellers:block:{seller_id}")])
        else:
            buttons.append([Button.inline("✅ رفع مسدودی فروشنده", f"admin:sellers:unblock:{seller_id}")])
        
        # Add back button
        buttons.append([Button.inline("« بازگشت", "admin:sellers:back_to_menu")])
        
        await event.edit(message, buttons=buttons)
    
    except Exception as e:
        log_error("Error in handle_edit_seller", e, event.sender_id)
        await event.answer("خطایی رخ داد. لطفاً دوباره تلاش کنید.", alert=True)

async def handle_seller_products(event: events.CallbackQuery.Event, seller_id: int, page: int, user_service: UserService, session) -> None:
    """Handle viewing seller products"""
    try:
        seller = user_service.get_by_id(seller_id)
        
        if not seller or seller.role != UserRole.SELLER:
            await event.answer("فروشنده مورد نظر یافت نشد", alert=True)
            await handle_list_sellers(event, 1, user_service)
            return
        
        # Get seller products with pagination
        product_service = ProductService(session)
        per_page = 5
        products = product_service.get_products_by_seller(seller_id, page=page, per_page=per_page)
        total_products = product_service.count_products_by_seller(seller_id)
        total_pages = (total_products + per_page - 1) // per_page
        
        message = f"📦 **محصولات فروشنده: {seller.first_name} {seller.last_name or ''}**\n\nصفحه {page} از {total_pages}\n\n"
        
        if not products:
            message += "این فروشنده هیچ محصولی ثبت نکرده است."
        else:
            for i, product in enumerate(products, 1):
                status_emoji = "✅" if product.is_available else "❌"
                message += (
                    f"{i}. {status_emoji} {product.name}\n"
                    f"   💰 قیمت: {product.price} تومان\n"
                    f"   📦 موجودی: {product.stock}\n"
                    f"   👁 بازدید: {product.views}\n\n"
                )
        
        # Create keyboard with pagination and actions
        buttons = []
        
        # Add button to add new product for this seller
        buttons.append([Button.inline("➕ افزودن محصول جدید", f"admin:products:add_for_seller:{seller_id}")])
        
        # Pagination buttons
        pagination = []
        if page > 1:
            pagination.append(Button.inline("« صفحه قبل", f"admin:sellers:products:{seller_id}:{page-1}"))
        
        if page < total_pages:
            pagination.append(Button.inline("صفحه بعد »", f"admin:sellers:products:{seller_id}:{page+1}"))
            
        if pagination:
            buttons.append(pagination)
            
        # Back button
        buttons.append([Button.inline("« بازگشت", f"admin:sellers:edit:{seller_id}")])
        
        await event.edit(message, buttons=buttons)
    
    except Exception as e:
        log_error("Error in handle_seller_products", e, event.sender_id)
        await event.answer("خطایی رخ داد. لطفاً دوباره تلاش کنید.", alert=True)

async def handle_seller_orders(event: events.CallbackQuery.Event, seller_id: int, page: int, user_service: UserService, session) -> None:
    """Handle viewing seller orders"""
    try:
        seller = user_service.get_by_id(seller_id)
        
        if not seller or seller.role != UserRole.SELLER:
            await event.answer("فروشنده مورد نظر یافت نشد", alert=True)
            await handle_list_sellers(event, 1, user_service)
            return
        
        # Get seller orders with pagination
        order_service = OrderService(session)
        per_page = 5
        orders = order_service.get_seller_orders(seller_id, page=page, per_page=per_page)
        total_orders = order_service.count_seller_orders(seller_id)
        total_pages = (total_orders + per_page - 1) // per_page
        
        message = f"🛒 **سفارشات فروشنده: {seller.first_name} {seller.last_name or ''}**\n\nصفحه {page} از {total_pages}\n\n"
        
        if not orders:
            message += "این فروشنده هیچ سفارشی ندارد."
        else:
            for i, order in enumerate(orders, 1):
                message += (
                    f"{i}. سفارش #{order.id}\n"
                    f"   👤 خریدار: {order.user.first_name} (شناسه: {order.user_id})\n"
                    f"   💰 مبلغ: {order.total_amount} تومان\n"
                    f"   📊 وضعیت: {order.status}\n"
                    f"   📆 تاریخ: {order.created_at.strftime('%Y-%m-%d %H:%M')}\n\n"
                )
        
        # Create keyboard with pagination
        buttons = []
        
        # Pagination buttons
        pagination = []
        if page > 1:
            pagination.append(Button.inline("« صفحه قبل", f"admin:sellers:orders:{seller_id}:{page-1}"))
        
        if page < total_pages:
            pagination.append(Button.inline("صفحه بعد »", f"admin:sellers:orders:{seller_id}:{page+1}"))
            
        if pagination:
            buttons.append(pagination)
            
        # Back button
        buttons.append([Button.inline("« بازگشت", f"admin:sellers:edit:{seller_id}")])
        
        await event.edit(message, buttons=buttons)
    
    except Exception as e:
        log_error("Error in handle_seller_orders", e, event.sender_id)
        await event.answer("خطایی رخ داد. لطفاً دوباره تلاش کنید.", alert=True)

async def handle_seller_wallet(event: events.CallbackQuery.Event, seller_id: int, user_service: UserService, session) -> None:
    """Handle viewing seller wallet"""
    try:
        seller = user_service.get_by_id(seller_id)
        
        if not seller or seller.role != UserRole.SELLER:
            await event.answer("فروشنده مورد نظر یافت نشد", alert=True)
            await handle_list_sellers(event, 1, user_service)
            return
        
        # Get seller wallet info
        wallet_service = WalletService(session)
        wallet = wallet_service.get_user_wallet(seller_id)
        
        # Get recent transactions
        transactions = wallet_service.get_user_transactions(seller_id, limit=5)
        
        message = (
            f"💰 **کیف پول فروشنده: {seller.first_name} {seller.last_name or ''}**\n\n"
            f"💵 موجودی: {wallet.balance if wallet else 0} تومان\n\n"
        )
        
        if transactions:
            message += "📋 تراکنش‌های اخیر:\n\n"
            for i, tx in enumerate(transactions, 1):
                tx_type = "واریز" if tx.amount > 0 else "برداشت"
                message += (
                    f"{i}. {tx_type}: {abs(tx.amount)} تومان\n"
                    f"   📝 توضیحات: {tx.description or '-'}\n"
                    f"   📆 تاریخ: {tx.created_at.strftime('%Y-%m-%d %H:%M')}\n\n"
                )
        else:
            message += "هیچ تراکنشی برای این فروشنده ثبت نشده است."
        
        # Create keyboard with wallet actions
        buttons = [
            [
                Button.inline("➕ افزایش موجودی", f"admin:sellers:add_funds:{seller_id}"),
                Button.inline("➖ کاهش موجودی", f"admin:sellers:deduct_funds:{seller_id}")
            ],
            [
                Button.inline("📜 تمام تراکنش‌ها", f"admin:sellers:transactions:{seller_id}")
            ],
            [
                Button.inline("« بازگشت", f"admin:sellers:edit:{seller_id}")
            ]
        ]
        
        await event.edit(message, buttons=buttons)
    
    except Exception as e:
        log_error("Error in handle_seller_wallet", e, event.sender_id)
        await event.answer("خطایی رخ داد. لطفاً دوباره تلاش کنید.", alert=True) 