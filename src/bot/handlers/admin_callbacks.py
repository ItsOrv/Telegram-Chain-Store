from telethon import events
from src.utils.logger import setup_logger, log_error
from src.core.database import get_db_session
from src.core.services.user_service import UserService
from src.core.services.product_service import ProductService
from src.core.services.order_service import OrderService
from src.core.services.payment_service import PaymentService
from src.bot.handlers.callback_router import register_callback
from typing import List
from src.core.models.user import UserRole, UserStatus

# Initialize logger
logger = setup_logger("admin_callbacks")

def register_admin_callbacks():
    """Register admin-related callback handlers"""
    logger.info("Registering admin callbacks")
    
    @register_callback("admin")
    async def handle_admin_actions(event: events.CallbackQuery.Event, params: List[str]) -> None:
        """Handle admin panel actions callback"""
        try:
            if len(params) < 1:
                await event.answer("Invalid action", alert=True)
                return
                
            action = params[0]  # users, orders, products, etc.
            sender = await event.get_sender()
            
            with get_db_session() as session:
                user_service = UserService(session)
                user = user_service.get_by_telegram_id(sender.id)
                
                if not user:
                    await event.answer("Please start the bot first", alert=True)
                    return
                
                # Check if user is admin
                if not user.is_admin:
                    await event.answer("You are not authorized to access admin panel", alert=True)
                    return
                
                if action == "users":
                    # Show users management
                    users = user_service.get_users(limit=10)
                    
                    message = (
                        f"👥 **User Management**\n\n"
                        f"Total users: {user_service.count_users()}\n\n"
                        f"Recent users:\n\n"
                    )
                    
                    for i, u in enumerate(users, 1):
                        message += (
                            f"{i}. {u.first_name} {u.last_name or ''} (@{u.username or 'N/A'})\n"
                            f"   ID: {u.id}, Role: {u.role}, Status: {u.status}\n\n"
                        )
                    
                    from src.bot.keyboards.user_keyboard import get_user_management_keyboard
                    keyboard = get_user_management_keyboard()
                    
                    await event.edit(message, buttons=keyboard)
                
                elif action == "orders":
                    # Show orders management
                    order_service = OrderService(session)
                    orders = order_service.get_recent_orders(limit=5)
                    
                    message = (
                        f"🧾 **Order Management**\n\n"
                        f"Total orders: {order_service.count_orders()}\n\n"
                        f"Recent orders:\n\n"
                    )
                    
                    for i, order in enumerate(orders, 1):
                        message += (
                            f"{i}. Order #{order.id}\n"
                            f"   User: {order.user.first_name} (ID: {order.user_id})\n"
                            f"   Amount: ${order.total_amount:.2f}, Status: {order.status}\n"
                            f"   Date: {order.created_at.strftime('%Y-%m-%d %H:%M')}\n\n"
                        )
                    
                    from src.bot.keyboards.order_keyboard import get_admin_orders_keyboard
                    keyboard = get_admin_orders_keyboard()
                    
                    await event.edit(message, buttons=keyboard)
                
                elif action == "products":
                    # Show products management
                    product_service = ProductService(session)
                    products = product_service.get_products(limit=5)
                    
                    message = (
                        f"🛍️ **Product Management**\n\n"
                        f"Total products: {product_service.count_products()}\n\n"
                        f"Recent products:\n\n"
                    )
                    
                    for i, product in enumerate(products, 1):
                        message += (
                            f"{i}. {product.name}\n"
                            f"   Price: ${product.price:.2f}, Stock: {product.stock}\n"
                            f"   Seller: {product.seller.first_name} (ID: {product.seller_id})\n\n"
                        )
                    
                    from src.bot.keyboards.product_keyboard import get_admin_products_keyboard
                    keyboard = get_admin_products_keyboard()
                    
                    await event.edit(message, buttons=keyboard)
                
                elif action == "payments":
                    # Show payments management
                    payment_service = PaymentService(session)
                    payments = payment_service.get_recent_payments(limit=5)
                    
                    message = (
                        f"💳 **Payment Management**\n\n"
                        f"Total payments: {payment_service.count_payments()}\n\n"
                        f"Recent payments:\n\n"
                    )
                    
                    for i, payment in enumerate(payments, 1):
                        message += (
                            f"{i}. Payment #{payment.id}\n"
                            f"   User: {payment.user.first_name} (ID: {payment.user_id})\n"
                            f"   Amount: ${float(payment.amount):.2f}, Status: {payment.status}\n"
                            f"   Method: {payment.payment_method}\n"
                            f"   Date: {payment.created_at.strftime('%Y-%m-%d %H:%M')}\n\n"
                        )
                    
                    from src.bot.keyboards.payment_keyboard import get_admin_payments_keyboard
                    keyboard = get_admin_payments_keyboard()
                    
                    await event.edit(message, buttons=keyboard)
                
                elif action == "locations":
                    # Show locations management
                    from src.core.services.location_service import LocationService
                    location_service = LocationService(session)
                    locations = location_service.get_locations(limit=5)
                    
                    message = (
                        f"📍 **Location Management**\n\n"
                        f"Total locations: {location_service.count_locations()}\n\n"
                        f"Recent locations:\n\n"
                    )
                    
                    for i, location in enumerate(locations, 1):
                        message += (
                            f"{i}. {location.name}\n"
                            f"   Address: {location.address}\n"
                            f"   Area: {location.area}, City: {location.city.name}\n\n"
                        )
                    
                    from src.bot.keyboards.location_keyboard import get_location_management_keyboard
                    keyboard = get_location_management_keyboard()
                    
                    await event.edit(message, buttons=keyboard)
                
                elif action == "stats":
                    # Show statistics
                    message = (
                        f"📊 **System Statistics**\n\n"
                        f"Users: {user_service.count_users()}\n"
                        f"• Admins: {user_service.count_users_by_role(UserRole.ADMIN)}\n"
                        f"• Sellers: {user_service.count_users_by_role(UserRole.SELLER)}\n"
                        f"• Buyers: {user_service.count_users_by_role(UserRole.BUYER)}\n"
                        f"• Cardholders: {user_service.count_users_by_role(UserRole.CARDHOLDER)}\n\n"
                    )
                    
                    order_service = OrderService(session)
                    payment_service = PaymentService(session)
                    product_service = ProductService(session)
                    
                    message += (
                        f"Products: {product_service.count_products()}\n"
                        f"Orders: {order_service.count_orders()}\n"
                        f"Payments: {payment_service.count_payments()}\n\n"
                        
                        f"Total Sales: ${order_service.get_total_sales():.2f}\n"
                        f"Pending Payments: {payment_service.count_pending_payments()}\n"
                    )
                    
                    from src.bot.keyboards.admin_keyboard import get_admin_keyboard
                    keyboard = get_admin_keyboard()
                    
                    await event.edit(message, buttons=keyboard)
                
                elif action == "back":
                    # Go back to admin panel
                    message = (
                        f"🛠️ **پنل مدیریت**\n\n"
                        f"خوش آمدید به پنل مدیریت، {user.first_name}.\n"
                        f"از اینجا می‌توانید سیستم را مدیریت کنید.\n\n"
                        f"لطفاً یک گزینه را انتخاب کنید:"
                    )
                    
                    from src.bot.keyboards.admin_keyboard import get_admin_keyboard
                    keyboard = get_admin_keyboard()
                    
                    await event.edit(message, buttons=keyboard)
                
                else:
                    await event.answer("Invalid action", alert=True)
                
        except Exception as e:
            log_error("Error in handle_admin_actions", e, event.sender_id)
            await event.answer("An error occurred. Please try again later.", alert=True)
    
    @register_callback("manage_user")
    async def handle_manage_user(event: events.CallbackQuery.Event, params: List[str]) -> None:
        """Handle user management callback"""
        try:
            if len(params) < 2:
                await event.answer("Invalid parameters", alert=True)
                return
                
            user_id = int(params[0])
            action = params[1]  # ban, unban, promote, demote, etc.
            sender = await event.get_sender()
            
            with get_db_session() as session:
                user_service = UserService(session)
                admin = user_service.get_by_telegram_id(sender.id)
                
                if not admin or not admin.is_admin:
                    await event.answer("You are not authorized", alert=True)
                    return
                
                user = user_service.get_by_id(user_id)
                
                if not user:
                    await event.answer("User not found", alert=True)
                    return
                
                # Process actions
                if action == "ban":
                    user_service.update_status(user_id, UserStatus.BANNED)
                    await event.answer(f"User {user.first_name} has been banned")
                
                elif action == "unban":
                    user_service.update_status(user_id, UserStatus.ACTIVE)
                    await event.answer(f"User {user.first_name} has been unbanned")
                
                elif action == "promote":
                    # Show role selection dialog
                    message = (
                        f"👤 **Promote User**\n\n"
                        f"User: {user.first_name} {user.last_name or ''}\n"
                        f"Current role: {user.role}\n\n"
                        f"Select new role:"
                    )
                    
                    from src.bot.keyboards.user_keyboard import get_role_selection_keyboard
                    keyboard = get_role_selection_keyboard(user_id)
                    
                    await event.edit(message, buttons=keyboard)
                    return
                
                elif action == "view":
                    # Show user details
                    message = (
                        f"👤 **User Details**\n\n"
                        f"ID: {user.id}\n"
                        f"Telegram ID: {user.telegram_id}\n"
                        f"Name: {user.first_name} {user.last_name or ''}\n"
                        f"Username: @{user.username or 'N/A'}\n"
                        f"Role: {user.role}\n"
                        f"Status: {user.status}\n"
                        f"Balance: ${user.balance:.2f}\n"
                        f"Joined: {user.created_at.strftime('%Y-%m-%d')}\n"
                        f"Last Login: {user.last_login.strftime('%Y-%m-%d %H:%M') if user.last_login else 'N/A'}\n"
                    )
                    
                    from src.bot.keyboards.user_keyboard import get_user_details_keyboard
                    keyboard = get_user_details_keyboard(user_id)
                    
                    await event.edit(message, buttons=keyboard)
                    return
                
                # Return to user management
                await handle_admin_actions(event, ["users"])
                
        except Exception as e:
            log_error("Error in handle_manage_user", e, event.sender_id)
            await event.answer("An error occurred. Please try again later.", alert=True)
    
    @register_callback("set_role")
    async def handle_set_role(event: events.CallbackQuery.Event, params: List[str]) -> None:
        """Handle role setting callback"""
        try:
            if len(params) < 2:
                await event.answer("Invalid parameters", alert=True)
                return
                
            user_id = int(params[0])
            role = params[1]  # admin, seller, buyer, cardholder
            sender = await event.get_sender()
            
            with get_db_session() as session:
                user_service = UserService(session)
                admin = user_service.get_by_telegram_id(sender.id)
                
                if not admin or not admin.is_admin:
                    await event.answer("You are not authorized", alert=True)
                    return
                
                user = user_service.get_by_id(user_id)
                
                if not user:
                    await event.answer("User not found", alert=True)
                    return
                
                # Update role
                if role == "admin":
                    user_service.update_role(user_id, UserRole.ADMIN)
                elif role == "seller":
                    user_service.update_role(user_id, UserRole.SELLER)
                elif role == "buyer":
                    user_service.update_role(user_id, UserRole.BUYER)
                elif role == "cardholder":
                    user_service.update_role(user_id, UserRole.CARDHOLDER)
                else:
                    await event.answer("Invalid role", alert=True)
                    return
                
                await event.answer(f"User {user.first_name} is now a {role}")
                
                # Return to user management
                await handle_admin_actions(event, ["users"])
                
        except Exception as e:
            log_error("Error in handle_set_role", e, event.sender_id)
            await event.answer("An error occurred. Please try again later.", alert=True)
            
    logger.info("Admin callbacks registered") 