from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

@dataclass
class NetworkRequest:
    id: int
    method: str
    url: str
    status_code: int
    response_time: float
    created_at: datetime = datetime.utcnow()
    user_id: Optional[int] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    request_headers: Optional[Dict[str, str]] = None
    request_body: Optional[Dict[str, Any]] = None
    response_headers: Optional[Dict[str, str]] = None
    response_body: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class NetworkEndpoint:
    id: int
    name: str
    url: str
    method: str
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    description: Optional[str] = None
    headers: Optional[Dict[str, str]] = None
    timeout: Optional[float] = None
    retry_count: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class NetworkRateLimit:
    id: int
    endpoint_id: int
    requests_per_minute: int
    burst_size: int
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    description: Optional[str] = None
    conditions: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class NetworkProxy:
    id: int
    host: str
    port: int
    protocol: str
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    description: Optional[str] = None
    credentials: Optional[Dict[str, str]] = None
    settings: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class NetworkSSL:
    id: int
    domain: str
    certificate: str
    private_key: str
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    expires_at: Optional[datetime] = None
    issuer: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class NetworkDNS:
    id: int
    domain: str
    record_type: str
    record_value: str
    ttl: int
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class NetworkFirewall:
    id: int
    name: str
    rule_type: str
    source: str
    destination: str
    action: str
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    description: Optional[str] = None
    conditions: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class NetworkMonitor:
    id: int
    endpoint_id: int
    check_type: str
    interval: int
    timeout: float
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    last_check: Optional[datetime] = None
    last_status: Optional[str] = None
    alert_recipients: Optional[List[int]] = None
    metadata: Optional[Dict[str, Any]] = None 