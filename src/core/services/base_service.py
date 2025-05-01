from typing import Any, Dict, List, Optional, Type, TypeVar, Generic
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from src.core.models.base import Base
from src.utils.logger import setup_logger, log_error

# Define a generic type for models
ModelType = TypeVar("ModelType", bound=Base)

# Initialize logger
logger = setup_logger("services")

class BaseService(Generic[ModelType]):
    """
    Base class for all services, providing common CRUD operations
    """
    
    def __init__(self, db_session: Session, model_class: Type[ModelType]):
        """
        Initialize the service
        
        Args:
            db_session: SQLAlchemy database session
            model_class: SQLAlchemy model class
        """
        self.db = db_session
        self.model = model_class
    
    def get_by_id(self, id: int) -> Optional[ModelType]:
        """
        Get an item by ID
        
        Args:
            id: Item ID
            
        Returns:
            Item if found, None otherwise
        """
        try:
            return self.db.query(self.model).filter(self.model.id == id).first()
        except SQLAlchemyError as e:
            log_error(f"Error getting {self.model.__name__} by ID {id}", e)
            return None
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """
        Get all items with pagination
        
        Args:
            skip: Number of items to skip
            limit: Maximum number of items to return
            
        Returns:
            List of items
        """
        try:
            return self.db.query(self.model).offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            log_error(f"Error getting all {self.model.__name__}s", e)
            return []
    
    def create(self, data: Dict[str, Any]) -> Optional[ModelType]:
        """
        Create a new item
        
        Args:
            data: Item data
            
        Returns:
            Created item if successful, None otherwise
        """
        try:
            item = self.model(**data)
            self.db.add(item)
            self.db.commit()
            self.db.refresh(item)
            return item
        except SQLAlchemyError as e:
            self.db.rollback()
            log_error(f"Error creating {self.model.__name__}", e)
            return None
    
    def update(self, id: int, data: Dict[str, Any]) -> Optional[ModelType]:
        """
        Update an existing item
        
        Args:
            id: Item ID
            data: Updated item data
            
        Returns:
            Updated item if successful, None otherwise
        """
        try:
            item = self.get_by_id(id)
            if not item:
                return None
                
            for key, value in data.items():
                if hasattr(item, key):
                    setattr(item, key, value)
            
            self.db.commit()
            self.db.refresh(item)
            return item
        except SQLAlchemyError as e:
            self.db.rollback()
            log_error(f"Error updating {self.model.__name__} with ID {id}", e)
            return None
    
    def delete(self, id: int) -> bool:
        """
        Delete an item
        
        Args:
            id: Item ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            item = self.get_by_id(id)
            if not item:
                return False
                
            self.db.delete(item)
            self.db.commit()
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            log_error(f"Error deleting {self.model.__name__} with ID {id}", e)
            return False
    
    def soft_delete(self, id: int) -> bool:
        """
        Soft delete an item (if supported)
        
        Args:
            id: Item ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            item = self.get_by_id(id)
            if not item or not hasattr(item, 'deleted_at'):
                return False
                
            from datetime import datetime
            item.deleted_at = datetime.utcnow()
            
            self.db.commit()
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            log_error(f"Error soft deleting {self.model.__name__} with ID {id}", e)
            return False
    
    def count(self) -> int:
        """
        Count total items
        
        Returns:
            Total count of items
        """
        try:
            return self.db.query(self.model).count()
        except SQLAlchemyError as e:
            log_error(f"Error counting {self.model.__name__}s", e)
            return 0 