from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, func
from src.core.models.order import Order, OrderItem, OrderStatus
from src.core.models.product import Product
from src.core.models.user import User
from src.core.models.payment import Payment, PaymentStatus, PaymentType
from src.core.models.base import BaseOrder, BaseOrderItem
from src.core.services.base_service import BaseService
from src.core.services.notification_service import NotificationService
from src.core.services.location_service import LocationService
from src.utils.logger import log_error, setup_logger
from datetime import datetime, timedelta
import string
import random

# Initialize logger
logger = setup_logger("order_service")

class OrderService(BaseService[Order]):
    """
    Service for managing orders with status flow
    """
    
    def __init__(self, db_session: Session):
        """
        Initialize the order service
        
        Args:
            db_session: SQLAlchemy database session
        """
        super().__init__(db_session, Order)
        self.notification_service = NotificationService(db_session)
        self.location_service = LocationService(db_session)
    
    def count_orders(self) -> int:
        """
        Count total number of orders
        
        Returns:
            Total number of orders
        """
        return self.db.query(func.count(Order.id)).scalar() or 0
    
    def create_order(self, user_id: int, items: List[Dict[str, Any]], 
                   shipping_address: Optional[str] = None,
                   notes: Optional[str] = None) -> BaseOrder:
        """Create a new order with items"""
        # Calculate total amount
        total_amount = 0.0
        order_items = []
        
        # Create order
        db_order = Order(
            user_id=user_id,
            status=OrderStatus.PENDING_PAYMENT,
            total_amount=total_amount,
            shipping_address=shipping_address,
            notes=notes,
            created_at=datetime.utcnow()
        )
        
        self.db.add(db_order)
        self.db.flush()  # Get order ID without committing transaction
        
        # Add order items
        for item_data in items:
            product_id = item_data.get("product_id")
            quantity = item_data.get("quantity", 1)
            
            # Get product details
            product = self.db.query(Product).filter(Product.id == product_id).first()
            if not product:
                continue
                
            # Create order item
            price = product.current_price
            item = OrderItem(
                order_id=db_order.id,
                product_id=product_id,
                quantity=quantity,
                price=price,
                created_at=datetime.utcnow()
            )
            
            order_items.append(item)
            total_amount += price * quantity
            
            # Update product stock
            product.stock -= quantity
        
        # Update order total
        db_order.total_amount = total_amount
        
        # Add all items
        self.db.add_all(order_items)
        
        # Commit transaction
        self.db.commit()
        self.db.refresh(db_order)
        
        return db_order.to_model()
    
    def update_order_status(self, order_id: int, status: str) -> Optional[BaseOrder]:
        """Update order status"""
        order = self.db.query(Order).filter(Order.id == order_id).first()
        if not order:
            return None
        
        try:
            new_status = OrderStatus(status)
            order.status = new_status
            
            self.db.commit()
            self.db.refresh(order)
            
            return order.to_model()
        except ValueError:
            # Invalid status
            return None
    
    def cancel_order(self, order_id: int) -> Optional[BaseOrder]:
        """Cancel an order and restore product stock"""
        order = self.db.query(Order).filter(Order.id == order_id).first()
        if not order:
            return None
        
        # Can only cancel pending orders
        if order.status not in [OrderStatus.PENDING_PAYMENT, OrderStatus.PAYMENT_SUBMITTED]:
            return None
        
        # Restore product stock
        for item in order.items:
            product = self.db.query(Product).filter(Product.id == item.product_id).first()
            if product:
                product.stock += item.quantity
        
        # Update order status
        order.status = OrderStatus.CANCELLED
        
        self.db.commit()
        self.db.refresh(order)
        
        return order.to_model()
    
    def get_order_items(self, order_id: int) -> List[BaseOrderItem]:
        """Get all items for a specific order"""
        items = self.db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
        return [item.to_model() for item in items]
    
    def get_order_by_id(self, order_id: int) -> Optional[BaseOrder]:
        """Get order by ID"""
        order = self.db.query(Order).filter(Order.id == order_id).first()
        if order:
            return order.to_model()
        return None
    
    def list_user_orders(self, user_id: int, skip: int = 0, limit: int = 20) -> List[BaseOrder]:
        """List orders for a specific user"""
        orders = self.db.query(Order).filter(Order.user_id == user_id)\
            .order_by(Order.created_at.desc())\
            .offset(skip).limit(limit).all()
        
        return [order.to_model() for order in orders]
    
    def submit_payment(self, order_id: int, payment_method: str, transaction_id: Optional[str] = None, 
                     transaction_data: Optional[Dict] = None) -> bool:
        """
        Submit payment for an order
        
        Args:
            order_id: Order ID
            payment_method: Payment method
            transaction_id: Transaction ID (optional)
            transaction_data: Transaction data (optional)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get order
            order = self.get_by_id(order_id)
            if not order or order.status != OrderStatus.PENDING_PAYMENT:
                logger.error(f"Cannot submit payment: Order {order_id} not found or not pending payment")
                return False
            
            # Create payment
            from src.core.services.payment_service import PaymentService
            payment_service = PaymentService(self.db)
            
            payment = payment_service.create_payment(
                user_id=order.buyer_id,
                amount=float(order.total_amount),
                payment_method=payment_method,
                payment_type=PaymentType.ORDER,
                order_id=order_id,
                transaction_id=transaction_id,
                transaction_data=transaction_data
            )
            
            if not payment:
                logger.error(f"Failed to create payment for order {order_id}")
                return False
            
            # Update order status
            order.status = OrderStatus.PAYMENT_SUBMITTED
            order.payment_method = payment_method
            order.payment_id = payment.id
            
            self.db.commit()
            logger.info(f"Payment submitted for order {order_id}")
            
            # Notify buyer
            self.notification_service.create_notification(
                user_id=order.buyer_id,
                title="Payment Submitted",
                message="Your payment has been submitted and is awaiting verification.",
                type="ORDER",
                order_id=order_id
            )
            
            # Notify cardholders about new payment to verify
            cardholders = self.db.query(User).filter(User.role == "CARDHOLDER").all()
            for cardholder in cardholders:
                self.notification_service.create_notification(
                    user_id=cardholder.id,
                    title="Payment Needs Verification",
                    message=f"Order {order_id} payment needs verification.",
                    type="ORDER",
                    order_id=order_id,
                    is_urgent=True
                )
            
            return True
        except Exception as e:
            self.db.rollback()
            log_error(f"Error submitting payment for order {order_id}", e)
            return False
    
    def payment_verified_by_cardholder(self, order_id: int) -> bool:
        """
        Update order status after payment verification by cardholder
        
        Args:
            order_id: Order ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get order
            order = self.get_by_id(order_id)
            if not order or order.status != OrderStatus.PAYMENT_SUBMITTED:
                logger.error(f"Cannot update order status: Order {order_id} not found or not in payment submitted status")
                return False
            
            # Update order status
            order.status = OrderStatus.CARDHOLDER_VERIFYING
            
            self.db.commit()
            logger.info(f"Order {order_id} payment verified by cardholder")
            
            # Notify buyer
            self.notification_service.create_notification(
                user_id=order.buyer_id,
                title="Payment Verified by Cardholder",
                message="Your payment has been verified by a cardholder and is awaiting admin verification.",
                type="ORDER",
                order_id=order_id
            )
            
            return True
        except Exception as e:
            self.db.rollback()
            log_error(f"Error updating order {order_id} status after cardholder verification", e)
            return False
    
    def payment_verified_by_admin(self, order_id: int) -> bool:
        """
        Update order status after payment verification by admin
        
        Args:
            order_id: Order ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get order
            order = self.get_by_id(order_id)
            if not order or order.status != OrderStatus.CARDHOLDER_VERIFYING:
                logger.error(f"Cannot update order status: Order {order_id} not found or not in cardholder verifying status")
                return False
            
            # Update order status
            order.status = OrderStatus.ADMIN_VERIFYING
            
            self.db.commit()
            logger.info(f"Order {order_id} payment verified by admin")
            
            # Notify buyer
            self.notification_service.create_notification(
                user_id=order.buyer_id,
                title="Payment Fully Verified",
                message="Your payment has been fully verified. Your order is now being processed.",
                type="ORDER",
                order_id=order_id
            )
            
            # Update to preparing delivery status
            self.prepare_for_delivery(order_id)
            
            return True
        except Exception as e:
            self.db.rollback()
            log_error(f"Error updating order {order_id} status after admin verification", e)
            return False
    
    def prepare_for_delivery(self, order_id: int) -> bool:
        """
        Prepare order for delivery by assigning location
        
        Args:
            order_id: Order ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get order
            order = self.get_by_id(order_id)
            if not order or order.status != OrderStatus.ADMIN_VERIFYING:
                logger.error(f"Cannot prepare for delivery: Order {order_id} not found or payment not fully verified")
                return False
            
            # Get product
            product = self.db.query(Product).filter(Product.id == order.product_id).first()
            if not product:
                logger.error(f"Product {order.product_id} not found for order {order_id}")
                return False
            
            # Get a random location based on product city and area
            pre_location = self.location_service.get_random_pre_location(product.city_id, product.area)
            if not pre_location:
                logger.error(f"No available locations found in city {product.city_id}, area {product.area}")
                return False
            
            # Create main location
            main_location = self.location_service.create_main_location(
                order_id=order_id,
                pre_location_id=pre_location.id
            )
            
            if not main_location:
                logger.error(f"Failed to create main location for order {order_id}")
                return False
            
            # Update order status
            order.status = OrderStatus.PREPARING_DELIVERY
            
            self.db.commit()
            logger.info(f"Order {order_id} prepared for delivery with location {pre_location.id}")
            
            # Notify seller about delivery location
            self.notification_service.create_notification(
                user_id=order.seller_id,
                title="Delivery Location Assigned",
                message=f"Please deliver order {order_id} to the assigned location: {pre_location.name}, {pre_location.address}. "
                        f"Remember to write the delivery code {order.delivery_code} on the package.",
                type="ORDER",
                order_id=order_id,
                is_urgent=True
            )
            
            # Update to awaiting dropoff
            order.status = OrderStatus.AWAITING_DROPOFF
            self.db.commit()
            
            return True
        except Exception as e:
            self.db.rollback()
            log_error(f"Error preparing order {order_id} for delivery", e)
            return False
    
    def mark_as_dropped(self, order_id: int, photo_url: str) -> bool:
        """
        Mark order as dropped at location
        
        Args:
            order_id: Order ID
            photo_url: Photo URL of dropped item
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get order
            order = self.get_by_id(order_id)
            if not order or order.status != OrderStatus.AWAITING_DROPOFF:
                logger.error(f"Cannot mark as dropped: Order {order_id} not found or not awaiting dropoff")
                return False
            
            # Get main location
            main_location = self.db.query(MainLocation).filter(MainLocation.order_id == order_id).first()
            if not main_location:
                logger.error(f"No main location found for order {order_id}")
                return False
            
            # Update main location with photo
            if not self.location_service.update_main_location_photo(main_location.id, photo_url):
                logger.error(f"Failed to update main location photo for order {order_id}")
                return False
            
            # Update order status
            order.status = OrderStatus.ITEM_DROPPED
            order.dropoff_time = datetime.utcnow()
            
            self.db.commit()
            logger.info(f"Order {order_id} marked as dropped at location")
            
            # Mark location as delivered
            self.location_service.mark_as_delivered(main_location.id)
            
            # Schedule notification to buyer after 15 minutes
            pickup_notification_time = datetime.utcnow() + timedelta(minutes=15)
            
            self.notification_service.create_notification(
                user_id=order.buyer_id,
                title="Your Order is Ready for Pickup",
                message=f"Your order is now ready for pickup at the designated location. Details and photo are available.",
                type="ORDER",
                order_id=order_id,
                is_urgent=True,
                deliver_at=pickup_notification_time
            )
            
            # Update to awaiting pickup
            order.status = OrderStatus.AWAITING_PICKUP
            self.db.commit()
            
            return True
        except Exception as e:
            self.db.rollback()
            log_error(f"Error marking order {order_id} as dropped", e)
            return False
    
    def confirm_delivery_code(self, order_id: int, delivery_code: str) -> bool:
        """
        Confirm delivery code for pickup
        
        Args:
            order_id: Order ID
            delivery_code: Delivery code entered by buyer
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get order
            order = self.get_by_id(order_id)
            if not order or order.status != OrderStatus.AWAITING_PICKUP:
                logger.error(f"Cannot confirm delivery code: Order {order_id} not found or not awaiting pickup")
                return False
            
            # Verify delivery code
            if order.delivery_code != delivery_code:
                logger.error(f"Invalid delivery code for order {order_id}")
                return False
            
            # Update order status
            order.status = OrderStatus.COMPLETED
            order.delivery_code_confirmed = True
            order.pickup_time = datetime.utcnow()
            
            # Get main location and mark as picked up
            main_location = self.db.query(MainLocation).filter(MainLocation.order_id == order_id).first()
            if main_location:
                self.location_service.mark_as_picked_up(main_location.id)
            
            # Update product stock
            product = self.db.query(Product).filter(Product.id == order.product_id).first()
            if product:
                product.stock -= order.quantity
            
            self.db.commit()
            logger.info(f"Order {order_id} completed with delivery code confirmation")
            
            # Notify buyer
            self.notification_service.create_notification(
                user_id=order.buyer_id,
                title="Order Completed",
                message="Your order has been completed. Thank you for your purchase!",
                type="ORDER",
                order_id=order_id
            )
            
            # Notify seller
            self.notification_service.create_notification(
                user_id=order.seller_id,
                title="Order Completed",
                message=f"Order {order_id} has been completed. The buyer has picked up the item.",
                type="ORDER",
                order_id=order_id
            )
            
            return True
        except Exception as e:
            self.db.rollback()
            log_error(f"Error confirming delivery code for order {order_id}", e)
            return False
    
    def get_buyer_orders(self, buyer_id: int, skip: int = 0, limit: int = 20) -> List[Order]:
        """
        Get a buyer's orders
        
        Args:
            buyer_id: Buyer user ID
            skip: Number of orders to skip
            limit: Maximum number of orders to return
            
        Returns:
            List of orders
        """
        try:
            return self.db.query(Order).filter(Order.buyer_id == buyer_id)\
                .order_by(desc(Order.created_at))\
                .offset(skip).limit(limit).all()
        except Exception as e:
            log_error(f"Error getting orders for buyer {buyer_id}", e)
            return []
    
    def get_seller_orders(self, seller_id: int, skip: int = 0, limit: int = 20) -> List[Order]:
        """
        Get a seller's orders
        
        Args:
            seller_id: Seller user ID
            skip: Number of orders to skip
            limit: Maximum number of orders to return
            
        Returns:
            List of orders
        """
        try:
            return self.db.query(Order).filter(Order.seller_id == seller_id)\
                .order_by(desc(Order.created_at))\
                .offset(skip).limit(limit).all()
        except Exception as e:
            log_error(f"Error getting orders for seller {seller_id}", e)
            return []
    
    def get_orders_by_status(self, status: OrderStatus, skip: int = 0, limit: int = 20) -> List[Order]:
        """
        Get orders by status
        
        Args:
            status: Order status
            skip: Number of orders to skip
            limit: Maximum number of orders to return
            
        Returns:
            List of orders
        """
        try:
            return self.db.query(Order).filter(Order.status == status)\
                .order_by(desc(Order.created_at))\
                .offset(skip).limit(limit).all()
        except Exception as e:
            log_error(f"Error getting orders with status {status}", e)
            return [] 