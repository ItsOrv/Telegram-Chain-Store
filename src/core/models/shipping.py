from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass

@dataclass
class ShippingMethod:
    id: int
    name: str
    code: str
    description: Optional[str] = None
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    base_price: float = 0.0
    price_per_kg: Optional[float] = None
    min_weight: Optional[float] = None
    max_weight: Optional[float] = None
    estimated_days: Optional[str] = None
    supported_regions: Optional[List[str]] = None
    settings: Optional[dict] = None

@dataclass
class ShippingZone:
    id: int
    name: str
    country_code: str
    state_code: Optional[str] = None
    city: Optional[str] = None
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    description: Optional[str] = None
    shipping_methods: Optional[List[int]] = None
    settings: Optional[dict] = None

@dataclass
class ShippingRate:
    id: int
    shipping_method_id: int
    zone_id: int
    base_price: float
    price_per_kg: Optional[float] = None
    min_weight: Optional[float] = None
    max_weight: Optional[float] = None
    estimated_days: Optional[str] = None
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    description: Optional[str] = None
    conditions: Optional[dict] = None

@dataclass
class ShippingAddress:
    id: int
    user_id: int
    full_name: str
    address_line1: str
    city: str
    state: Optional[str] = None
    postal_code: str
    country: str
    phone: Optional[str] = None
    is_default: bool = False
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    address_line2: Optional[str] = None
    instructions: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

@dataclass
class ShippingPackage:
    id: int
    order_id: int
    shipping_method_id: int
    tracking_number: Optional[str] = None
    status: str = "pending"
    weight: Optional[float] = None
    dimensions: Optional[dict] = None
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    estimated_delivery: Optional[datetime] = None
    shipping_cost: float = 0.0
    insurance_amount: Optional[float] = None
    customs_info: Optional[dict] = None

@dataclass
class ShippingTracking:
    id: int
    package_id: int
    status: str
    location: Optional[str] = None
    timestamp: datetime = datetime.utcnow()
    description: Optional[str] = None
    tracking_number: Optional[str] = None
    carrier: Optional[str] = None
    metadata: Optional[dict] = None

@dataclass
class ShippingLabel:
    id: int
    package_id: int
    label_url: str
    tracking_number: str
    created_at: datetime = datetime.utcnow()
    expires_at: Optional[datetime] = None
    format: str = "pdf"
    size: Optional[str] = None
    metadata: Optional[dict] = None

@dataclass
class ShippingRestriction:
    id: int
    shipping_method_id: int
    restriction_type: str  # weight, size, value, etc.
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    description: Optional[str] = None
    conditions: Optional[dict] = None 