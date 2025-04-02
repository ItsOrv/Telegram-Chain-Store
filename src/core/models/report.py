from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass

@dataclass
class Report:
    id: int
    name: str
    type: str  # sales, inventory, customer, etc.
    format: str  # pdf, csv, excel, etc.
    status: str = "pending"
    created_at: datetime = datetime.utcnow()
    generated_at: Optional[datetime] = None
    created_by: int
    parameters: Optional[dict] = None
    file_url: Optional[str] = None
    file_size: Optional[int] = None
    error_message: Optional[str] = None
    metadata: Optional[dict] = None

@dataclass
class ReportTemplate:
    id: int
    name: str
    code: str
    type: str
    query: str
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    description: Optional[str] = None
    parameters: Optional[List[dict]] = None
    default_format: str = "pdf"
    schedule: Optional[dict] = None
    recipients: Optional[List[int]] = None

@dataclass
class ReportSchedule:
    id: int
    template_id: int
    schedule_type: str  # daily, weekly, monthly, etc.
    schedule_data: dict
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    last_run_at: Optional[datetime] = None
    next_run_at: Optional[datetime] = None
    recipients: Optional[List[int]] = None
    conditions: Optional[dict] = None

@dataclass
class ReportParameter:
    id: int
    template_id: int
    name: str
    type: str
    label: str
    is_required: bool = False
    default_value: Optional[str] = None
    options: Optional[List[str]] = None
    validation_rules: Optional[dict] = None
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    description: Optional[str] = None

@dataclass
class ReportCategory:
    id: int
    name: str
    code: str
    description: Optional[str] = None
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    parent_id: Optional[int] = None
    templates: Optional[List[int]] = None
    settings: Optional[dict] = None

@dataclass
class ReportAccess:
    id: int
    user_id: int
    template_id: int
    permission_level: str  # view, generate, schedule, etc.
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    expires_at: Optional[datetime] = None
    conditions: Optional[dict] = None
    notes: Optional[str] = None

@dataclass
class ReportLog:
    id: int
    report_id: int
    event_type: str
    description: str
    created_at: datetime = datetime.utcnow()
    metadata: Optional[dict] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    user_id: Optional[int] = None

@dataclass
class ReportExport:
    id: int
    report_id: int
    format: str
    status: str = "pending"
    created_at: datetime = datetime.utcnow()
    completed_at: Optional[datetime] = None
    file_url: Optional[str] = None
    file_size: Optional[int] = None
    error_message: Optional[str] = None
    metadata: Optional[dict] = None 