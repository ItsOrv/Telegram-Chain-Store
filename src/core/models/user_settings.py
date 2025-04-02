from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

@dataclass
class UserSettings:
    id: int
    user_id: int
    language: str = "en"
    timezone: str = "UTC"
    theme: str = "light"
    notifications_enabled: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    preferences: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class UserPreference:
    id: int
    user_id: int
    key: str
    value: Any
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class UserNotificationSettings:
    id: int
    user_id: int
    channel: str  # email, sms, push, etc.
    enabled: bool = True
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    preferences: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class UserPrivacySettings:
    id: int
    user_id: int
    profile_visibility: str = "public"
    show_online_status: bool = True
    show_activity_status: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    preferences: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class UserSecuritySettings:
    id: int
    user_id: int
    two_factor_enabled: bool = False
    login_notifications: bool = True
    suspicious_activity_alerts: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    preferences: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class UserDisplaySettings:
    id: int
    user_id: int
    date_format: str = "YYYY-MM-DD"
    time_format: str = "HH:mm:ss"
    number_format: str = "1,234.56"
    currency: str = "USD"
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    preferences: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class UserCommunicationSettings:
    id: int
    user_id: int
    marketing_emails: bool = True
    newsletter: bool = True
    product_updates: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    preferences: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class UserAccessibilitySettings:
    id: int
    user_id: int
    high_contrast: bool = False
    font_size: str = "medium"
    reduce_animations: bool = False
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    preferences: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class UserIntegrationSettings:
    id: int
    user_id: int
    provider: str
    enabled: bool = True
    credentials: Optional[Dict[str, Any]] = None
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    preferences: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None 