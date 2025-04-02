from datetime import datetime
from typing import List, Dict, Any, Optional
from src.core.models import Order, OrderItem, User, Product
from src.core.exceptions import OrderError, ValidationError
from src.core.validators import Validators

class OrderManager:
    def create_order(self, order_data: Dict[str, Any]) -> Order:
        """Create a new order"""
        try:
            # Validate order data
            Validators.validate_order_data(order_data)
            
            # Get user
            user = User.get_by_id(order_data['user_id'])
            if not user:
                raise OrderError("User not found")
            
            # Create order
            order = Order(
                user_id=user.id,
                total_amount=order_data['total_amount'],
                status='pending',
                created_at=datetime.utcnow()
            )
            order.save()
            
            # Create order items
            for item in order_data['items']:
                product = Product.get_by_id(item['product_id'])
                if not product:
                    raise OrderError(f"Product not found: {item['product_id']}")
                
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=item['quantity'],
                    price=product.price
                )
                order_item.save()
            
            return order
        except Exception as e:
            raise OrderError(f"Failed to create order: {str(e)}")

    def get_order(self, order_id: int) -> Optional[Order]:
        """Get order by ID"""
        try:
            return Order.get_by_id(order_id)
        except Exception as e:
            raise OrderError(f"Failed to get order: {str(e)}")

    def update_order_status(self, order_id: int, status: str) -> Order:
        """Update order status"""
        try:
            order = self.get_order(order_id)
            if not order:
                raise OrderError("Order not found")
            
            valid_statuses = ['pending', 'paid', 'processing', 'shipped', 'delivered', 'cancelled']
            if status not in valid_statuses:
                raise ValidationError(f"Invalid status. Must be one of: {valid_statuses}")
            
            order.status = status
            order.updated_at = datetime.utcnow()
            order.save()
            
            return order
        except Exception as e:
            raise OrderError(f"Failed to update order status: {str(e)}")

    def get_user_orders(self, user_id: int) -> List[Order]:
        """Get all orders for a user"""
        try:
            return Order.get_by_user_id(user_id)
        except Exception as e:
            raise OrderError(f"Failed to get user orders: {str(e)}")

    def cancel_order(self, order_id: int) -> Order:
        """Cancel an order"""
        try:
            order = self.get_order(order_id)
            if not order:
                raise OrderError("Order not found")
            
            if order.status not in ['pending', 'paid']:
                raise OrderError("Order cannot be cancelled in current status")
            
            order.status = 'cancelled'
            order.updated_at = datetime.utcnow()
            order.save()
            
            return order
        except Exception as e:
            raise OrderError(f"Failed to cancel order: {str(e)}")

    def get_order_items(self, order_id: int) -> List[OrderItem]:
        """Get all items in an order"""
        try:
            return OrderItem.get_by_order_id(order_id)
        except Exception as e:
            raise OrderError(f"Failed to get order items: {str(e)}")

    def calculate_order_total(self, order_id: int) -> float:
        """Calculate total amount for an order"""
        try:
            items = self.get_order_items(order_id)
            return sum(item.price * item.quantity for item in items)
        except Exception as e:
            raise OrderError(f"Failed to calculate order total: {str(e)}")

    def validate_order(self, order_id: int) -> bool:
        """Validate order data and status"""
        try:
            order = self.get_order(order_id)
            if not order:
                return False
            
            items = self.get_order_items(order_id)
            if not items:
                return False
            
            calculated_total = self.calculate_order_total(order_id)
            if abs(calculated_total - order.total_amount) > 0.01:  # Allow small floating point differences
                return False
            
            return True
        except Exception:
            return False
