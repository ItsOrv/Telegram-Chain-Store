import pytest
from datetime import datetime
from src.core.models.backup import (
    Backup, BackupType, BackupSchedule,
    BackupConfig, BackupLog, BackupStatus,
    BackupStorage, BackupRestore, BackupReport,
    BackupVerification
)

def test_backup_creation():
    backup = Backup(
        id=1,
        name="Daily Backup",
        description="Daily system backup",
        type="full",
        status="completed",
        created_at=datetime.now()
    )
    
    assert backup.id == 1
    assert backup.name == "Daily Backup"
    assert backup.description == "Daily system backup"
    assert backup.type == "full"
    assert backup.status == "completed"
    assert isinstance(backup.created_at, datetime)

def test_backup_type_creation():
    backup_type = BackupType(
        id=1,
        name="Full Backup",
        description="Complete system backup",
        retention_days=30,
        is_active=True
    )
    
    assert backup_type.id == 1
    assert backup_type.name == "Full Backup"
    assert backup_type.description == "Complete system backup"
    assert backup_type.retention_days == 30
    assert backup_type.is_active is True

def test_backup_schedule_creation():
    schedule = BackupSchedule(
        id=1,
        backup_id=1,
        name="Daily Schedule",
        description="Daily backup schedule",
        frequency="daily",
        time="00:00",
        is_active=True
    )
    
    assert schedule.id == 1
    assert schedule.backup_id == 1
    assert schedule.name == "Daily Schedule"
    assert schedule.description == "Daily backup schedule"
    assert schedule.frequency == "daily"
    assert schedule.time == "00:00"
    assert schedule.is_active is True

def test_backup_config_creation():
    config = BackupConfig(
        id=1,
        backup_id=1,
        name="Storage Config",
        description="Backup storage configuration",
        settings={
            "storage_type": "s3",
            "bucket": "my-backups",
            "region": "us-east-1"
        },
        is_active=True
    )
    
    assert config.id == 1
    assert config.backup_id == 1
    assert config.name == "Storage Config"
    assert config.description == "Backup storage configuration"
    assert isinstance(config.settings, dict)
    assert config.is_active is True

def test_backup_log_creation():
    log = BackupLog(
        id=1,
        backup_id=1,
        status="completed",
        message="Backup completed successfully",
        details={
            "size": "1.5GB",
            "duration": "15m",
            "files": 1000
        },
        created_at=datetime.now()
    )
    
    assert log.id == 1
    assert log.backup_id == 1
    assert log.status == "completed"
    assert log.message == "Backup completed successfully"
    assert isinstance(log.details, dict)
    assert isinstance(log.created_at, datetime)

def test_backup_status_creation():
    status = BackupStatus(
        id=1,
        backup_id=1,
        status="in_progress",
        progress=75,
        message="Backup in progress",
        timestamp=datetime.now()
    )
    
    assert status.id == 1
    assert status.backup_id == 1
    assert status.status == "in_progress"
    assert status.progress == 75
    assert status.message == "Backup in progress"
    assert isinstance(status.timestamp, datetime)

def test_backup_storage_creation():
    storage = BackupStorage(
        id=1,
        backup_id=1,
        name="S3 Storage",
        description="Amazon S3 storage",
        type="s3",
        location="my-backups",
        is_active=True
    )
    
    assert storage.id == 1
    assert storage.backup_id == 1
    assert storage.name == "S3 Storage"
    assert storage.description == "Amazon S3 storage"
    assert storage.type == "s3"
    assert storage.location == "my-backups"
    assert storage.is_active is True

def test_backup_restore_creation():
    restore = BackupRestore(
        id=1,
        backup_id=1,
        name="System Restore",
        description="System restore from backup",
        status="completed",
        started_at=datetime.now(),
        completed_at=datetime.now()
    )
    
    assert restore.id == 1
    assert restore.backup_id == 1
    assert restore.name == "System Restore"
    assert restore.description == "System restore from backup"
    assert restore.status == "completed"
    assert isinstance(restore.started_at, datetime)
    assert isinstance(restore.completed_at, datetime)

def test_backup_report_creation():
    report = BackupReport(
        id=1,
        backup_id=1,
        name="Monthly Report",
        description="Monthly backup report",
        type="summary",
        status="generated",
        created_at=datetime.now()
    )
    
    assert report.id == 1
    assert report.backup_id == 1
    assert report.name == "Monthly Report"
    assert report.description == "Monthly backup report"
    assert report.type == "summary"
    assert report.status == "generated"
    assert isinstance(report.created_at, datetime)

def test_backup_verification_creation():
    verification = BackupVerification(
        id=1,
        backup_id=1,
        name="Integrity Check",
        description="Backup integrity verification",
        status="passed",
        details={
            "checksum": "abc123",
            "size": "1.5GB",
            "files": 1000
        },
        created_at=datetime.now()
    )
    
    assert verification.id == 1
    assert verification.backup_id == 1
    assert verification.name == "Integrity Check"
    assert verification.description == "Backup integrity verification"
    assert verification.status == "passed"
    assert isinstance(verification.details, dict)
    assert isinstance(verification.created_at, datetime) 