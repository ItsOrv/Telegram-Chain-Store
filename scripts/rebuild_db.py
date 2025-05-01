#!/usr/bin/env python3
import os
import sys
import shutil
import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.database import Database, drop_tables, create_tables
from src.core.config import load_settings
from src.utils.logger import setup_logger

# Import models to ensure they're all registered
from src.core.models.cart import CartItem, Cart
from src.core.models import Base

logger = setup_logger("db_rebuild")

def backup_database():
    """Create a backup of the current database file"""
    db_path = "data/chainstore.db"
    if os.path.exists(db_path):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"data/chainstore_backup_{timestamp}.db"
        shutil.copy2(db_path, backup_path)
        logger.info(f"Database backed up to {backup_path}")
        return True
    else:
        logger.warning("No database file found to backup")
        return False

def rebuild_database():
    """Drop and recreate all database tables"""
    logger.info("Starting database rebuild...")
    
    # Load settings
    settings = load_settings()
    
    # Initialize database
    db = Database(settings.database)
    
    try:
        # Drop all tables
        logger.info("Dropping all tables...")
        drop_tables()
        
        # Create all tables
        logger.info("Creating all tables...")
        create_tables()
        
        logger.info("Database rebuild completed successfully")
        return True
    except Exception as e:
        logger.error(f"Error rebuilding database: {str(e)}")
        return False

if __name__ == "__main__":
    print("This script will backup and then COMPLETELY REBUILD your database.")
    print("ALL EXISTING DATA WILL BE LOST.")
    
    confirmation = input("Do you want to continue? (yes/no): ")
    
    if confirmation.lower() == "yes":
        backed_up = backup_database()
        if backed_up:
            print(f"Database backed up successfully.")
        
        success = rebuild_database()
        if success:
            print("Database rebuilt successfully.")
        else:
            print("Failed to rebuild database. See logs for details.")
    else:
        print("Operation cancelled.") 