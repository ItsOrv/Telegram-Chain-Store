from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass

@dataclass
class User:
    id: int
    telegram_id: int
    username: str
    first_name: str
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    role: str = 'user'
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    last_login: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    language: str = 'en'
    timezone: Optional[str] = None
    notification_preferences: Optional[dict] = None

@dataclass
class UserAddress:
    id: int
    user_id: int
    address_type: str  # shipping or billing
    street: str
    city: str
    state: Optional[str] = None
    country: str
    postal_code: str
    is_default: bool = False
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    phone: Optional[str] = None
    recipient_name: Optional[str] = None

@dataclass
class UserPayment:
    id: int
    user_id: int
    payment_method: str
    payment_details: dict
    is_default: bool = False
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    last_used: Optional[datetime] = None
    is_active: bool = True

@dataclass
class UserSession:
    id: int
    user_id: int
    session_token: str
    created_at: datetime = datetime.utcnow()
    expires_at: datetime
    last_activity: datetime = datetime.utcnow()
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    is_active: bool = True

@dataclass
class UserNotification:
    id: int
    user_id: int
    title: str
    message: str
    notification_type: str
    created_at: datetime = datetime.utcnow()
    read_at: Optional[datetime] = None
    is_read: bool = False
    data: Optional[dict] = None

@dataclass
class UserPreference:
    id: int
    user_id: int
    preference_key: str
    preference_value: str
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()

@dataclass
class UserActivity:
    id: int
    user_id: int
    activity_type: str
    description: str
    created_at: datetime = datetime.utcnow()
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    metadata: Optional[dict] = None

@dataclass
class UserVerification:
    id: int
    user_id: int
    verification_type: str  # email, phone, or document
    verification_code: str
    expires_at: datetime
    created_at: datetime = datetime.utcnow()
    verified_at: Optional[datetime] = None
    is_verified: bool = False
    attempts: int = 0
    last_attempt: Optional[datetime] = None 