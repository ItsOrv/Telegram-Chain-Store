from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass
from sqlalchemy import Column, Integer, String, Enum, DECIMAL, DateTime, Boolean, BigInteger, ForeignKey, Table, func, Float, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import text
import enum
from src.core.models.base import Base, metadata, BaseUser

# Define role enum
class UserRole(str, enum.Enum):
    """User roles within the system"""
    ADMIN = "ADMIN"          # Can manage the entire system
    SELLER = "SELLER"        # Can sell products
    BUYER = "BUYER"          # Can purchase products
    CARDHOLDER = "CARDHOLDER"  # Can verify payments
    
    def __str__(self) -> str:
        return self.value

# Define user status enum
class UserStatus(str, enum.Enum):
    """User status within the system"""
    ACTIVE = "ACTIVE"        # User is active
    BANNED = "BANNED"        # User is banned from the system
    SUSPENDED = "SUSPENDED"  # User is temporarily suspended
    PENDING = "PENDING"      # User is pending approval
    
    def __str__(self) -> str:
        return self.value

# Define user-city association table
UserCity = Table(
    'user_cities',
    metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('city_id', Integer, ForeignKey('cities.id', ondelete='CASCADE'), primary_key=True),
    Column('created_at', DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
)

# We'll use SQLAlchemy models instead of dataclasses for database entities
class User(Base):
    """User model for database operations"""
    
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=True)
    username = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    email = Column(String, nullable=True)
    role = Column(Enum(UserRole), default=UserRole.BUYER, nullable=False)
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE, nullable=False)
    balance = Column(Float, default=0.0, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    language = Column(String(10), default='en', nullable=False)
    timezone = Column(String(50), nullable=True)
    notification_preferences = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    last_login = Column(DateTime, nullable=True)
    last_activity = Column(DateTime, nullable=True)
    
    # Relationships
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    products = relationship("Product", back_populates="seller", cascade="all, delete-orphan")
    payments = relationship("Payment", foreign_keys="Payment.user_id", back_populates="user")
    cities = relationship("City", secondary="user_cities", back_populates="users")
    notifications = relationship("Notification", back_populates="user")
    user_notifications = relationship("UserNotification", back_populates="user")
    cart_items = relationship("CartItem", back_populates="user")
    # Add other relationships as needed
    
    def to_model(self) -> BaseUser:
        """Convert ORM model to dataclass model"""
        return BaseUser(
            id=self.id,
            telegram_id=self.telegram_id,
            first_name=self.first_name,
            last_name=self.last_name,
            username=self.username,
            phone_number=self.phone_number,
            is_admin=self.is_admin,
            created_at=self.created_at
        )
    
    @classmethod
    def from_model(cls, model: BaseUser) -> "User":
        """Create ORM model from dataclass model"""
        return cls(
            id=model.id,
            telegram_id=model.telegram_id,
            first_name=model.first_name,
            last_name=model.last_name,
            username=model.username,
            phone_number=model.phone_number,
            role=UserRole.ADMIN if model.is_admin else UserRole.BUYER,
            created_at=model.created_at
        )
    
    def get_full_name(self) -> str:
        """Get user's full name"""
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name

    @property
    def is_admin(self) -> bool:
        """Check if user is an admin"""
        return self.role == UserRole.ADMIN
        
    @property
    def is_seller(self) -> bool:
        """Check if user is a seller"""
        return self.role == UserRole.SELLER
        
    @property
    def is_buyer(self) -> bool:
        """Check if user is a buyer"""
        return self.role == UserRole.BUYER
        
    @property
    def is_cardholder(self) -> bool:
        """Check if user is a cardholder"""
        return self.role == UserRole.CARDHOLDER
        
    @property
    def is_active(self) -> bool:
        """Check if user is active"""
        return self.status == UserStatus.ACTIVE
        
    @property
    def display_name(self) -> str:
        """Get user's display name"""
        return self.username or f"User {self.id}"
        
    def can_buy(self) -> bool:
        """Check if user can buy products"""
        return self.is_active and (self.is_buyer or self.is_admin)
        
    def can_sell(self) -> bool:
        """Check if user can sell products"""
        return self.is_active and (self.is_seller or self.is_admin)
        
    def can_verify_payments(self) -> bool:
        """Check if user can verify payments"""
        return self.is_active and (self.is_cardholder or self.is_admin)
        
    def can_approve_payments(self) -> bool:
        """Check if user can approve payments"""
        return self.is_active and self.is_admin

# Create related models using SQLAlchemy for consistency
class UserAddress(Base):
    """User address model"""
    __tablename__ = 'user_addresses'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    address_type = Column(String(20), nullable=False)  # shipping or billing
    street = Column(String, nullable=False)
    city = Column(String, nullable=False)
    country = Column(String, nullable=False)
    postal_code = Column(String, nullable=False)
    state = Column(String, nullable=True)
    is_default = Column(Boolean, default=False, nullable=False)
    phone = Column(String, nullable=True)
    recipient_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationship
    user = relationship("User", backref="addresses")

class UserPayment(Base):
    """User payment method model"""
    __tablename__ = 'user_payments'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    payment_method = Column(String, nullable=False)
    payment_details = Column(JSON, nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    last_used = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationship
    user = relationship("User", backref="payment_methods")

class UserNotification(Base):
    """User notification model"""
    __tablename__ = 'user_notifications'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    read_at = Column(DateTime, nullable=True)
    
    # Relationship
    user = relationship("User", back_populates="user_notifications")

class UserActivity(Base):
    """User activity model"""
    __tablename__ = 'user_activities'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    activity_type = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    activity_data = Column(JSON, nullable=True)  # Renamed from metadata to activity_data
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationship
    user = relationship("User", backref="activities") 