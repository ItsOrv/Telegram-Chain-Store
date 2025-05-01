from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from sqlalchemy import Column, Integer, String, DECIMAL, DateTime, Text, ForeignKey, Boolean, Enum, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import text, func
import enum
from src.core.models.base import Base, BaseModel, Product as BaseProduct, Category as BaseCategory

class ProductStatus(str, enum.Enum):
    """Product status enum"""
    ACTIVE = "ACTIVE"  # Available for purchase
    INACTIVE = "INACTIVE"  # Temporarily unavailable
    DELETED = "DELETED"  # Soft-deleted
    
    def __str__(self) -> str:
        return self.value

class Category(Base):
    """Product category model"""
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), nullable=False, unique=True)
    parent_id = Column(Integer, ForeignKey('categories.id', ondelete='SET NULL'), nullable=True)
    description = Column(Text, nullable=True)
    
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime, nullable=False, 
                      server_default=text('CURRENT_TIMESTAMP'),
                      onupdate=text('CURRENT_TIMESTAMP'))
    
    # Relationships
    products = relationship("Product", back_populates="category")
    subcategories = relationship("Category", 
                               back_populates="parent", 
                               remote_side=[id], 
                               cascade="all, delete-orphan",
                               single_parent=True)
    parent = relationship("Category", back_populates="subcategories", remote_side=[parent_id])
    
    def __repr__(self) -> str:
        return f"<Category(id={self.id}, name={self.name})>"

    def to_model(self) -> BaseCategory:
        """Convert ORM model to dataclass model"""
        return BaseCategory(
            id=self.id,
            name=self.name,
            description=self.description,
            parent_id=self.parent_id,
            created_at=self.created_at
        )
    
    @classmethod
    def from_model(cls, model: BaseCategory) -> "Category":
        """Create ORM model from dataclass model"""
        return cls(
            id=model.id,
            name=model.name,
            description=model.description,
            parent_id=model.parent_id,
            created_at=model.created_at
        )

class Product(Base):
    """Product model"""
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Ownership and classification
    seller_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey('categories.id', ondelete='RESTRICT'), nullable=False)
    city_id = Column(Integer, ForeignKey('cities.id', ondelete='RESTRICT'), nullable=False)
    
    # Basic product details
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    discount_price = Column(DECIMAL(18, 8), nullable=True)
    
    # Inventory details
    stock = Column(Integer, nullable=False, server_default=text('0'))
    min_order = Column(Integer, nullable=False, server_default=text('1'))
    max_order = Column(Integer, nullable=True)
    
    # Location and availability
    area = Column(String(100), nullable=False, comment='Specific area/zone within the city')
    status = Column(Enum(ProductStatus), nullable=False, server_default=ProductStatus.ACTIVE.value)
    is_available = Column(Boolean, default=True, nullable=False)
    
    # Additional fields
    views_count = Column(Integer, nullable=False, server_default=text('0'))
    weight = Column(DECIMAL(10, 2), nullable=True, comment='Product weight in kilograms')
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime, nullable=False, 
                      server_default=text('CURRENT_TIMESTAMP'),
                      onupdate=text('CURRENT_TIMESTAMP'))
    deleted_at = Column(DateTime, nullable=True)  # For soft delete
    
    # Relationships
    seller = relationship("User", back_populates="products")
    category = relationship("Category", back_populates="products")
    city = relationship("City", back_populates="products")
    order_items = relationship("OrderItem", back_populates="product")
    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="product")
    cart_items = relationship("CartItem", back_populates="product")
    
    def __repr__(self) -> str:
        return f"<Product(id={self.id}, name={self.name}, price={self.price})>"
    
    @property
    def current_price(self) -> float:
        """Get the current price (considering discount if available)"""
        return float(self.discount_price or self.price)
    
    @property
    def has_discount(self) -> bool:
        """Check if product has discount"""
        return self.discount_price is not None and self.discount_price < self.price
    
    @property
    def discount_percentage(self) -> float:
        """Get discount percentage"""
        if not self.has_discount:
            return 0
        return round((1 - (float(self.discount_price) / float(self.price))) * 100, 2)
    
    @property
    def is_in_stock(self) -> bool:
        """Check if product is in stock"""
        return self.stock > 0 and self.is_available and self.status == ProductStatus.ACTIVE
    
    @property
    def main_image_url(self) -> str:
        """Get URL of the main product image"""
        if self.images and len(self.images) > 0:
            return self.images[0].image_url
        return ""  # Default placeholder or empty string
    
    def to_dict(self) -> dict:
        """Convert product to dictionary for API responses"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": float(self.price),
            "current_price": self.current_price,
            "discount_price": float(self.discount_price) if self.discount_price else None,
            "discount_percentage": self.discount_percentage,
            "stock": self.stock,
            "seller_id": self.seller_id,
            "seller_name": self.seller.display_name,
            "category_id": self.category_id,
            "category_name": self.category.name,
            "city": self.city.name,
            "area": self.area,
            "status": self.status.value,
            "is_available": self.is_available,
            "is_in_stock": self.is_in_stock,
            "main_image_url": self.main_image_url,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

    def to_model(self) -> BaseProduct:
        """Convert ORM model to dataclass model"""
        return BaseProduct(
            id=self.id,
            name=self.name,
            description=self.description,
            price=self.price,
            image_url=self.main_image_url,
            category_id=self.category_id,
            stock_quantity=self.stock,
            created_at=self.created_at
        )
    
    @classmethod
    def from_model(cls, model: BaseProduct) -> "Product":
        """Create ORM model from dataclass model"""
        return cls(
            id=model.id,
            name=model.name,
            description=model.description,
            price=model.price,
            discount_price=model.discount_price,
            stock=model.stock_quantity,
            category_id=model.category_id,
            area=model.area,
            status=model.status,
            is_available=model.is_available,
            views_count=model.views_count,
            weight=model.weight,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
            seller_id=model.seller_id,
            city_id=model.city_id
        )

class ProductImage(Base):
    """Product image model"""
    __tablename__ = "product_images"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'), nullable=False, index=True)
    image_url = Column(String(500), nullable=False)
    display_order = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    
    # Relationships
    product = relationship("Product", back_populates="images")
    
    def __repr__(self) -> str:
        return f"<ProductImage(id={self.id}, product_id={self.product_id})>"

class Review(Base):
    """Product review model"""
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    rating = Column(Integer, nullable=False)  # 1-5 stars
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime, nullable=False, 
                      server_default=text('CURRENT_TIMESTAMP'),
                      onupdate=text('CURRENT_TIMESTAMP'))
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    product = relationship("Product", back_populates="reviews")
    user = relationship("User", backref="reviews")
    
    def __repr__(self) -> str:
        return f"<Review(id={self.id}, product_id={self.product_id}, rating={self.rating})>"

@dataclass
class ProductCategory:
    id: int
    name: str
    store_id: int
    description: Optional[str] = None
    parent_id: Optional[int] = None
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    image_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class ProductVariant:
    id: int
    product_id: int
    name: str
    sku: Optional[str] = None
    price: Optional[float] = None
    stock: int = 0
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    attributes: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class ProductAttribute:
    id: int
    name: str
    type: str
    description: Optional[str] = None
    is_required: bool = False
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    options: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class ProductReview:
    id: int
    product_id: int
    user_id: int
    rating: int
    comment: Optional[str] = None
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    is_verified: bool = False
    images: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class ProductPrice:
    id: int
    product_id: int
    price_type: str  # regular, sale, wholesale
    amount: float
    currency: str = "USD"
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class ProductInventory:
    id: int
    product_id: int
    warehouse_id: int
    quantity: int
    low_stock_threshold: Optional[int] = None
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    last_restock: Optional[datetime] = None
    next_restock: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class ProductTag:
    id: int
    name: str
    slug: str
    description: Optional[str] = None
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class ProductDiscount:
    id: int
    product_id: int
    type: str  # percentage, fixed
    value: float
    start_date: datetime
    end_date: datetime
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    conditions: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None 