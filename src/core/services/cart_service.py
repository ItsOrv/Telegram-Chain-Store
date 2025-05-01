from sqlalchemy.orm import Session
from typing import List, Optional
from src.core.models.cart import CartItem
from src.core.models.product import Product
from src.core.services.base_service import BaseService
from src.utils.logger import setup_logger, log_error

# Initialize logger
logger = setup_logger("cart_service")

class CartService(BaseService):
    """Service for managing user cart items"""
    
    def __init__(self, session: Session):
        super().__init__(session)
        
    def get_cart_items(self, user_id: int) -> List[CartItem]:
        """Get all cart items for a user
        
        Args:
            user_id: User ID to get cart items for
            
        Returns:
            List of cart items
        """
        try:
            cart_items = self.session.query(CartItem).filter(
                CartItem.user_id == user_id
            ).all()
            return cart_items
        except Exception as e:
            log_error("Error getting cart items", e)
            return []
    
    def get_cart_item(self, user_id: int, product_id: int) -> Optional[CartItem]:
        """Get a specific cart item
        
        Args:
            user_id: User ID
            product_id: Product ID
            
        Returns:
            Cart item if found, otherwise None
        """
        try:
            cart_item = self.session.query(CartItem).filter(
                CartItem.user_id == user_id,
                CartItem.product_id == product_id
            ).first()
            return cart_item
        except Exception as e:
            log_error("Error getting cart item", e)
            return None
    
    def add_to_cart(self, user_id: int, product_id: int, quantity: int = 1) -> bool:
        """Add a product to the user's cart
        
        Args:
            user_id: User ID
            product_id: Product ID
            quantity: Quantity to add (default: 1)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if product exists and has sufficient stock
            product = self.session.query(Product).filter(Product.id == product_id).first()
            if not product:
                logger.warning(f"Product {product_id} not found")
                return False
                
            if product.stock < quantity:
                logger.warning(f"Insufficient stock for product {product_id}")
                return False
            
            # Check if item already in cart
            cart_item = self.get_cart_item(user_id, product_id)
            
            if cart_item:
                # Update quantity if already in cart
                cart_item.quantity += quantity
                if cart_item.quantity > product.stock:
                    cart_item.quantity = product.stock
            else:
                # Create new cart item
                cart_item = CartItem(
                    user_id=user_id,
                    product_id=product_id,
                    quantity=quantity
                )
                self.session.add(cart_item)
                
            self.session.commit()
            return True
        except Exception as e:
            log_error("Error adding item to cart", e)
            self.session.rollback()
            return False
    
    def remove_from_cart(self, user_id: int, product_id: int) -> bool:
        """Remove a product from the user's cart
        
        Args:
            user_id: User ID
            product_id: Product ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cart_item = self.get_cart_item(user_id, product_id)
            
            if not cart_item:
                logger.warning(f"Cart item not found for user {user_id} and product {product_id}")
                return False
                
            self.session.delete(cart_item)
            self.session.commit()
            return True
        except Exception as e:
            log_error("Error removing item from cart", e)
            self.session.rollback()
            return False
    
    def update_quantity(self, user_id: int, product_id: int, quantity: int) -> bool:
        """Update the quantity of a product in the cart
        
        Args:
            user_id: User ID
            product_id: Product ID
            quantity: New quantity
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cart_item = self.get_cart_item(user_id, product_id)
            
            if not cart_item:
                logger.warning(f"Cart item not found for user {user_id} and product {product_id}")
                return False
            
            if quantity <= 0:
                # Remove item if quantity is 0 or negative
                return self.remove_from_cart(user_id, product_id)
                
            # Check stock availability
            product = self.session.query(Product).filter(Product.id == product_id).first()
            if not product:
                logger.warning(f"Product {product_id} not found")
                return False
                
            if product.stock < quantity:
                quantity = product.stock
                logger.warning(f"Adjusted quantity to match available stock: {quantity}")
            
            cart_item.quantity = quantity
            self.session.commit()
            return True
        except Exception as e:
            log_error("Error updating cart item quantity", e)
            self.session.rollback()
            return False
    
    def clear_cart(self, user_id: int) -> bool:
        """Clear all items from a user's cart
        
        Args:
            user_id: User ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cart_items = self.get_cart_items(user_id)
            
            for item in cart_items:
                self.session.delete(item)
                
            self.session.commit()
            return True
        except Exception as e:
            log_error("Error clearing cart", e)
            self.session.rollback()
            return False
    
    def get_cart_total(self, user_id: int) -> float:
        """Calculate the total price of all items in the cart
        
        Args:
            user_id: User ID
            
        Returns:
            Total price of all items
        """
        try:
            cart_items = self.get_cart_items(user_id)
            total = sum(item.quantity * item.product.price for item in cart_items)
            return total
        except Exception as e:
            log_error("Error calculating cart total", e)
            return 0.0 