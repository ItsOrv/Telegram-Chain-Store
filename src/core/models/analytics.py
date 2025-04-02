from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

@dataclass
class AnalyticsEvent:
    id: int
    event_type: str
    user_id: Optional[int]
    session_id: Optional[str]
    created_at: datetime = datetime.utcnow()
    properties: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class AnalyticsSession:
    id: int
    session_id: str
    user_id: Optional[int]
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    device_type: Optional[str] = None
    platform: Optional[str] = None
    browser: Optional[str] = None
    location: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class AnalyticsMetric:
    id: int
    name: str
    value: float
    type: str  # count, average, sum, etc.
    timestamp: datetime = datetime.utcnow()
    dimensions: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class AnalyticsReport:
    id: int
    name: str
    type: str
    parameters: Dict[str, Any]
    created_at: datetime = datetime.utcnow()
    generated_at: Optional[datetime] = None
    status: str = "pending"
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class AnalyticsDashboard:
    id: int
    name: str
    description: Optional[str] = None
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    widgets: Optional[List[Dict[str, Any]]] = None
    settings: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class AnalyticsSegment:
    id: int
    name: str
    description: Optional[str] = None
    criteria: Dict[str, Any]
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class AnalyticsFunnel:
    id: int
    name: str
    description: Optional[str] = None
    steps: List[Dict[str, Any]]
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class AnalyticsExport:
    id: int
    type: str
    parameters: Dict[str, Any]
    status: str = "pending"
    created_at: datetime = datetime.utcnow()
    completed_at: Optional[datetime] = None
    file_url: Optional[str] = None
    file_size: Optional[int] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class AnalyticsAlert:
    id: int
    name: str
    condition: Dict[str, Any]
    threshold: float
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    last_triggered: Optional[datetime] = None
    recipients: Optional[List[int]] = None
    metadata: Optional[Dict[str, Any]] = None 