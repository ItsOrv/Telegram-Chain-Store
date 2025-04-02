from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

@dataclass
class Discount:
    id: int
    name: str
    type: str  # percentage, fixed
    value: float
    store_id: int
    description: Optional[str] = None
    start_date: datetime = datetime.utcnow()
    end_date: Optional[datetime] = None
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    minimum_spend: Optional[float] = None
    maximum_spend: Optional[float] = None
    usage_limit: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class DiscountRule:
    id: int
    discount_id: int
    rule_type: str
    conditions: Dict[str, Any]
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class DiscountUsage:
    id: int
    discount_id: int
    user_id: int
    order_id: int
    amount: float
    created_at: datetime = datetime.utcnow()
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class DiscountProduct:
    id: int
    discount_id: int
    product_id: int
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class DiscountCategory:
    id: int
    discount_id: int
    category_id: int
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class DiscountCustomer:
    id: int
    discount_id: int
    customer_id: int
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class DiscountHistory:
    id: int
    discount_id: int
    action: str
    user_id: Optional[int] = None
    created_at: datetime = datetime.utcnow()
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class DiscountReport:
    id: int
    discount_id: int
    total_usage: int
    total_amount: float
    start_date: datetime
    end_date: datetime
    created_at: datetime = datetime.utcnow()
    metadata: Optional[Dict[str, Any]] = None 