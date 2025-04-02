from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

@dataclass
class Cache:
    id: int
    key: str
    value: Any
    type: str
    created_at: datetime = datetime.utcnow()
    expires_at: Optional[datetime] = None
    is_valid: bool = True
    hits: int = 0
    last_hit: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    size: Optional[int] = None

@dataclass
class CacheConfig:
    id: int
    name: str
    type: str  # redis, memcached, etc.
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    description: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None
    credentials: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class CacheTag:
    id: int
    name: str
    description: Optional[str] = None
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    items: Optional[List[int]] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class CacheStats:
    id: int
    cache_id: int
    hits: int
    misses: int
    evictions: int
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class CacheInvalidation:
    id: int
    cache_id: int
    reason: str
    created_at: datetime = datetime.utcnow()
    completed_at: Optional[datetime] = None
    created_by: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class CachePreload:
    id: int
    cache_id: int
    status: str = "pending"
    created_at: datetime = datetime.utcnow()
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_by: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class CacheLock:
    id: int
    cache_id: int
    lock_key: str
    lock_value: str
    expires_at: datetime
    created_at: datetime = datetime.utcnow()
    released_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class CacheMigration:
    id: int
    version: str
    description: str
    created_at: datetime = datetime.utcnow()
    executed_at: Optional[datetime] = None
    status: str = "pending"
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None 