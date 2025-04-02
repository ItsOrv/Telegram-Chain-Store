from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass

@dataclass
class Payment:
    id: int
    order_id: int
    user_id: int
    amount: float
    currency: str
    status: str
    payment_method: str
    created_at: datetime
    updated_at: datetime
    transaction_id: Optional[str] = None
    payment_details: Optional[dict] = None
    refund_amount: float = 0.0
    refund_status: Optional[str] = None
    refund_reason: Optional[str] = None
    refunded_at: Optional[datetime] = None
    error_message: Optional[str] = None
    metadata: Optional[dict] = None

@dataclass
class PaymentMethod:
    id: int
    name: str
    code: str
    description: Optional[str] = None
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    settings: Optional[dict] = None
    supported_currencies: Optional[List[str]] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    processing_fee: Optional[float] = None
    processing_time: Optional[str] = None

@dataclass
class PaymentTransaction:
    id: int
    payment_id: int
    transaction_type: str  # payment, refund, etc.
    amount: float
    currency: str
    status: str
    created_at: datetime
    updated_at: datetime
    transaction_id: Optional[str] = None
    payment_details: Optional[dict] = None
    error_message: Optional[str] = None
    metadata: Optional[dict] = None

@dataclass
class PaymentRefund:
    id: int
    payment_id: int
    amount: float
    reason: str
    status: str
    created_at: datetime
    updated_at: datetime
    processed_by: Optional[int] = None
    processed_at: Optional[datetime] = None
    transaction_id: Optional[str] = None
    refund_method: Optional[str] = None
    notes: Optional[str] = None

@dataclass
class PaymentGateway:
    id: int
    name: str
    code: str
    description: Optional[str] = None
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    settings: Optional[dict] = None
    supported_currencies: Optional[List[str]] = None
    supported_payment_methods: Optional[List[str]] = None
    webhook_url: Optional[str] = None
    test_mode: bool = False

@dataclass
class PaymentWebhook:
    id: int
    gateway_id: int
    event_type: str
    payload: dict
    status: str
    created_at: datetime = datetime.utcnow()
    processed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    response_code: Optional[int] = None
    response_body: Optional[str] = None

@dataclass
class PaymentFee:
    id: int
    payment_method_id: int
    fee_type: str  # percentage or fixed
    fee_value: float
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    is_active: bool = True
    description: Optional[str] = None

@dataclass
class PaymentLog:
    id: int
    payment_id: int
    event_type: str
    description: str
    created_at: datetime = datetime.utcnow()
    metadata: Optional[dict] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None 