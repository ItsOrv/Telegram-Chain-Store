from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

@dataclass
class Order:
    id: int
    user_id: int
    store_id: int
    status: str
    total_amount: float
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    shipping_address: Optional[Dict[str, Any]] = None
    billing_address: Optional[Dict[str, Any]] = None
    payment_method: Optional[str] = None
    payment_status: Optional[str] = None
    shipping_method: Optional[str] = None
    shipping_status: Optional[str] = None
    tracking_number: Optional[str] = None
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class OrderItem:
    id: int
    order_id: int
    product_id: int
    variant_id: Optional[int] = None
    quantity: int
    unit_price: float
    total_price: float
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    discount_amount: Optional[float] = None
    tax_amount: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class OrderPayment:
    id: int
    order_id: int
    amount: float
    payment_method: str
    status: str
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    transaction_id: Optional[str] = None
    payment_details: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class OrderShipment:
    id: int
    order_id: int
    carrier: str
    tracking_number: str
    status: str
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    shipping_address: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class OrderRefund:
    id: int
    order_id: int
    amount: float
    reason: str
    status: str
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    refunded_at: Optional[datetime] = None
    refund_method: Optional[str] = None
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class OrderNote:
    id: int
    order_id: int
    user_id: int
    note: str
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    is_internal: bool = True
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class OrderDiscount:
    id: int
    order_id: int
    code: str
    type: str  # percentage, fixed
    value: float
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    applied_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class OrderTax:
    id: int
    order_id: int
    name: str
    rate: float
    amount: float
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class OrderHistory:
    id: int
    order_id: int
    status: str
    created_at: datetime = datetime.utcnow()
    user_id: Optional[int] = None
    comment: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None 