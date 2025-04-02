from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

@dataclass
class Product:
    id: int
    name: str
    description: str
    price: float
    store_id: int
    category_id: Optional[int] = None
    sku: Optional[str] = None
    barcode: Optional[str] = None
    weight: Optional[float] = None
    dimensions: Optional[Dict[str, float]] = None
    is_active: bool = True
    is_featured: bool = False
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class ProductCategory:
    id: int
    name: str
    description: Optional[str] = None
    parent_id: Optional[int] = None
    store_id: int
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
class ProductImage:
    id: int
    product_id: int
    url: str
    alt_text: Optional[str] = None
    position: int = 0
    is_primary: bool = False
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
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