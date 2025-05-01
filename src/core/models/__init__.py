"""
Core data models for the application
"""

# Base models
from src.core.models.base import Base, metadata, BaseModel, ModelBase

# User models
from src.core.models.user import (
    User, 
    UserRole, 
    UserStatus, 
    BaseUser, 
    UserAddress, 
    UserPayment, 
    UserNotification,
    UserActivity
)

# Product models
from src.core.models.product import (
    Product,
    Category,
    ProductImage,
    Review
)

# Order models
from src.core.models.order import (
    Order,
    OrderItem,
    OrderStatus
)

# Payment models
from src.core.models.payment import (
    Payment,
    PaymentMethod,
    PaymentStatus,
    Transaction
)

# Location models
from src.core.models.location import (
    PreLocation,
    MainLocation,
    City,
    Province,
    LocationStatus
)

# Cart models
from src.core.models.cart import (
    CartItem,
    Cart,
    CartDiscount,
    CartTax,
    CartShipping,
    CartAddress,
    CartPaymentMethod,
    CartHistory,
    SavedCart
)

# Notification models
from src.core.models.notification import (
    Notification,
    NotificationType
)

# All models for database creation
__all__ = [
    # Base
    'Base', 'metadata', 'BaseModel', 'ModelBase',
    
    # User
    'User', 'UserRole', 'UserStatus', 'BaseUser', 
    'UserAddress', 'UserPayment', 'UserNotification', 'UserActivity',
    
    # Product
    'Product', 'Category', 'ProductImage', 'Review',
    
    # Order
    'Order', 'OrderItem', 'OrderStatus',
    
    # Payment
    'Payment', 'PaymentMethod', 'PaymentStatus', 'Transaction',
    
    # Location
    'PreLocation', 'MainLocation', 'City', 'Province', 'LocationStatus',
    
    # Cart
    'CartItem', 'Cart', 'CartDiscount', 'CartTax', 'CartShipping',
    'CartAddress', 'CartPaymentMethod', 'CartHistory', 'SavedCart',
    
    # Notification
    'Notification', 'NotificationType'
]
