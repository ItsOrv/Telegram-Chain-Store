from datetime import datetime
from typing import Optional
from dataclasses import dataclass

@dataclass
class SupportTicket:
    id: int
    user_id: int
    description: str
    status: str
    created_at: datetime
    updated_at: datetime
    assigned_to: Optional[int] = None
    priority: str = 'normal'
    category: Optional[str] = None
    resolution: Optional[str] = None
    closed_at: Optional[datetime] = None

@dataclass
class FAQ:
    id: int
    question: str
    answer: str
    created_at: datetime
    updated_at: datetime
    category: Optional[str] = None
    is_active: bool = True
    order: int = 0

@dataclass
class SupportCategory:
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()

@dataclass
class SupportAgent:
    id: int
    user_id: int
    name: str
    email: str
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    last_active: Optional[datetime] = None
    assigned_tickets: int = 0
    resolved_tickets: int = 0
    average_response_time: float = 0.0

@dataclass
class TicketComment:
    id: int
    ticket_id: int
    user_id: int
    content: str
    created_at: datetime
    updated_at: datetime
    is_internal: bool = False
    attachments: Optional[list] = None

@dataclass
class SupportSettings:
    id: int
    support_email: str
    support_phone: Optional[str] = None
    support_channel: Optional[str] = None
    support_group: Optional[str] = None
    business_hours: Optional[str] = None
    response_time: Optional[str] = None
    auto_reply_message: Optional[str] = None
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow() 