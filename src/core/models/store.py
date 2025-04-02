from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

@dataclass
class Store:
    id: int
    name: str
    description: Optional[str] = None
    owner_id: int
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    logo_url: Optional[str] = None
    banner_url: Optional[str] = None
    contact_info: Optional[Dict[str, Any]] = None
    settings: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class StoreSettings:
    id: int
    store_id: int
    currency: str = "USD"
    language: str = "en"
    timezone: str = "UTC"
    tax_rate: float = 0.0
    shipping_enabled: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    preferences: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class StoreLocation:
    id: int
    store_id: int
    name: str
    address: str
    city: str
    state: str
    country: str
    postal_code: str
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    contact_info: Optional[Dict[str, Any]] = None
    coordinates: Optional[Dict[str, float]] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class StoreHours:
    id: int
    store_id: int
    day_of_week: int
    open_time: str
    close_time: str
    is_closed: bool = False
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    special_hours: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class StoreStaff:
    id: int
    store_id: int
    user_id: int
    role: str
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    permissions: Optional[List[str]] = None
    schedule: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class StoreInventory:
    id: int
    store_id: int
    product_id: int
    quantity: int
    low_stock_threshold: Optional[int] = None
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    last_restock: Optional[datetime] = None
    next_restock: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class StorePromotion:
    id: int
    store_id: int
    name: str
    description: Optional[str] = None
    type: str
    value: float
    start_date: datetime
    end_date: datetime
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    conditions: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class StoreAnalytics:
    id: int
    store_id: int
    metric_type: str
    value: float
    timestamp: datetime = datetime.utcnow()
    dimensions: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class StoreReview:
    id: int
    store_id: int
    user_id: int
    rating: int
    comment: Optional[str] = None
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    is_verified: bool = False
    response: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None 