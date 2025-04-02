import pytest
from datetime import datetime
from src.core.models.system import (
    System, SystemComponent, SystemStatus,
    SystemConfig, SystemLog, SystemMetric,
    SystemAlert, SystemBackup, SystemUpdate,
    SystemHealth
)

def test_system_creation():
    system = System(
        id=1,
        name="Production System",
        description="Main production environment",
        environment="production",
        status="active",
        created_at=datetime.now()
    )
    
    assert system.id == 1
    assert system.name == "Production System"
    assert system.description == "Main production environment"
    assert system.environment == "production"
    assert system.status == "active"
    assert isinstance(system.created_at, datetime)

def test_system_component_creation():
    component = SystemComponent(
        id=1,
        system_id=1,
        name="Database",
        description="Main database server",
        type="database",
        status="active",
        is_active=True
    )
    
    assert component.id == 1
    assert component.system_id == 1
    assert component.name == "Database"
    assert component.description == "Main database server"
    assert component.type == "database"
    assert component.status == "active"
    assert component.is_active is True

def test_system_status_creation():
    status = SystemStatus(
        id=1,
        system_id=1,
        component_id=1,
        status="healthy",
        message="All systems operational",
        timestamp=datetime.now()
    )
    
    assert status.id == 1
    assert status.system_id == 1
    assert status.component_id == 1
    assert status.status == "healthy"
    assert status.message == "All systems operational"
    assert isinstance(status.timestamp, datetime)

def test_system_config_creation():
    config = SystemConfig(
        id=1,
        system_id=1,
        name="Database Config",
        description="Database configuration",
        settings={
            "host": "localhost",
            "port": 5432,
            "database": "mydb"
        },
        is_active=True
    )
    
    assert config.id == 1
    assert config.system_id == 1
    assert config.name == "Database Config"
    assert config.description == "Database configuration"
    assert isinstance(config.settings, dict)
    assert config.is_active is True

def test_system_log_creation():
    log = SystemLog(
        id=1,
        system_id=1,
        component_id=1,
        level="info",
        message="System started successfully",
        data={
            "version": "1.0.0",
            "uptime": "1h"
        },
        created_at=datetime.now()
    )
    
    assert log.id == 1
    assert log.system_id == 1
    assert log.component_id == 1
    assert log.level == "info"
    assert log.message == "System started successfully"
    assert isinstance(log.data, dict)
    assert isinstance(log.created_at, datetime)

def test_system_metric_creation():
    metric = SystemMetric(
        id=1,
        system_id=1,
        component_id=1,
        name="cpu_usage",
        value=75.5,
        unit="%",
        timestamp=datetime.now()
    )
    
    assert metric.id == 1
    assert metric.system_id == 1
    assert metric.component_id == 1
    assert metric.name == "cpu_usage"
    assert metric.value == 75.5
    assert metric.unit == "%"
    assert isinstance(metric.timestamp, datetime)

def test_system_alert_creation():
    alert = SystemAlert(
        id=1,
        system_id=1,
        component_id=1,
        name="High CPU Usage",
        description="CPU usage above threshold",
        severity="warning",
        status="open",
        created_at=datetime.now()
    )
    
    assert alert.id == 1
    assert alert.system_id == 1
    assert alert.component_id == 1
    assert alert.name == "High CPU Usage"
    assert alert.description == "CPU usage above threshold"
    assert alert.severity == "warning"
    assert alert.status == "open"
    assert isinstance(alert.created_at, datetime)

def test_system_backup_creation():
    backup = SystemBackup(
        id=1,
        system_id=1,
        name="Daily Backup",
        description="Daily system backup",
        status="completed",
        file_path="/path/to/backup.tar.gz",
        created_at=datetime.now()
    )
    
    assert backup.id == 1
    assert backup.system_id == 1
    assert backup.name == "Daily Backup"
    assert backup.description == "Daily system backup"
    assert backup.status == "completed"
    assert backup.file_path == "/path/to/backup.tar.gz"
    assert isinstance(backup.created_at, datetime)

def test_system_update_creation():
    update = SystemUpdate(
        id=1,
        system_id=1,
        name="Security Update",
        description="Security patches update",
        version="1.0.1",
        status="pending",
        scheduled_at=datetime.now()
    )
    
    assert update.id == 1
    assert update.system_id == 1
    assert update.name == "Security Update"
    assert update.description == "Security patches update"
    assert update.version == "1.0.1"
    assert update.status == "pending"
    assert isinstance(update.scheduled_at, datetime)

def test_system_health_creation():
    health = SystemHealth(
        id=1,
        system_id=1,
        status="healthy",
        score=95,
        details={
            "cpu_usage": 75,
            "memory_usage": 80,
            "disk_usage": 60
        },
        timestamp=datetime.now()
    )
    
    assert health.id == 1
    assert health.system_id == 1
    assert health.status == "healthy"
    assert health.score == 95
    assert isinstance(health.details, dict)
    assert isinstance(health.timestamp, datetime) 