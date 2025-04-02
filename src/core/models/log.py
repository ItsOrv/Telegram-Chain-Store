from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

@dataclass
class Log:
    id: int
    level: str  # debug, info, warning, error, critical
    message: str
    module: str
    function: str
    line_number: int
    created_at: datetime = datetime.utcnow()
    user_id: Optional[int] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    request_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    traceback: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class LogConfig:
    id: int
    name: str
    level: str
    format: str
    handler: str
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    description: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None
    filters: Optional[List[str]] = None
    rotation: Optional[Dict[str, Any]] = None

@dataclass
class LogFilter:
    id: int
    name: str
    pattern: str
    level: str
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    description: Optional[str] = None
    conditions: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class LogHandler:
    id: int
    name: str
    type: str  # file, console, email, etc.
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    description: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None
    filters: Optional[List[int]] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class LogRotation:
    id: int
    handler_id: int
    max_size: int
    backup_count: int
    interval: str  # daily, weekly, monthly
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    last_rotation: Optional[datetime] = None
    next_rotation: Optional[datetime] = None
    settings: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class LogExport:
    id: int
    format: str
    status: str = "pending"
    created_at: datetime = datetime.utcnow()
    completed_at: Optional[datetime] = None
    file_url: Optional[str] = None
    file_size: Optional[int] = None
    error_message: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class LogAlert:
    id: int
    name: str
    condition: str
    threshold: int
    interval: str
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    last_triggered: Optional[datetime] = None
    recipients: Optional[List[int]] = None
    actions: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class LogArchive:
    id: int
    start_date: datetime
    end_date: datetime
    status: str = "pending"
    created_at: datetime = datetime.utcnow()
    completed_at: Optional[datetime] = None
    file_url: Optional[str] = None
    file_size: Optional[int] = None
    error_message: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None 