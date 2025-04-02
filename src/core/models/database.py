from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

@dataclass
class Database:
    id: int
    name: str
    type: str  # mysql, postgresql, etc.
    host: str
    port: int
    username: str
    password: str
    database: str
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    settings: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class DatabaseConnection:
    id: int
    database_id: int
    status: str
    created_at: datetime = datetime.utcnow()
    closed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class DatabaseQuery:
    id: int
    database_id: int
    query: str
    execution_time: float
    status: str
    created_at: datetime = datetime.utcnow()
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    affected_rows: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class DatabaseMigration:
    id: int
    version: str
    description: str
    created_at: datetime = datetime.utcnow()
    executed_at: Optional[datetime] = None
    status: str = "pending"
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class DatabaseBackup:
    id: int
    database_id: int
    type: str  # full, incremental
    status: str = "pending"
    created_at: datetime = datetime.utcnow()
    completed_at: Optional[datetime] = None
    file_url: Optional[str] = None
    file_size: Optional[int] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class DatabaseRestore:
    id: int
    backup_id: int
    status: str = "pending"
    created_at: datetime = datetime.utcnow()
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class DatabaseLog:
    id: int
    database_id: int
    event_type: str
    description: str
    created_at: datetime = datetime.utcnow()
    metadata: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    user_id: Optional[int] = None

@dataclass
class DatabaseMonitor:
    id: int
    database_id: int
    metric_type: str  # cpu, memory, connections, etc.
    value: float
    created_at: datetime = datetime.utcnow()
    metadata: Optional[Dict[str, Any]] = None 