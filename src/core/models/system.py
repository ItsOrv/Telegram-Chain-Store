from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

@dataclass
class SystemConfig:
    id: int
    key: str
    value: Any
    type: str
    group: str
    is_system: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    description: Optional[str] = None
    validation_rules: Optional[Dict[str, Any]] = None
    options: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class SystemStatus:
    id: int
    component: str
    status: str
    message: Optional[str] = None
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    last_check: Optional[datetime] = None
    next_check: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class SystemMetric:
    id: int
    name: str
    value: float
    type: str  # cpu, memory, disk, etc.
    timestamp: datetime = datetime.utcnow()
    dimensions: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class SystemJob:
    id: int
    name: str
    type: str
    status: str = "pending"
    created_at: datetime = datetime.utcnow()
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    progress: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class SystemSchedule:
    id: int
    name: str
    job_type: str
    schedule_type: str  # cron, interval
    schedule_data: Dict[str, Any]
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class SystemAlert:
    id: int
    name: str
    condition: Dict[str, Any]
    severity: str  # info, warning, error, critical
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    last_triggered: Optional[datetime] = None
    recipients: Optional[List[int]] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class SystemLog:
    id: int
    level: str  # debug, info, warning, error, critical
    message: str
    component: str
    created_at: datetime = datetime.utcnow()
    metadata: Optional[Dict[str, Any]] = None
    stack_trace: Optional[str] = None
    user_id: Optional[int] = None

@dataclass
class SystemMaintenance:
    id: int
    type: str
    status: str = "pending"
    scheduled_at: datetime
    completed_at: Optional[datetime] = None
    duration: Optional[float] = None
    description: Optional[str] = None
    affected_components: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class SystemBackup:
    id: int
    type: str  # full, incremental
    status: str = "pending"
    created_at: datetime = datetime.utcnow()
    completed_at: Optional[datetime] = None
    file_url: Optional[str] = None
    file_size: Optional[int] = None
    checksum: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None 