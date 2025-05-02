from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, Boolean, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from src.core.models.base import Base

class TransactionType(enum.Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    PAYMENT = "payment"
    REFUND = "refund"
    BONUS = "bonus"
    FEE = "fee"
    TRANSFER = "transfer"
    OTHER = "other"

class TransactionStatus(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Wallet(Base):
    """Represents a user's wallet for financial transactions"""
    __tablename__ = 'wallets'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    balance = Column(Float, default=0.0, nullable=False)
    currency = Column(String(10), default="IRR", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="wallet")
    transactions = relationship("Transaction", back_populates="wallet", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Wallet(user_id={self.user_id}, balance={self.balance})>"

class Transaction(Base):
    """Represents a financial transaction in a user's wallet"""
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True)
    wallet_id = Column(Integer, ForeignKey('wallets.id', ondelete='CASCADE'), nullable=False)
    amount = Column(Float, nullable=False)
    type = Column(Enum(TransactionType), nullable=False)
    status = Column(Enum(TransactionStatus), default=TransactionStatus.COMPLETED, nullable=False)
    description = Column(Text, nullable=True)
    reference_id = Column(String(100), nullable=True)  # For payment ID, order ID, etc.
    related_user_id = Column(Integer, ForeignKey('users.id'), nullable=True)  # For transfers between users
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    wallet = relationship("Wallet", back_populates="transactions")
    related_user = relationship("User", foreign_keys=[related_user_id])
    
    def __repr__(self):
        return f"<Transaction(id={self.id}, wallet_id={self.wallet_id}, amount={self.amount}, type={self.type})>" 