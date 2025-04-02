from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

@dataclass
class Cart:
    id: int
    user_id: Optional[int]
    session_id: str
    store_id: int
    status: str = "active"
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    expires_at: Optional[datetime] = None
    currency: str = "USD"
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class CartItem:
    id: int
    cart_id: int
    product_id: int
    variant_id: Optional[int] = None
    quantity: int
    unit_price: float
    total_price: float
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class CartDiscount:
    id: int
    cart_id: int
    code: str
    type: str  # percentage, fixed
    value: float
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    applied_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class CartTax:
    id: int
    cart_id: int
    name: str
    rate: float
    amount: float
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class CartShipping:
    id: int
    cart_id: int
    method: str
    cost: float
    estimated_days: Optional[int] = None
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class CartAddress:
    id: int
    cart_id: int
    type: str  # shipping, billing
    full_name: str
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    state: str
    postal_code: str
    country: str
    phone: Optional[str] = None
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class CartPaymentMethod:
    id: int
    cart_id: int
    method: str
    details: Dict[str, Any]
    is_default: bool = False
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class CartHistory:
    id: int
    cart_id: int
    action: str
    details: Dict[str, Any]
    created_at: datetime = datetime.utcnow()
    user_id: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class SavedCart:
    id: int
    user_id: int
    name: str
    cart_data: Dict[str, Any]
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    expires_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None 