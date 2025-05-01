"""
Core services for the application
"""

# Base service
from src.core.services.base_service import BaseService

# User service
from src.core.services.user_service import UserService

# Product service
from src.core.services.product_service import ProductService

# Order service
from src.core.services.order_service import OrderService

# Payment service
from src.core.services.payment_service import PaymentService

# Location service
from src.core.services.location_service import LocationService

# Notification service
from src.core.services.notification_service import NotificationService

# All services for easy import
__all__ = [
    'BaseService',
    'UserService',
    'ProductService',
    'OrderService',
    'PaymentService',
    'LocationService',
    'NotificationService'
]

# Factory function to get services with a database session
def get_services(db_session):
    """
    Create all services with the given database session
    
    Args:
        db_session: SQLAlchemy session
        
    Returns:
        Dictionary of services
    """
    return {
        'user_service': UserService(db_session),
        'product_service': ProductService(db_session),
        'order_service': OrderService(db_session),
        'payment_service': PaymentService(db_session),
        'location_service': LocationService(db_session),
        'notification_service': NotificationService(db_session)
    }
