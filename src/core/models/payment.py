from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass
from sqlalchemy import Column, Integer, String, Enum, DECIMAL, DateTime, Boolean, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import text
import enum
from src.core.models.base import Base

class PaymentStatus(str, enum.Enum):
    """Payment status enum for tracking verification process"""
    PENDING = "PENDING"  # Initial state, awaiting verification
    CARDHOLDER_VERIFIED = "CARDHOLDER_VERIFIED"  # Verified by cardholder
    ADMIN_VERIFIED = "ADMIN_VERIFIED"  # Verified by admin, final verification
    COMPLETED = "COMPLETED"  # Successfully processed
    FAILED = "FAILED"  # Failed to process
    REFUNDED = "REFUNDED"  # Refunded to user
    
    def __str__(self) -> str:
        return self.value

class PaymentMethod(str, enum.Enum):
    """Payment method types"""
    WALLET = "WALLET"  # Internal wallet
    CRYPTO = "CRYPTO"  # Cryptocurrency
    CARD = "CARD"  # Bank card
    CASH = "CASH"  # Cash deposit
    
    def __str__(self) -> str:
        return self.value

class PaymentType(str, enum.Enum):
    """Payment type - what this payment is for"""
    ORDER = "ORDER"  # Payment for an order
    WALLET_CHARGE = "WALLET_CHARGE"  # Adding funds to wallet
    
    def __str__(self) -> str:
        return self.value

class TransactionType(str, enum.Enum):
    """Transaction types"""
    PAYMENT = "PAYMENT"       # Payment from user
    REFUND = "REFUND"         # Refund to user
    DEPOSIT = "DEPOSIT"       # Deposit to wallet
    WITHDRAWAL = "WITHDRAWAL" # Withdrawal from wallet
    TRANSFER = "TRANSFER"     # Transfer between users
    FEE = "FEE"               # Transaction fee
    
    def __str__(self) -> str:
        return self.value

class Transaction(Base):
    """Transaction model for tracking money movements"""
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # References
    user_id = Column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), nullable=False, index=True)
    payment_id = Column(Integer, ForeignKey('payments.id', ondelete='SET NULL'), nullable=True, index=True)
    
    # Transaction details
    amount = Column(Float, nullable=False)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    description = Column(Text, nullable=True)
    reference_id = Column(String(255), nullable=True, index=True)
    external_id = Column(String(255), nullable=True, index=True)
    
    # Status
    status = Column(String(50), nullable=False, default="COMPLETED")
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime, nullable=False, 
                      server_default=text('CURRENT_TIMESTAMP'),
                      onupdate=text('CURRENT_TIMESTAMP'))
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    payment = relationship("Payment", foreign_keys=[payment_id], back_populates="transactions")
    
    def __repr__(self) -> str:
        return f"<Transaction(id={self.id}, amount={self.amount}, type={self.transaction_type})>"

class Payment(Base):
    """Payment model for tracking transactions"""
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # User and order references (nullable for wallet charges)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), nullable=False, index=True)
    order_id = Column(Integer, ForeignKey('orders.id', ondelete='RESTRICT'), nullable=True, index=True)
    
    # Payment details
    amount = Column(DECIMAL(18, 8), nullable=False)
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    payment_type = Column(Enum(PaymentType), nullable=False, server_default=PaymentType.ORDER.value)
    status = Column(Enum(PaymentStatus), nullable=False, server_default=PaymentStatus.PENDING.value)
    
    # Transaction details
    transaction_id = Column(String(255), unique=True, nullable=True)
    transaction_data = Column(Text, nullable=True, comment="JSON data with payment provider response")
    
    # Verification tracking
    cardholder_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    cardholder_verified_at = Column(DateTime, nullable=True)
    cardholder_notes = Column(Text, nullable=True)
    
    admin_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    admin_verified_at = Column(DateTime, nullable=True)
    admin_notes = Column(Text, nullable=True)
    
    # Receipt data
    receipt_url = Column(String(500), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime, nullable=False, 
                      server_default=text('CURRENT_TIMESTAMP'),
                      onupdate=text('CURRENT_TIMESTAMP'))
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="payments")
    order = relationship("Order", foreign_keys=[order_id], back_populates="payment")
    cardholder = relationship("User", foreign_keys=[cardholder_id])
    admin = relationship("User", foreign_keys=[admin_id])
    transactions = relationship("Transaction", back_populates="payment")
    
    def __repr__(self) -> str:
        return f"<Payment(id={self.id}, amount={self.amount}, status={self.status})>"
    
    @property
    def is_pending(self) -> bool:
        """Check if payment is pending verification"""
        return self.status == PaymentStatus.PENDING
    
    @property
    def is_cardholder_verified(self) -> bool:
        """Check if payment is verified by cardholder"""
        return self.status == PaymentStatus.CARDHOLDER_VERIFIED
    
    @property
    def is_admin_verified(self) -> bool:
        """Check if payment is verified by admin"""
        return self.status == PaymentStatus.ADMIN_VERIFIED
    
    @property
    def is_completed(self) -> bool:
        """Check if payment is completed"""
        return self.status == PaymentStatus.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """Check if payment failed"""
        return self.status == PaymentStatus.FAILED
    
    @property
    def is_refunded(self) -> bool:
        """Check if payment is refunded"""
        return self.status == PaymentStatus.REFUNDED
    
    @property
    def needs_cardholder_verification(self) -> bool:
        """Check if payment needs cardholder verification"""
        return self.status == PaymentStatus.PENDING
    
    @property
    def needs_admin_verification(self) -> bool:
        """Check if payment needs admin verification"""
        return self.status == PaymentStatus.CARDHOLDER_VERIFIED
    
    @property
    def is_fully_verified(self) -> bool:
        """Check if payment is fully verified"""
        return self.status in [PaymentStatus.ADMIN_VERIFIED, PaymentStatus.COMPLETED]

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