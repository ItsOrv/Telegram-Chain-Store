from sqlalchemy import MetaData
from sqlalchemy.orm import declarative_base
from datetime import datetime
from typing import Optional, Dict, Any, List, ClassVar
from dataclasses import dataclass, field, asdict

# Define naming convention for constraints
metadata = MetaData(naming_convention={
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
})

# Create the base class for declarative models
Base = declarative_base(metadata=metadata)

# Create a non-dataclass base for common attributes
class ModelBase:
    """Base model methods"""
    # Class variable for table name
    table: ClassVar[str] = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {k: v for k, v in asdict(self).items() if v is not None}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create model from dictionary"""
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})

# Dataclass for common fields
@dataclass
class BaseModel(ModelBase):
    """Base model with common fields"""
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# User model dataclass for API operations
@dataclass
class BaseUser(ModelBase):
    """Base user model for API operations"""
    # Required fields first
    telegram_id: int
    first_name: str
    
    # Optional fields with default values
    last_name: Optional[str] = None
    username: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    role: str = "BUYER"  # Default role is buyer
    status: str = "ACTIVE"  # Default status is active
    balance: float = 0.0
    is_verified: bool = False
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    language: str = "en"
    timezone: Optional[str] = None
    
    def get_full_name(self) -> str:
        """Get user's full name"""
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name
    
    @property
    def is_admin(self) -> bool:
        """Backward compatibility property"""
        return self.role == "ADMIN"

# Set table name
BaseUser.table = "users"


# Category model
@dataclass
class Category(ModelBase):
    """Category model"""
    # Required fields
    name: str
    
    # Optional fields
    description: Optional[str] = None
    parent_id: Optional[int] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

# Set table name
Category.table = "categories"


# Product model
@dataclass
class Product(ModelBase):
    """Product model"""
    # Required fields
    name: str
    price: float
    
    # Optional fields
    category_id: Optional[int] = None
    seller_id: Optional[int] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    in_stock: bool = True
    stock_quantity: int = 0
    updated_at: Optional[datetime] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    
    # Advanced product details
    discount_price: Optional[float] = None
    area: Optional[str] = None
    status: Optional[str] = None
    is_available: bool = True
    views_count: int = 0
    weight: Optional[float] = None
    deleted_at: Optional[datetime] = None
    city_id: Optional[int] = None

# Set table name
Product.table = "products"


# Order model
@dataclass
class Order(ModelBase):
    """Order model"""
    # Required fields
    user_id: int
    
    # Optional fields
    status: str = "pending"
    total_amount: float = 0.0
    delivery_address: Optional[str] = None
    contact_phone: Optional[str] = None
    updated_at: Optional[datetime] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    items: List["OrderItem"] = field(default_factory=list)

# Set table name
Order.table = "orders"


# Order item model
@dataclass
class OrderItem(ModelBase):
    """Order item model"""
    # Required fields
    order_id: int
    product_id: int
    
    # Optional fields
    quantity: int = 1
    price: float = 0.0
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    
    def get_total(self) -> float:
        """Get total price for this item"""
        return self.price * self.quantity

# Set table name
OrderItem.table = "order_items"

# Aliases for backward compatibility
BaseProduct = Product
BaseCategory = Category
BaseOrder = Order
BaseOrderItem = OrderItem 