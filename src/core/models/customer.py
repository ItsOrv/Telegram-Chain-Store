from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

@dataclass
class Customer:
    id: int
    user_id: int
    store_id: int
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    last_login: Optional[datetime] = None
    last_order: Optional[datetime] = None
    total_orders: int = 0
    total_spent: float = 0.0
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class CustomerAddress:
    id: int
    customer_id: int
    type: str  # shipping, billing
    full_name: str
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    state: str
    postal_code: str
    country: str
    phone: Optional[str] = None
    is_default: bool = False
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class CustomerGroup:
    id: int
    name: str
    description: Optional[str] = None
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class CustomerGroupMembership:
    id: int
    customer_id: int
    group_id: int
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    expires_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class CustomerNote:
    id: int
    customer_id: int
    user_id: int
    note: str
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    is_internal: bool = True
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class CustomerPreference:
    id: int
    customer_id: int
    key: str
    value: Any
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class CustomerActivity:
    id: int
    customer_id: int
    activity_type: str
    description: str
    created_at: datetime = datetime.utcnow()
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class CustomerSegment:
    id: int
    name: str
    description: Optional[str] = None
    criteria: Dict[str, Any]
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class CustomerTag:
    id: int
    customer_id: int
    name: str
    created_at: datetime = datetime.utcnow()
    metadata: Optional[Dict[str, Any]] = None 