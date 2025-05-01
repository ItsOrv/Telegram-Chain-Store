from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import text
from src.core.models.base import Base

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
class CartItem(Base):
    """Cart item model for storing items in user's cart"""
    __tablename__ = "cart_items"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'), nullable=False, index=True)
    quantity = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime, nullable=False, 
                      server_default=text('CURRENT_TIMESTAMP'),
                      onupdate=text('CURRENT_TIMESTAMP'))
    
    # Relationships
    user = relationship("User", back_populates="cart_items")
    product = relationship("Product", back_populates="cart_items")
    
    def __repr__(self) -> str:
        return f"<CartItem(id={self.id}, user_id={self.user_id}, product_id={self.product_id})>"
    
    @property
    def subtotal(self) -> float:
        """Calculate subtotal for this cart item"""
        if not self.product:
            return 0
        return float(self.product.current_price) * self.quantity
    
    def to_dict(self) -> dict:
        """Convert cart item to dictionary for API responses"""
        return {
            "id": self.id,
            "product_id": self.product_id,
            "product_name": self.product.name if self.product else "Unknown Product",
            "quantity": self.quantity,
            "unit_price": float(self.product.current_price) if self.product else 0,
            "subtotal": self.subtotal,
            "product_image": self.product.main_image_url if self.product else "",
            "seller_id": self.product.seller_id if self.product else None,
            "seller_name": self.product.seller.display_name if self.product and self.product.seller else "Unknown Seller"
        }

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
    city: str
    state: str
    postal_code: str
    country: str
    address_line2: Optional[str] = None
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