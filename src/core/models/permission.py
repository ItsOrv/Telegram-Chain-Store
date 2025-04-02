from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

@dataclass
class Permission:
    id: int
    name: str
    code: str
    description: Optional[str] = None
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    module: Optional[str] = None
    actions: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class Role:
    id: int
    name: str
    code: str
    description: Optional[str] = None
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    permissions: Optional[List[int]] = None
    parent_id: Optional[int] = None
    level: int = 0
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class UserRole:
    id: int
    user_id: int
    role_id: int
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    expires_at: Optional[datetime] = None
    created_by: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class RolePermission:
    id: int
    role_id: int
    permission_id: int
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    expires_at: Optional[datetime] = None
    created_by: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class PermissionGroup:
    id: int
    name: str
    code: str
    description: Optional[str] = None
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    parent_id: Optional[int] = None
    permissions: Optional[List[int]] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class PermissionOverride:
    id: int
    permission_id: int
    entity_type: str  # user, role, etc.
    entity_id: int
    is_granted: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    expires_at: Optional[datetime] = None
    created_by: Optional[int] = None
    reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class PermissionRequest:
    id: int
    user_id: int
    permission_id: int
    status: str = "pending"
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    approved_at: Optional[datetime] = None
    approved_by: Optional[int] = None
    reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class PermissionLog:
    id: int
    user_id: int
    permission_id: int
    action: str
    status: str
    created_at: datetime = datetime.utcnow()
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None 