from telethon import events, Button
from src.core.database import SessionLocal
from src.core.models import User, UserRole
from src.bot.common.messages import Messages
from src.bot.common.keyboards import AdminKeyboards, DialogKeyboards, BaseKeyboard
from typing import Dict, Any, List
import logging
from src.utils.logger import (
    APP_LOGGER as logger,
    log_user_action,
    log_admin_action,
    log_error,
    log_ui_event,
    log_function_execution,
    log_db_operation
)
import traceback
from src.core.exceptions import ValidationError, OrderError
from src.core.auth import Auth
from src.core.services.order_manager import OrderManager
from src.core.services.payment_manager import PaymentManager
from src.core.services.crypto_manager import CryptoManager

class UserHandler:
    def __init__(self, client):
        self.client = client
        self.user_states: Dict[int, Dict] = {}
        logger.info("Initializing UserHandler")
        self.setup_handlers()
        self.order_manager = OrderManager()
        self.payment_manager = PaymentManager()
        self.crypto_manager = CryptoManager()

    @log_function_execution()
    async def get_users_stats(self) -> str:
        """Get users statistics"""
        try:
            with SessionLocal() as db:
                total_users = db.query(User).count()
                banned_users = db.query(User).filter(User.status == "BANNED").count()
                suspended_users = db.query(User).filter(User.status == "SUSPENDED").count()
                active_users = db.query(User).filter(User.status == "ACTIVE").count()

                logger.info(f"Retrieved user statistics: Total={total_users}, Active={active_users}, Banned={banned_users}, Suspended={suspended_users}")
                
                return Messages.USERS_STATS.format(
                    total=total_users,
                    active=active_users,
                    banned=banned_users,
                    suspended=suspended_users
                )
        except Exception as e:
            log_error("Error getting user statistics", e)
            return Messages.ERROR_OCCURRED

    @log_function_execution()
    async def show_error_message(self, event, error_msg):
        """Show error message with retry option"""
        user_id = event.sender_id
        logger.error(f"Showing error message to user {user_id}: {error_msg}")
        log_ui_event(user_id, "ERROR_DISPLAY", "dialog", {"error": error_msg})
        
        buttons = DialogKeyboards.get_error_handling()
        await event.edit(f"{Messages.ERROR_OCCURRED}\n{error_msg}", buttons=buttons)

    def setup_handlers(self):
        logger.info("Setting up user management handlers")
        
        @self.client.on(events.CallbackQuery(pattern="👤 Manage Users"))
        @log_function_execution()
        async def show_users_management(event):
            """Show users management panel"""
            try:
                # Check if user is admin
                user_id = event.sender_id
                logger.info(f"User {user_id} accessing user management panel")
                log_admin_action(user_id, "ACCESS_USER_MANAGEMENT")
                
                with SessionLocal() as db:
                    user = db.query(User).filter(User.telegram_id == str(user_id)).first()
                    if user.role != UserRole.ADMIN:
                        logger.warning(f"Unauthorized user management access from {user_id}")
                        log_admin_action(user_id, "UNAUTHORIZED_USER_MANAGEMENT")
                        await event.answer(Messages.UNAUTHORIZED, alert=True)
                        return

                # Get users statistics
                stats = await self.get_users_stats()
                log_admin_action(user_id, "VIEW_USER_STATISTICS")

                # Use keyboard from keyboard class
                buttons = AdminKeyboards.get_users_management()
                log_ui_event(user_id, "SHOW_PANEL", "user_management", {"panel": "user_management"})
                await event.edit(stats, buttons=buttons)

            except Exception as e:
                user_id = event.sender_id
                log_error("Error in show_users_management", e, user_id)
                logger.error(f"Error in show_users_management: {str(e)}")
                logger.error(traceback.format_exc())
                await event.answer(Messages.ERROR_OCCURRED, alert=True)

        @log_function_execution()
        async def handle_user_action(event, action: str):
            """Generic handler for user status actions"""
            user_id = event.sender_id
            logger.info(f"User {user_id} initiating {action} action")
            log_admin_action(user_id, f"INITIATE_{action.upper()}_USER")
            
            self.user_states[user_id] = {"action": action}
            action_messages = {
                "ban": Messages.ENTER_USER_ID_BAN,
                "unban": Messages.ENTER_USER_ID_UNBAN,
                "suspend": Messages.ENTER_USER_ID_SUSPEND,
                "unsuspend": Messages.ENTER_USER_ID_UNSUSPEND
            }
            
            log_ui_event(user_id, "SHOW_INPUT", "user_action", {"action": action})
            await event.edit(action_messages[action])

        for pattern, action in [
            ("ban_user", "ban"),
            ("unban_user", "unban"),
            ("suspend_user", "suspend"),
            ("unsuspend_user", "unsuspend")
        ]:
            @self.client.on(events.CallbackQuery(pattern=pattern))
            async def user_action_handler(event, action=action):
                await handle_user_action(event, action)

        @self.client.on(events.NewMessage())
        @log_function_execution()
        async def handle_user_input(event):
            """Handle user ID input for actions"""
            user_id = event.sender_id
            state = self.user_states.get(user_id)
            
            if not state:
                return

            try:
                target_id = event.text
                logger.info(f"Admin {user_id} entered target user ID: {target_id}")
                
                try:
                    target_id = int(target_id)
                except ValueError:
                    logger.warning(f"Invalid user ID format: {target_id}")
                    log_admin_action(user_id, "INVALID_USER_ID_FORMAT", details={"input": target_id})
                    await event.respond(Messages.INVALID_USER_ID)
                    return
                    
                action = state["action"]
                log_admin_action(user_id, f"ATTEMPT_{action.upper()}_USER", target_id)
                
                with SessionLocal() as db:
                    # Check if admin
                    admin = db.query(User).filter(User.telegram_id == str(user_id)).first()
                    if admin.role != UserRole.ADMIN:
                        logger.warning(f"Non-admin user {user_id} attempting user action")
                        log_admin_action(user_id, "UNAUTHORIZED_ADMIN_ACTION")
                        await event.respond(Messages.UNAUTHORIZED)
                        return

                    # Get target user
                    target_user = db.query(User).filter(User.telegram_id == str(target_id)).first()
                    if not target_user:
                        logger.warning(f"Target user {target_id} not found")
                        log_admin_action(user_id, "USER_NOT_FOUND", target_id)
                        await event.respond(Messages.USER_NOT_FOUND)
                        return

                    # Update user status
                    status_map = {
                        "ban": "BANNED",
                        "unban": "ACTIVE",
                        "suspend": "SUSPENDED",
                        "unsuspend": "ACTIVE"
                    }
                    
                    previous_status = target_user.status
                    new_status = status_map[action]
                    
                    logger.info(f"Updating user {target_id} status from {previous_status} to {new_status}")
                    
                    target_user.status = new_status
                    db.commit()
                    
                    log_db_operation("UPDATE", "users", target_user.id, {
                        "field": "status",
                        "previous_value": previous_status,
                        "new_value": new_status
                    })
                    
                    log_admin_action(user_id, f"{action.upper()}_USER_SUCCESS", target_id, {
                        "previous_status": previous_status,
                        "new_status": new_status
                    })

                    # Send confirmation
                    await event.respond(Messages.USER_STATUS_UPDATED.format(
                        user_id=target_id,
                        status=new_status.lower()
                    ))

                    # Clear state
                    del self.user_states[user_id]
                    logger.info(f"Cleared state for admin {user_id} after {action} action")

                    # Show updated stats
                    stats = await self.get_users_stats()
                    buttons = AdminKeyboards.get_users_management()
                    log_ui_event(user_id, "SHOW_PANEL", "user_management", {"panel": "user_management", "after_action": action})
                    await event.respond(stats, buttons=buttons)

            except ValueError:
                logger.warning(f"Invalid user ID input from admin {user_id}: {event.text}")
                log_admin_action(user_id, "INVALID_USER_ID", details={"input": event.text})
                await event.respond(Messages.INVALID_USER_ID)
            except Exception as e:
                log_error(f"Error handling user action", e, user_id)
                logger.error(f"Error handling user action: {str(e)}")
                logger.error(traceback.format_exc())
                await event.respond(Messages.ERROR_OCCURRED)

    async def handle_user_command(self, message: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Handle user commands"""
        try:
            user_id = message['from']['id']
            command = message.get('text', '').split()[0].lower()
            
            if command == '/start':
                await self.handle_start(message, context)
            elif command == '/help':
                await self.handle_help(message, context)
            elif command == '/profile':
                await self.handle_profile(message, context)
            elif command == '/orders':
                await self.handle_orders(message, context)
            elif command == '/products':
                await self.handle_products(message, context)
            elif command == '/cart':
                await self.handle_cart(message, context)
            elif command == '/checkout':
                await self.handle_checkout(message, context)
            elif command == '/support':
                await self.handle_support(message, context)
            else:
                await context.bot.send_message(
                    chat_id=message['chat']['id'],
                    text="Invalid command. Available commands:\n"
                         "/start - Start the bot\n"
                         "/help - Show help message\n"
                         "/profile - View your profile\n"
                         "/orders - View your orders\n"
                         "/products - Browse products\n"
                         "/cart - View your cart\n"
                         "/checkout - Checkout your cart\n"
                         "/support - Contact support"
                )
        except Exception as e:
            await context.bot.send_message(
                chat_id=message['chat']['id'],
                text=f"Error processing command: {str(e)}"
            )

    async def handle_start(self, message: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Handle /start command"""
        try:
            user_id = message['from']['id']
            username = message['from'].get('username', 'User')
            
            welcome_text = (
                f"👋 Welcome {username}!\n\n"
                "I'm your Telegram Shop Bot. Here's what you can do:\n\n"
                "🛍️ /products - Browse our products\n"
                "🛒 /cart - View your shopping cart\n"
                "💳 /checkout - Complete your purchase\n"
                "📋 /orders - View your order history\n"
                "👤 /profile - Manage your profile\n"
                "❓ /help - Get help and support\n\n"
                "Need assistance? Use /support to contact us."
            )
            
            await context.bot.send_message(
                chat_id=message['chat']['id'],
                text=welcome_text
            )
        except Exception as e:
            await context.bot.send_message(
                chat_id=message['chat']['id'],
                text=f"Error starting bot: {str(e)}"
            )

    async def handle_help(self, message: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Handle /help command"""
        try:
            help_text = (
                "📚 Help Guide:\n\n"
                "Shopping:\n"
                "• /products - Browse available products\n"
                "• /cart - View your shopping cart\n"
                "• /checkout - Complete your purchase\n\n"
                "Account:\n"
                "• /profile - View and edit your profile\n"
                "• /orders - View your order history\n\n"
                "Support:\n"
                "• /support - Contact customer support\n\n"
                "Need more help? Contact our support team using /support"
            )
            
            await context.bot.send_message(
                chat_id=message['chat']['id'],
                text=help_text
            )
        except Exception as e:
            await context.bot.send_message(
                chat_id=message['chat']['id'],
                text=f"Error showing help: {str(e)}"
            )

    async def handle_profile(self, message: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Handle /profile command"""
        try:
            user_id = message['from']['id']
            user = self.get_user(user_id)
            
            if not user:
                raise ValidationError("User not found")
            
            profile_text = (
                "👤 Your Profile:\n\n"
                f"Username: {user.username}\n"
                f"Email: {user.email}\n"
                f"Phone: {user.phone}\n"
                f"Joined: {user.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"Total Orders: {self.get_user_total_orders(user_id)}\n"
                f"Total Spent: {self.get_user_total_spent(user_id)} USDT\n\n"
                "To update your profile, please contact support."
            )
            
            await context.bot.send_message(
                chat_id=message['chat']['id'],
                text=profile_text
            )
        except Exception as e:
            await context.bot.send_message(
                chat_id=message['chat']['id'],
                text=f"Error viewing profile: {str(e)}"
            )

    async def handle_orders(self, message: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Handle /orders command"""
        try:
            user_id = message['from']['id']
            orders = self.order_manager.get_user_orders(user_id)
            
            if not orders:
                await context.bot.send_message(
                    chat_id=message['chat']['id'],
                    text="You haven't placed any orders yet."
                )
                return
            
            orders_text = "📋 Your Orders:\n\n"
            for order in orders:
                orders_text += (
                    f"Order #{order.id}\n"
                    f"Amount: {order.total_amount} USDT\n"
                    f"Status: {order.status}\n"
                    f"Date: {order.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                )
            
            await context.bot.send_message(
                chat_id=message['chat']['id'],
                text=orders_text
            )
        except Exception as e:
            await context.bot.send_message(
                chat_id=message['chat']['id'],
                text=f"Error viewing orders: {str(e)}"
            )

    async def handle_products(self, message: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Handle /products command"""
        try:
            products = self.get_available_products()
            
            if not products:
                await context.bot.send_message(
                    chat_id=message['chat']['id'],
                    text="No products available at the moment."
                )
                return
            
            products_text = "🛍️ Available Products:\n\n"
            for product in products:
                products_text += (
                    f"Product: {product.name}\n"
                    f"Price: {product.price} USDT\n"
                    f"Stock: {product.stock}\n"
                    f"Description: {product.description}\n\n"
                )
            
            await context.bot.send_message(
                chat_id=message['chat']['id'],
                text=products_text
            )
        except Exception as e:
            await context.bot.send_message(
                chat_id=message['chat']['id'],
                text=f"Error viewing products: {str(e)}"
            )

    async def handle_cart(self, message: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Handle /cart command"""
        try:
            user_id = message['from']['id']
            cart = self.get_user_cart(user_id)
            
            if not cart or not cart.items:
                await context.bot.send_message(
                    chat_id=message['chat']['id'],
                    text="Your cart is empty."
                )
                return
            
            cart_text = "🛒 Your Cart:\n\n"
            for item in cart.items:
                cart_text += (
                    f"Product: {item.product.name}\n"
                    f"Quantity: {item.quantity}\n"
                    f"Price: {item.price} USDT\n"
                    f"Subtotal: {item.quantity * item.price} USDT\n\n"
                )
            
            cart_text += f"Total: {cart.total_amount} USDT"
            
            await context.bot.send_message(
                chat_id=message['chat']['id'],
                text=cart_text
            )
        except Exception as e:
            await context.bot.send_message(
                chat_id=message['chat']['id'],
                text=f"Error viewing cart: {str(e)}"
            )

    async def handle_checkout(self, message: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Handle /checkout command"""
        try:
            user_id = message['from']['id']
            cart = self.get_user_cart(user_id)
            
            if not cart or not cart.items:
                raise OrderError("Your cart is empty")
            
            # Create order
            order_data = {
                "user_id": user_id,
                "items": cart.items,
                "total_amount": cart.total_amount
            }
            
            order = self.order_manager.create_order(order_data)
            
            # Generate payment address
            payment_address = self.crypto_manager.generate_wallet_address()
            
            checkout_text = (
                "💳 Checkout:\n\n"
                f"Order #{order.id}\n"
                f"Total Amount: {order.total_amount} USDT\n\n"
                "Please send the payment to this address:\n"
                f"{payment_address}\n\n"
                "After sending the payment, please use the /confirm_payment command with your transaction hash."
            )
            
            await context.bot.send_message(
                chat_id=message['chat']['id'],
                text=checkout_text
            )
        except Exception as e:
            await context.bot.send_message(
                chat_id=message['chat']['id'],
                text=f"Error during checkout: {str(e)}"
            )

    async def handle_support(self, message: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Handle /support command"""
        try:
            support_text = (
                "💬 Support:\n\n"
                "Need help? Our support team is here for you!\n\n"
                "Contact us:\n"
                "• Email: support@example.com\n"
                "• Telegram: @support_bot\n"
                "• Hours: 24/7\n\n"
                "For urgent issues, please use our Telegram support channel."
            )
            
            await context.bot.send_message(
                chat_id=message['chat']['id'],
                text=support_text
            )
        except Exception as e:
            await context.bot.send_message(
                chat_id=message['chat']['id'],
                text=f"Error contacting support: {str(e)}"
            )

    def get_user(self, user_id: int) -> Any:
        """Get user by ID"""
        from src.core.models import User
        return User.get_by_id(user_id)

    def get_user_total_orders(self, user_id: int) -> int:
        """Get total number of orders for user"""
        return self.order_manager.get_user_total_orders(user_id)

    def get_user_total_spent(self, user_id: int) -> float:
        """Get total amount spent by user"""
        return self.order_manager.get_user_total_spent(user_id)

    def get_available_products(self) -> List[Any]:
        """Get available products"""
        from src.core.models import Product
        return Product.get_available()

    def get_user_cart(self, user_id: int) -> Any:
        """Get user's cart"""
        from src.core.models import Cart
        return Cart.get_by_user_id(user_id)
