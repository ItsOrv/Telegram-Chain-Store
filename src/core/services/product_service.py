from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime

from src.core.models.product import Product, Category, ProductStatus
from src.core.models.base import BaseProduct, BaseCategory
from src.utils.logger import log_error, setup_logger

# Initialize logger
logger = setup_logger("product_service")

class ProductService:
    """Service for product-related operations"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def get_product_by_id(self, product_id: int) -> Optional[BaseProduct]:
        """Get product by ID"""
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if product:
            return product.to_model()
        return None
    
    def list_products(self, 
                     skip: int = 0, 
                     limit: int = 20, 
                     category_id: Optional[int] = None,
                     search: Optional[str] = None,
                     sort_by: str = "created_at",
                     sort_order: str = "desc") -> List[BaseProduct]:
        """List products with filtering and sorting"""
        query = self.db.query(Product).filter(Product.status == ProductStatus.ACTIVE)
        
        # Apply filters
        if category_id:
            query = query.filter(Product.category_id == category_id)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(Product.name.ilike(search_term) | 
                               Product.description.ilike(search_term))
        
        # Apply sorting
        if sort_order.lower() == "asc":
            query = query.order_by(getattr(Product, sort_by).asc())
        else:
            query = query.order_by(getattr(Product, sort_by).desc())
        
        # Apply pagination
        products = query.offset(skip).limit(limit).all()
        
        # Convert to base models
        return [p.to_model() for p in products]
    
    def create_product(self, product_data: Dict[str, Any]) -> BaseProduct:
        """Create a new product"""
        product_model = BaseProduct(**product_data)
        db_product = Product.from_model(product_model)
        
        self.db.add(db_product)
        self.db.commit()
        self.db.refresh(db_product)
        
        return db_product.to_model()
    
    def update_product(self, product_id: int, product_data: Dict[str, Any]) -> Optional[BaseProduct]:
        """Update an existing product"""
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return None
        
        for key, value in product_data.items():
            if hasattr(product, key):
                setattr(product, key, value)
        
        self.db.commit()
        self.db.refresh(product)
        
        return product.to_model()
    
    def delete_product(self, product_id: int) -> bool:
        """Soft delete a product"""
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return False
        
        product.status = ProductStatus.DELETED
        product.deleted_at = datetime.utcnow()
        self.db.commit()
        
        return True
    
    # Category methods
    
    def get_category_by_id(self, category_id: int) -> Optional[BaseCategory]:
        """Get category by ID"""
        category = self.db.query(Category).filter(Category.id == category_id).first()
        if category:
            return category.to_model()
        return None
    
    def list_categories(self, parent_id: Optional[int] = None) -> List[BaseCategory]:
        """List categories, optionally filtered by parent ID"""
        query = self.db.query(Category)
        
        if parent_id is not None:
            query = query.filter(Category.parent_id == parent_id)
        
        categories = query.all()
        return [c.to_model() for c in categories]
    
    def create_category(self, category_data: Dict[str, Any]) -> BaseCategory:
        """Create a new category"""
        category_model = BaseCategory(**category_data)
        db_category = Category.from_model(category_model)
        
        self.db.add(db_category)
        self.db.commit()
        self.db.refresh(db_category)
        
        return db_category.to_model()
    
    def update_category(self, category_id: int, category_data: Dict[str, Any]) -> Optional[BaseCategory]:
        """Update an existing category"""
        category = self.db.query(Category).filter(Category.id == category_id).first()
        if not category:
            return None
        
        for key, value in category_data.items():
            if hasattr(category, key):
                setattr(category, key, value)
        
        self.db.commit()
        self.db.refresh(category)
        
        return category.to_model()
    
    def delete_category(self, category_id: int) -> bool:
        """Delete a category"""
        category = self.db.query(Category).filter(Category.id == category_id).first()
        if not category:
            return False
        
        self.db.delete(category)
        self.db.commit()
        
        return True
    
    def get_products(self, skip: int = 0, limit: int = 5) -> List[Product]:
        """
        Get a list of products with pagination
        
        Args:
            skip: Number of products to skip (for pagination)
            limit: Maximum number of products to return
            
        Returns:
            List of products
        """
        try:
            products = self.db.query(Product).order_by(Product.created_at.desc()).offset(skip).limit(limit).all()
            return products
        except Exception as e:
            log_error("Error getting products list", e)
            return []
    
    def count_products(self) -> int:
        """
        Get total number of products
        
        Returns:
            Total count of products
        """
        try:
            return self.db.query(Product).count()
        except Exception as e:
            log_error("Error counting products", e)
            return 0 