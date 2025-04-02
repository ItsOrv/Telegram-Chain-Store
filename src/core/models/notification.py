from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass

@dataclass
class Notification:
    id: int
    user_id: int
    title: str
    message: str
    type: str  # order, payment, shipping, etc.
    status: str = "unread"
    created_at: datetime = datetime.utcnow()
    read_at: Optional[datetime] = None
    priority: str = "normal"  # low, normal, high
    data: Optional[dict] = None
    action_url: Optional[str] = None
    expires_at: Optional[datetime] = None

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