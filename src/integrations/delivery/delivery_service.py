from core.models import DeliveryAddress, Order
from core.database import SessionLocal
from sqlalchemy.sql import func
import random
import logging

logger = logging.getLogger(__name__)

class DeliveryManager:
    @staticmethod
    async def add_addresses(addresses: list, city: str, province: str, added_by: int) -> bool:
        """Add new delivery addresses"""
        try:
            with SessionLocal() as db:
                for address in addresses:
                    new_address = DeliveryAddress(
                        address=address,
                        city=city,
                        province=province,
                        added_by=added_by
                    )
                    db.add(new_address)
                db.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding addresses: {e}")
            return False

    @staticmethod
    async def get_random_address(city: str) -> DeliveryAddress:
        """Get random unused address for delivery"""
        with SessionLocal() as db:
            available_addresses = (
                db.query(DeliveryAddress)
                .filter(
                    DeliveryAddress.city == city,
                    DeliveryAddress.is_used == False
                )
                .all()
            )
            
            if not available_addresses:
                return None
                
            address = random.choice(available_addresses)
            address.is_used = True
            address.used_at = func.now()
            db.commit()
            
            return address

    @staticmethod
    async def mark_address_used(address_id: int, order_id: str) -> bool:
        """Mark address as used and associate with order"""
        try:
            with SessionLocal() as db:
                address = db.query(DeliveryAddress).get(address_id)
                if address and not address.is_used:
                    address.is_used = True
                    address.used_at = func.now()
                    address.order_id = order_id
                    db.commit()
                    return True
            return False
        except Exception as e:
            logger.error(f"Error marking address as used: {e}")
            return False


from sqlalchemy.sql import func
from core.models import DeliveryAddress
from core.database import SessionLocal
from typing import Optional
import random

class DeliveryManager:
    @staticmethod
    def get_random_address(city: str) -> Optional[DeliveryAddress]:
        """Get random unused delivery address for a city"""
        with SessionLocal() as db:
            available_addresses = (
                db.query(DeliveryAddress)
                .filter(
                    DeliveryAddress.city == city,
                    DeliveryAddress.is_used == False
                )
                .all()
            )
            if not available_addresses:
                return None
            
            address = random.choice(available_addresses)
            address.is_used = True
            address.used_at = func.now()
            db.commit()
            return address

    @staticmethod
    def add_addresses(addresses: list, city: str, province: str, added_by: int) -> bool:
        """Add new delivery addresses"""
        try:
            with SessionLocal() as db:
                for address in addresses:
                    new_address = DeliveryAddress(
                        address=address,
                        city=city,
                        province=province,
                        added_by=added_by
                    )
                    db.add(new_address)
                db.commit()
            return True
        except Exception as e:
            return False

from core.models import Order, DeliveryAddress
from core.database import SessionLocal
from core.notification_manager import NotificationManager
from bot.utils import generate_order_id
import logging

logger = logging.getLogger(__name__)

class OrderManager:
    @staticmethod
    async def create_order(user_id: int, product_id: int, quantity: int) -> Order:
        """Create new order"""
        with SessionLocal() as db:
            # Get random delivery address
            address = db.query(DeliveryAddress)\
                .filter(DeliveryAddress.is_used == False)\
                .first()
            
            if not address:
                raise Exception("No delivery address available")

            order = Order(
                order_id=generate_order_id(),
                buyer_id=user_id,
                product_id=product_id,
                quantity=quantity,
                delivery_address_id=address.id,
                status="pending"
            )
            
            db.add(order)
            address.is_used = True
            db.commit()
            
            # Notify seller
            await NotificationManager.notify_new_order(order.id)
            
            return order

    @staticmethod
    async def update_order_status(order_id: str, status: str) -> bool:
        """Update order status"""
        with SessionLocal() as db:
            order = db.query(Order).filter(Order.order_id == order_id).first()
            if order:
                order.status = status
                db.commit()
                # Notify buyer
                await NotificationManager.notify_order_status(order.buyer_id, order_id, status)
                return True
            return False


from enum import Enum
from datetime import datetime
from core.models import Order
from core.database import SessionLocal
from core.notification_manager import NotificationManager
import logging

logger = logging.getLogger(__name__)

class OrderStatus(Enum):
    PENDING = "pending"
    PAYMENT_WAITING = "payment_waiting"
    PAID = "paid"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class OrderStatusManager:
    @staticmethod
    async def update_status(order_id: str, new_status: OrderStatus) -> bool:
        try:
            with SessionLocal() as db:
                order = db.query(Order).filter(Order.order_id == order_id).first()
                if not order:
                    return False
                    
                order.status = new_status.value
                order.updated_at = datetime.now()
                db.commit()
                
                # Send notifications
                await NotificationManager.notify_status_change(
                    order.buyer_id,
                    order_id,
                    new_status.value
                )
                return True
                
        except Exception as e:
            logger.error(f"Error updating order status: {e}")
            return False

    @staticmethod
    async def can_transition(current_status: str, new_status: OrderStatus) -> bool:
        """Check if status transition is valid"""
        valid_transitions = {
            "pending": [OrderStatus.PAYMENT_WAITING, OrderStatus.CANCELLED],
            "payment_waiting": [OrderStatus.PAID, OrderStatus.CANCELLED],
            "paid": [OrderStatus.PROCESSING, OrderStatus.CANCELLED],
            "processing": [OrderStatus.SHIPPED, OrderStatus.CANCELLED],
            "shipped": [OrderStatus.DELIVERED, OrderStatus.CANCELLED],
            "delivered": [],
            "cancelled": []
        }
        return new_status in valid_transitions.get(current_status, [])
