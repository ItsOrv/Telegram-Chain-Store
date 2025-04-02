import pytest
from datetime import datetime
from src.core.models.monitoring import (
    Monitor, MonitorType, MonitorTarget,
    MonitorAlert, MonitorMetric, MonitorLog,
    MonitorSchedule, MonitorConfig, MonitorStatus,
    MonitorReport
)

def test_monitor_creation():
    monitor = Monitor(
        id=1,
        name="API Health",
        description="API health monitoring",
        type="health",
        status="active",
        created_at=datetime.now()
    )
    
    assert monitor.id == 1
    assert monitor.name == "API Health"
    assert monitor.description == "API health monitoring"
    assert monitor.type == "health"
    assert monitor.status == "active"
    assert isinstance(monitor.created_at, datetime)

def test_monitor_type_creation():
    monitor_type = MonitorType(
        id=1,
        name="Health Check",
        description="System health monitoring",
        category="system",
        is_active=True
    )
    
    assert monitor_type.id == 1
    assert monitor_type.name == "Health Check"
    assert monitor_type.description == "System health monitoring"
    assert monitor_type.category == "system"
    assert monitor_type.is_active is True

def test_monitor_target_creation():
    target = MonitorTarget(
        id=1,
        monitor_id=1,
        name="API Endpoint",
        description="API endpoint monitoring",
        type="http",
        url="https://api.example.com/health",
        is_active=True
    )
    
    assert target.id == 1
    assert target.monitor_id == 1
    assert target.name == "API Endpoint"
    assert target.description == "API endpoint monitoring"
    assert target.type == "http"
    assert target.url == "https://api.example.com/health"
    assert target.is_active is True

def test_monitor_alert_creation():
    alert = MonitorAlert(
        id=1,
        monitor_id=1,
        name="High Response Time",
        description="Alert on high API response time",
        condition="response_time > 1000",
        severity="warning",
        is_active=True
    )
    
    assert alert.id == 1
    assert alert.monitor_id == 1
    assert alert.name == "High Response Time"
    assert alert.description == "Alert on high API response time"
    assert alert.condition == "response_time > 1000"
    assert alert.severity == "warning"
    assert alert.is_active is True

def test_monitor_metric_creation():
    metric = MonitorMetric(
        id=1,
        monitor_id=1,
        name="Response Time",
        description="API response time",
        value=150,
        unit="ms",
        timestamp=datetime.now()
    )
    
    assert metric.id == 1
    assert metric.monitor_id == 1
    assert metric.name == "Response Time"
    assert metric.description == "API response time"
    assert metric.value == 150
    assert metric.unit == "ms"
    assert isinstance(metric.timestamp, datetime)

def test_monitor_log_creation():
    log = MonitorLog(
        id=1,
        monitor_id=1,
        status="success",
        message="Health check passed",
        details={
            "response_time": 150,
            "status_code": 200
        },
        created_at=datetime.now()
    )
    
    assert log.id == 1
    assert log.monitor_id == 1
    assert log.status == "success"
    assert log.message == "Health check passed"
    assert isinstance(log.details, dict)
    assert isinstance(log.created_at, datetime)

def test_monitor_schedule_creation():
    schedule = MonitorSchedule(
        id=1,
        monitor_id=1,
        name="Every 5 Minutes",
        description="Check every 5 minutes",
        frequency="5m",
        is_active=True
    )
    
    assert schedule.id == 1
    assert schedule.monitor_id == 1
    assert schedule.name == "Every 5 Minutes"
    assert schedule.description == "Check every 5 minutes"
    assert schedule.frequency == "5m"
    assert schedule.is_active is True

def test_monitor_config_creation():
    config = MonitorConfig(
        id=1,
        monitor_id=1,
        name="HTTP Config",
        description="HTTP monitoring settings",
        settings={
            "timeout": 5,
            "retries": 3,
            "headers": {
                "User-Agent": "Monitor/1.0"
            }
        },
        is_active=True
    )
    
    assert config.id == 1
    assert config.monitor_id == 1
    assert config.name == "HTTP Config"
    assert config.description == "HTTP monitoring settings"
    assert isinstance(config.settings, dict)
    assert config.is_active is True

def test_monitor_status_creation():
    status = MonitorStatus(
        id=1,
        monitor_id=1,
        status="healthy",
        message="All checks passed",
        timestamp=datetime.now()
    )
    
    assert status.id == 1
    assert status.monitor_id == 1
    assert status.status == "healthy"
    assert status.message == "All checks passed"
    assert isinstance(status.timestamp, datetime)

def test_monitor_report_creation():
    report = MonitorReport(
        id=1,
        monitor_id=1,
        name="Daily Report",
        description="Daily monitoring report",
        type="summary",
        status="generated",
        created_at=datetime.now()
    )
    
    assert report.id == 1
    assert report.monitor_id == 1
    assert report.name == "Daily Report"
    assert report.description == "Daily monitoring report"
    assert report.type == "summary"
    assert report.status == "generated"
    assert isinstance(report.created_at, datetime) 