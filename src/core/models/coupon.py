from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

@dataclass
class Coupon:
    id: int
    code: str
    type: str  # percentage, fixed
    value: float
    store_id: int
    description: Optional[str] = None
    start_date: datetime = datetime.utcnow()
    end_date: Optional[datetime] = None
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    usage_limit: Optional[int] = None
    minimum_spend: Optional[float] = None
    maximum_spend: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class CouponUsage:
    id: int
    coupon_id: int
    user_id: int
    order_id: int
    amount: float
    created_at: datetime = datetime.utcnow()
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class CouponRestriction:
    id: int
    coupon_id: int
    restriction_type: str  # product, category, user, etc.
    restriction_id: int
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class CouponCategory:
    id: int
    name: str
    description: Optional[str] = None
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class CouponRule:
    id: int
    coupon_id: int
    rule_type: str
    conditions: Dict[str, Any]
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class CouponBatch:
    id: int
    name: str
    prefix: str
    count: int
    length: int
    created_at: datetime = datetime.utcnow()
    expires_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class CouponHistory:
    id: int
    coupon_id: int
    action: str
    user_id: Optional[int] = None
    created_at: datetime = datetime.utcnow()
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class CouponReport:
    id: int
    coupon_id: int
    total_usage: int
    total_amount: float
    start_date: datetime
    end_date: datetime
    created_at: datetime = datetime.utcnow()
    metadata: Optional[Dict[str, Any]] = None 