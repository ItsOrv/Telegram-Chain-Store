from typing import Dict, Any
from datetime import datetime
from src.core.exceptions import AuthorizationError
from src.core.auth import Auth
from src.core.services.order_manager import OrderManager
from src.core.services.payment_manager import PaymentManager
from src.core.services.crypto_manager import CryptoManager

class AdminHandler:
    def __init__(self):
        self.order_manager = OrderManager()
        self.payment_manager = PaymentManager()
        self.crypto_manager = CryptoManager()

    async def handle_admin_command(self, message: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Handle admin commands"""
        try:
            # Check if user is admin
            user_id = message['from']['id']
            if not Auth.check_permissions(user_id, 'admin'):
                raise AuthorizationError("User is not authorized to use admin commands")

            command = message.get('text', '').split()[0].lower()
            
            if command == '/admin_stats':
                await self.handle_stats(message, context)
            elif command == '/admin_orders':
                await self.handle_orders(message, context)
            elif command == '/admin_payments':
                await self.handle_payments(message, context)
            elif command == '/admin_users':
                await self.handle_users(message, context)
            elif command == '/admin_products':
                await self.handle_products(message, context)
            else:
                await context.bot.send_message(
                    chat_id=message['chat']['id'],
                    text="Invalid admin command. Available commands:\n"
                         "/admin_stats - Get system statistics\n"
                         "/admin_orders - Manage orders\n"
                         "/admin_payments - Manage payments\n"
                         "/admin_users - Manage users\n"
                         "/admin_products - Manage products"
                )
        except Exception as e:
            await context.bot.send_message(
                chat_id=message['chat']['id'],
                text=f"Error processing admin command: {str(e)}"
            )

    async def handle_stats(self, message: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Handle /admin_stats command"""
        try:
            # Get system statistics
            stats = {
                "total_orders": self.order_manager.get_total_orders(),
                "total_payments": self.payment_manager.get_total_payments(),
                "total_users": self.get_total_users(),
                "total_products": self.get_total_products(),
                "system_uptime": self.get_system_uptime()
            }
            
            stats_text = (
                "📊 System Statistics:\n\n"
                f"Total Orders: {stats['total_orders']}\n"
                f"Total Payments: {stats['total_payments']}\n"
                f"Total Users: {stats['total_users']}\n"
                f"Total Products: {stats['total_products']}\n"
                f"System Uptime: {stats['system_uptime']}"
            )
            
            await context.bot.send_message(
                chat_id=message['chat']['id'],
                text=stats_text
            )
        except Exception as e:
            await context.bot.send_message(
                chat_id=message['chat']['id'],
                text=f"Error getting statistics: {str(e)}"
            )

    async def handle_orders(self, message: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Handle /admin_orders command"""
        try:
            # Get recent orders
            orders = self.order_manager.get_recent_orders(limit=10)
            
            orders_text = "📦 Recent Orders:\n\n"
            for order in orders:
                orders_text += (
                    f"Order #{order.id}\n"
                    f"User: {order.user.username}\n"
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
                text=f"Error getting orders: {str(e)}"
            )

    async def handle_payments(self, message: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Handle /admin_payments command"""
        try:
            # Get recent payments
            payments = self.payment_manager.get_recent_payments(limit=10)
            
            payments_text = "💳 Recent Payments:\n\n"
            for payment in payments:
                payments_text += (
                    f"Payment #{payment.id}\n"
                    f"Order: #{payment.order_id}\n"
                    f"Amount: {payment.amount} {payment.currency}\n"
                    f"Status: {payment.status}\n"
                    f"Date: {payment.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                )
            
            await context.bot.send_message(
                chat_id=message['chat']['id'],
                text=payments_text
            )
        except Exception as e:
            await context.bot.send_message(
                chat_id=message['chat']['id'],
                text=f"Error getting payments: {str(e)}"
            )

    async def handle_users(self, message: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Handle /admin_users command"""
        try:
            # Get recent users
            users = self.get_recent_users(limit=10)
            
            users_text = "👥 Recent Users:\n\n"
            for user in users:
                users_text += (
                    f"User: {user.username}\n"
                    f"ID: {user.id}\n"
                    f"Role: {user.role}\n"
                    f"Joined: {user.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                )
            
            await context.bot.send_message(
                chat_id=message['chat']['id'],
                text=users_text
            )
        except Exception as e:
            await context.bot.send_message(
                chat_id=message['chat']['id'],
                text=f"Error getting users: {str(e)}"
            )

    async def handle_products(self, message: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Handle /admin_products command"""
        try:
            # Get recent products
            products = self.get_recent_products(limit=10)
            
            products_text = "🛍️ Recent Products:\n\n"
            for product in products:
                products_text += (
                    f"Product: {product.name}\n"
                    f"ID: {product.id}\n"
                    f"Price: {product.price} USDT\n"
                    f"Stock: {product.stock}\n"
                    f"Added: {product.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                )
            
            await context.bot.send_message(
                chat_id=message['chat']['id'],
                text=products_text
            )
        except Exception as e:
            await context.bot.send_message(
                chat_id=message['chat']['id'],
                text=f"Error getting products: {str(e)}"
            )

    def get_total_users(self) -> int:
        """Get total number of users"""
        from src.core.models import User
        return User.get_total_count()

    def get_total_products(self) -> int:
        """Get total number of products"""
        from src.core.models import Product
        return Product.get_total_count()

    def get_system_uptime(self) -> str:
        """Get system uptime"""
        from datetime import datetime, timedelta
        start_time = datetime.utcnow() - timedelta(days=30)  # Example uptime
        uptime = datetime.utcnow() - start_time
        return f"{uptime.days} days, {uptime.seconds // 3600} hours"

    def get_recent_users(self, limit: int = 10) -> list:
        """Get recent users"""
        from src.core.models import User
        return User.get_recent(limit)

    def get_recent_products(self, limit: int = 10) -> list:
        """Get recent products"""
        from src.core.models import Product
        return Product.get_recent(limit)
