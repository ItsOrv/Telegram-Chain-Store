from typing import Optional, Union
from datetime import datetime
from core.models import User, Order
from core.database import SessionLocal
from bot.telethon_client import telegram_manager
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class NotificationManager:
    @classmethod
    async def send_message(cls, user_id: int, message: str, silent: bool = False):
        """Send notification to user"""
        if not settings.ENABLE_NOTIFICATIONS:
            return
            
        try:
            await telegram_manager.send_notification(user_id, message, silent)
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")

    @classmethod
    async def notify_order_status(cls, user_id: int, order_id: str, status: str):
        """Notify user about order status change"""
        message = f"Order #{order_id} status updated to: {status}"
        await cls.send_message(user_id, message)

    @classmethod
    async def notify_payment(cls, user_id: int, order_id: str, status: str, amount: float):
        """Notify user about payment status"""
        message = f"Payment {status} for Order #{order_id}\nAmount: {amount} USDT"
        await cls.send_message(user_id, message)

    @classmethod
    async def notify_delivery_address(cls, user_id: int, order_id: str, address: str):
        """Send delivery address to user"""
        message = f"🏠 Delivery address for Order #{order_id}:\n\n{address}"
        # Send silently for security
        await cls.send_message(user_id, message, silent=True)

    @classmethod
    async def notify_admin(cls, message: str):
        """Send notification to admin"""
        with SessionLocal() as db:
            admin = db.query(User).filter(User.role == "head").first()
            if admin:
                await cls.send_message(int(admin.telegram_id), f"👤 ADMIN: {message}")

notification_manager = NotificationManager()
