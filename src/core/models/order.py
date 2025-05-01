from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from sqlalchemy import Column, Integer, String, Enum, DECIMAL, DateTime, Text, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import text, func
import enum
from src.core.models.base import Base, Order as BaseOrder, OrderItem as BaseOrderItem

class OrderStatus(str, enum.Enum):
    """Order status enum for tracking the lifecycle of an order"""
    # Initial status
    PENDING_PAYMENT = "PENDING_PAYMENT"  # Created but awaiting payment
    
    # Payment verification stages
    PAYMENT_SUBMITTED = "PAYMENT_SUBMITTED"  # Buyer submitted payment
    CARDHOLDER_VERIFYING = "CARDHOLDER_VERIFYING"  # Cardholder is verifying payment
    ADMIN_VERIFYING = "ADMIN_VERIFYING"  # Admin is verifying payment
    
    # Delivery stages
    PREPARING_DELIVERY = "PREPARING_DELIVERY"  # Payment verified, preparing for delivery
    AWAITING_DROPOFF = "AWAITING_DROPOFF"  # Location assigned, waiting for seller to drop
    ITEM_DROPPED = "ITEM_DROPPED"  # Seller has dropped the item
    AWAITING_PICKUP = "AWAITING_PICKUP"  # Waiting for buyer to pick up
    
    # Final states
    COMPLETED = "COMPLETED"  # Successfully completed
    CANCELLED = "CANCELLED"  # Cancelled by buyer/seller
    REFUNDED = "REFUNDED"  # Refunded to buyer
    
    def __str__(self) -> str:
        return self.value

class Order(Base):
    """Order model for database operations"""
    
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    location_id = Column(Integer, ForeignKey('pre_locations.id'), nullable=True)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING_PAYMENT)
    total_amount = Column(Float, nullable=False)
    shipping_address = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payment = relationship("Payment", foreign_keys="Payment.order_id", back_populates="order", uselist=False)
    location = relationship("PreLocation", back_populates="orders")
    
    def to_model(self) -> BaseOrder:
        """Convert ORM model to dataclass model"""
        return BaseOrder(
            id=self.id,
            user_id=self.user_id,
            status=self.status.value if self.status else None,
            total_amount=self.total_amount,
            shipping_address=self.shipping_address,
            notes=self.notes,
            created_at=self.created_at,
            items=[item.to_model() for item in self.items] if self.items else []
        )
    
    @classmethod
    def from_model(cls, model: BaseOrder) -> "Order":
        """Create ORM model from dataclass model"""
        return cls(
            id=model.id,
            user_id=model.user_id,
            status=model.status,
            total_amount=model.total_amount,
            shipping_address=model.shipping_address,
            notes=model.notes,
            created_at=model.created_at
        )

class OrderItem(Base):
    """OrderItem model for database operations"""
    
    __tablename__ = 'order_items'
    
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")
    
    def to_model(self) -> BaseOrderItem:
        """Convert ORM model to dataclass model"""
        return BaseOrderItem(
            id=self.id,
            order_id=self.order_id,
            product_id=self.product_id,
            quantity=self.quantity,
            price=self.price,
            created_at=self.created_at
        )
    
    @classmethod
    def from_model(cls, model: BaseOrderItem) -> "OrderItem":
        """Create ORM model from dataclass model"""
        return cls(
            id=model.id,
            order_id=model.order_id,
            product_id=model.product_id,
            quantity=model.quantity,
            price=model.price,
            created_at=model.created_at
        )

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
    shipping_address: Dict[str, Any]
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
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