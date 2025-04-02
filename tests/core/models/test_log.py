import pytest
from datetime import datetime
from src.core.models.log import (
    Log, LogLevel, LogCategory,
    LogSource, LogContext, LogFilter,
    LogExport, LogAlert, LogMetric,
    LogTrace
)

def test_log_creation():
    log = Log(
        id=1,
        level="info",
        category="application",
        source="api",
        message="API request received",
        context={
            "method": "GET",
            "path": "/api/users",
            "ip": "192.168.1.1"
        },
        created_at=datetime.now()
    )
    
    assert log.id == 1
    assert log.level == "info"
    assert log.category == "application"
    assert log.source == "api"
    assert log.message == "API request received"
    assert isinstance(log.context, dict)
    assert isinstance(log.created_at, datetime)

def test_log_level_creation():
    level = LogLevel(
        id=1,
        name="INFO",
        description="Information level logs",
        severity=1,
        color="#2196F3"
    )
    
    assert level.id == 1
    assert level.name == "INFO"
    assert level.description == "Information level logs"
    assert level.severity == 1
    assert level.color == "#2196F3"

def test_log_category_creation():
    category = LogCategory(
        id=1,
        name="Application",
        description="Application logs",
        parent_id=None,
        is_active=True
    )
    
    assert category.id == 1
    assert category.name == "Application"
    assert category.description == "Application logs"
    assert category.parent_id is None
    assert category.is_active is True

def test_log_source_creation():
    source = LogSource(
        id=1,
        name="API",
        description="API logs",
        type="service",
        is_active=True
    )
    
    assert source.id == 1
    assert source.name == "API"
    assert source.description == "API logs"
    assert source.type == "service"
    assert source.is_active is True

def test_log_context_creation():
    context = LogContext(
        id=1,
        log_id=1,
        key="user_id",
        value="123",
        type="string"
    )
    
    assert context.id == 1
    assert context.log_id == 1
    assert context.key == "user_id"
    assert context.value == "123"
    assert context.type == "string"

def test_log_filter_creation():
    filter = LogFilter(
        id=1,
        name="Error Logs",
        description="Filter error level logs",
        conditions={
            "level": "error",
            "category": "application"
        },
        is_active=True
    )
    
    assert filter.id == 1
    assert filter.name == "Error Logs"
    assert filter.description == "Filter error level logs"
    assert isinstance(filter.conditions, dict)
    assert filter.is_active is True

def test_log_export_creation():
    export = LogExport(
        id=1,
        name="Daily Export",
        description="Daily log export",
        format="json",
        status="completed",
        file_path="/path/to/export.json",
        created_at=datetime.now()
    )
    
    assert export.id == 1
    assert export.name == "Daily Export"
    assert export.description == "Daily log export"
    assert export.format == "json"
    assert export.status == "completed"
    assert export.file_path == "/path/to/export.json"
    assert isinstance(export.created_at, datetime)

def test_log_alert_creation():
    alert = LogAlert(
        id=1,
        name="Error Rate Alert",
        description="Alert on high error rate",
        condition="error_count > 100",
        severity="high",
        is_active=True
    )
    
    assert alert.id == 1
    assert alert.name == "Error Rate Alert"
    assert alert.description == "Alert on high error rate"
    assert alert.condition == "error_count > 100"
    assert alert.severity == "high"
    assert alert.is_active is True

def test_log_metric_creation():
    metric = LogMetric(
        id=1,
        name="Error Rate",
        description="Error rate per minute",
        value=5.2,
        unit="errors/min",
        timestamp=datetime.now()
    )
    
    assert metric.id == 1
    assert metric.name == "Error Rate"
    assert metric.description == "Error rate per minute"
    assert metric.value == 5.2
    assert metric.unit == "errors/min"
    assert isinstance(metric.timestamp, datetime)

def test_log_trace_creation():
    trace = LogTrace(
        id=1,
        trace_id="abc123",
        span_id="def456",
        parent_id=None,
        name="API Request",
        start_time=datetime.now(),
        end_time=datetime.now()
    )
    
    assert trace.id == 1
    assert trace.trace_id == "abc123"
    assert trace.span_id == "def456"
    assert trace.parent_id is None
    assert trace.name == "API Request"
    assert isinstance(trace.start_time, datetime)
    assert isinstance(trace.end_time, datetime) 