from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

@dataclass
class Backup:
    id: int
    name: str
    type: str  # full, incremental, etc.
    status: str = "pending"
    created_at: datetime = datetime.utcnow()
    completed_at: Optional[datetime] = None
    file_url: Optional[str] = None
    file_size: Optional[int] = None
    error_message: Optional[str] = None
    created_by: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    checksum: Optional[str] = None
    compression: Optional[str] = None

@dataclass
class BackupSchedule:
    id: int
    name: str
    type: str
    schedule_type: str  # daily, weekly, monthly, etc.
    schedule_data: Dict[str, Any]
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    last_run_at: Optional[datetime] = None
    next_run_at: Optional[datetime] = None
    retention_days: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class BackupStorage:
    id: int
    name: str
    type: str  # local, s3, ftp, etc.
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    description: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None
    credentials: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class BackupVerification:
    id: int
    backup_id: int
    status: str
    created_at: datetime = datetime.utcnow()
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    verification_type: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class BackupRestore:
    id: int
    backup_id: int
    status: str = "pending"
    created_at: datetime = datetime.utcnow()
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_by: Optional[int] = None
    target_location: Optional[str] = None
    restore_type: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class BackupLog:
    id: int
    backup_id: int
    event_type: str
    description: str
    created_at: datetime = datetime.utcnow()
    metadata: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    user_id: Optional[int] = None

@dataclass
class BackupCleanup:
    id: int
    backup_id: int
    status: str = "pending"
    created_at: datetime = datetime.utcnow()
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_by: Optional[int] = None
    reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class BackupEncryption:
    id: int
    backup_id: int
    encryption_type: str
    status: str = "pending"
    created_at: datetime = datetime.utcnow()
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    key_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None 