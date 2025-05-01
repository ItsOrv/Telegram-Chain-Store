from sqlalchemy.orm import Session
from typing import Optional

from src.core.services.user_service import UserService
from src.core.services.product_service import ProductService
from src.core.services.order_service import OrderService


class Repository:
    """
    Repository interface that provides access to all services.
    This is the main entry point for the application to interact with the data layer.
    """
    
    def __init__(self, db_session: Session):
        """
        Initialize repository with database session
        
        Args:
            db_session: SQLAlchemy database session
        """
        self.db = db_session
        self._user_service = None
        self._product_service = None
        self._order_service = None
    
    @property
    def user_service(self) -> UserService:
        """Get user service instance"""
        if self._user_service is None:
            self._user_service = UserService(self.db)
        return self._user_service
    
    @property
    def product_service(self) -> ProductService:
        """Get product service instance"""
        if self._product_service is None:
            self._product_service = ProductService(self.db)
        return self._product_service
    
    @property
    def order_service(self) -> OrderService:
        """Get order service instance"""
        if self._order_service is None:
            self._order_service = OrderService(self.db)
        return self._order_service
    
    def close(self):
        """Close database session"""
        self.db.close()


def get_repository(db_session: Session) -> Repository:
    """
    Get a repository instance with a database session
    
    Args:
        db_session: SQLAlchemy database session
        
    Returns:
        Repository instance
    """
    return Repository(db_session) 