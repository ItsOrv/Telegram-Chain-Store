from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import text
import enum
from src.core.models.base import Base

class NotificationType(str, enum.Enum):
    """Notification type enum"""
    ORDER = "ORDER"  # Order-related notifications
    PAYMENT = "PAYMENT"  # Payment-related notifications
    DELIVERY = "DELIVERY"  # Delivery-related notifications
    SYSTEM = "SYSTEM"  # System-related notifications
    
    def __str__(self) -> str:
        return self.value

class Notification(Base):
    """Notification model for system notifications"""
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Notification content
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(50), nullable=False, server_default=NotificationType.SYSTEM.value)
    
    # Related entities
    order_id = Column(Integer, ForeignKey('orders.id', ondelete='SET NULL'), nullable=True)
    payment_id = Column(Integer, ForeignKey('payments.id', ondelete='SET NULL'), nullable=True)
    
    # Additional data as JSON
    data = Column(JSON, nullable=True)
    
    # Status flags
    is_read = Column(Boolean, nullable=False, server_default=text('0'))
    is_urgent = Column(Boolean, nullable=False, server_default=text('0'))
    
    # Schedule delivery time (for delayed notifications)
    deliver_at = Column(DateTime, nullable=True)
    
    # Tracking
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    read_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    order = relationship("Order", foreign_keys=[order_id])
    payment = relationship("Payment", foreign_keys=[payment_id])
    
    def __repr__(self) -> str:
        return f"<Notification(id={self.id}, user_id={self.user_id}, type={self.type})>"
    
    @property
    def is_delivered(self) -> bool:
        """Check if notification is ready to be delivered"""
        if self.deliver_at is None:
            return True
        return datetime.utcnow() >= self.deliver_at
    
    def mark_as_read(self) -> None:
        """Mark notification as read"""
        self.is_read = True
        self.read_at = datetime.utcnow()
    
    def to_dict(self) -> dict:
        """Convert notification to dictionary for API responses"""
        return {
            "id": self.id,
            "title": self.title,
            "message": self.message,
            "type": self.type,
            "is_read": self.is_read,
            "is_urgent": self.is_urgent,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "read_at": self.read_at.isoformat() if self.read_at else None,
            "data": self.data
        }

@dataclass
class NotificationTemplate:
    id: int
    name: str
    code: str
    title_template: str
    message_template: str
    type: str
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    description: Optional[str] = None
    variables: Optional[List[str]] = None
    default_priority: str = "normal"
    default_expiry_days: Optional[int] = None

@dataclass
class NotificationChannel:
    id: int
    name: str
    code: str  # email, sms, telegram, etc.
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    description: Optional[str] = None
    settings: Optional[dict] = None
    supported_templates: Optional[List[str]] = None
    rate_limit: Optional[int] = None
    rate_limit_period: Optional[str] = None

@dataclass
class NotificationPreference:
    id: int
    user_id: int
    channel_id: int
    notification_type: str
    is_enabled: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None
    priority_level: str = "normal"
    custom_settings: Optional[dict] = None

@dataclass
class NotificationLog:
    id: int
    notification_id: int
    channel_id: int
    status: str
    created_at: datetime = datetime.utcnow()
    sent_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    metadata: Optional[dict] = None
    response_code: Optional[int] = None
    response_body: Optional[str] = None

@dataclass
class NotificationGroup:
    id: int
    name: str
    description: Optional[str] = None
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    notification_types: Optional[List[str]] = None
    priority: str = "normal"
    settings: Optional[dict] = None

@dataclass
class NotificationSchedule:
    id: int
    template_id: int
    schedule_type: str  # one-time, recurring, etc.
    schedule_data: dict
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    last_run_at: Optional[datetime] = None
    next_run_at: Optional[datetime] = None
    target_users: Optional[List[int]] = None
    conditions: Optional[dict] = None

@dataclass
class NotificationBlacklist:
    id: int
    user_id: int
    channel_id: int
    reason: str
    created_at: datetime = datetime.utcnow()
    expires_at: Optional[datetime] = None
    is_permanent: bool = False
    notes: Optional[str] = None 