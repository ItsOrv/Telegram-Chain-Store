from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

@dataclass
class Setting:
    id: int
    key: str
    value: Any
    type: str
    group: str
    is_system: bool = False
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    description: Optional[str] = None
    validation_rules: Optional[Dict[str, Any]] = None
    options: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class SettingGroup:
    id: int
    name: str
    code: str
    description: Optional[str] = None
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    parent_id: Optional[int] = None
    settings: Optional[List[int]] = None
    order: int = 0
    icon: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class SettingHistory:
    id: int
    setting_id: int
    old_value: Any
    new_value: Any
    changed_by: int
    created_at: datetime = datetime.utcnow()
    reason: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class SettingOverride:
    id: int
    setting_id: int
    entity_type: str  # user, role, etc.
    entity_id: int
    value: Any
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    expires_at: Optional[datetime] = None
    created_by: Optional[int] = None
    reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class SettingValidation:
    id: int
    setting_id: int
    validation_type: str
    validation_rules: Dict[str, Any]
    error_message: str
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    is_active: bool = True
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class SettingDependency:
    id: int
    setting_id: int
    depends_on_setting_id: int
    condition: str
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    is_active: bool = True
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class SettingCache:
    id: int
    setting_id: int
    value: Any
    created_at: datetime = datetime.utcnow()
    expires_at: datetime
    is_valid: bool = True
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class SettingMigration:
    id: int
    version: str
    description: str
    created_at: datetime = datetime.utcnow()
    executed_at: Optional[datetime] = None
    status: str = "pending"
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None 