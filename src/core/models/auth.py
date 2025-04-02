from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

@dataclass
class User:
    id: int
    username: str
    email: str
    password_hash: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    last_login: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    roles: Optional[List[int]] = None
    permissions: Optional[List[int]] = None
    settings: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class Session:
    id: int
    user_id: int
    token: str
    device_type: str
    ip_address: str
    user_agent: str
    created_at: datetime = datetime.utcnow()
    expires_at: datetime
    last_activity: Optional[datetime] = None
    is_active: bool = True
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class Token:
    id: int
    user_id: int
    token_type: str  # access, refresh, reset, etc.
    token: str
    created_at: datetime = datetime.utcnow()
    expires_at: datetime
    is_revoked: bool = False
    revoked_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class VerificationCode:
    id: int
    user_id: int
    code_type: str  # email, phone, etc.
    code: str
    created_at: datetime = datetime.utcnow()
    expires_at: datetime
    is_used: bool = False
    used_at: Optional[datetime] = None
    attempts: int = 0
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class LoginAttempt:
    id: int
    user_id: Optional[int]
    ip_address: str
    user_agent: str
    status: str  # success, failed
    created_at: datetime = datetime.utcnow()
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class PasswordReset:
    id: int
    user_id: int
    token: str
    created_at: datetime = datetime.utcnow()
    expires_at: datetime
    is_used: bool = False
    used_at: Optional[datetime] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class TwoFactorAuth:
    id: int
    user_id: int
    method: str  # app, sms, email
    secret: str
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    backup_codes: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class AuthProvider:
    id: int
    name: str
    provider_type: str  # google, facebook, etc.
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    settings: Optional[Dict[str, Any]] = None
    credentials: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class UserProvider:
    id: int
    user_id: int
    provider_id: int
    provider_user_id: str
    created_at: datetime = datetime.utcnow()
    last_login: Optional[datetime] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None 