#!/usr/bin/env python3
"""
Simple Database Setup Script
This script sets up the database with password authentication using default values.
"""

import os
import sys
import pymysql
import subprocess
from pathlib import Path

# Configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'admin_user': 'root',
    'admin_password': 'root',  # Use 'root' as the default password
    'user': 'chainstore_user',
    'password': 'chainstore_password',  # Default password for the database user
    'database': 'chainstore_db',
    'charset': 'utf8mb4'
}

def setup_database():
    """Set up the database with password authentication"""
    print("Starting database setup...")
    
    # Connect to MySQL with admin user
    try:
        print(f"Connecting to MySQL with admin user {DB_CONFIG['admin_user']}...")
        connection = pymysql.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['admin_user'],
            password=DB_CONFIG['admin_password'],
            charset=DB_CONFIG['charset']
        )
        print("Successfully connected to MySQL.")
    except pymysql.Error as e:
        print(f"Error connecting to MySQL: {e}")
        print("Make sure MySQL is installed and running.")
        return False
    
    try:
        with connection.cursor() as cursor:
            # Create database if not exists
            print(f"Creating database {DB_CONFIG['database']}...")
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_CONFIG['database']}` CHARACTER SET {DB_CONFIG['charset']} COLLATE {DB_CONFIG['charset']}_unicode_ci;")
            
            # Drop user if exists
            print(f"Setting up user {DB_CONFIG['user']}...")
            cursor.execute(f"DROP USER IF EXISTS '{DB_CONFIG['user']}'@'localhost';")
            
            # Create user with password
            cursor.execute(f"CREATE USER '{DB_CONFIG['user']}'@'localhost' IDENTIFIED BY '{DB_CONFIG['password']}';")
            
            # Grant privileges
            cursor.execute(f"GRANT ALL PRIVILEGES ON `{DB_CONFIG['database']}`.* TO '{DB_CONFIG['user']}'@'localhost';")
            cursor.execute("FLUSH PRIVILEGES;")
            
            print(f"Database and user setup completed successfully.")
        
        # Update .env file
        update_env_file()
        
        # Run migrations
        print("Running database migrations...")
        try:
            result = subprocess.run(['alembic', 'upgrade', 'head'], capture_output=True, text=True)
            if result.returncode == 0:
                print("Migrations completed successfully.")
            else:
                print(f"Error running migrations: {result.stderr}")
                return False
        except Exception as e:
            print(f"Error running migrations: {e}")
            return False
        
        return True
    except pymysql.Error as e:
        print(f"Error setting up database: {e}")
        return False
    finally:
        connection.close()

def update_env_file():
    """Update the .env file with database settings"""
    env_file = Path('.env')
    if not env_file.exists():
        print(f".env file not found.")
        return False
    
    print("Updating .env file with database settings...")
    
    # Create backup
    env_backup = Path('.env.bak')
    if not env_backup.exists():
        with open(env_file, 'r', encoding='utf-8') as src, open(env_backup, 'w', encoding='utf-8') as dst:
            dst.write(src.read())
    
    # Read content
    with open(env_file, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Define replacements
    replacements = {
        'DB_HOST': DB_CONFIG['host'],
        'DB_PORT': str(DB_CONFIG['port']),
        'DB_USER': DB_CONFIG['user'],
        'DB_PASSWORD': DB_CONFIG['password'],
        'DB_NAME': DB_CONFIG['database'],
        'DB_CHARSET': DB_CONFIG['charset'],
        'DB_AUTH_SOCKET': 'false'
    }
    
    # Apply replacements
    new_content = content
    for key, value in replacements.items():
        if f"{key}=" in new_content:
            # Replace existing value
            lines = new_content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith(f"{key}="):
                    lines[i] = f"{key}={value}"
            new_content = '\n'.join(lines)
        else:
            # Add new value in Database Settings section
            if "# Database Settings" in new_content:
                new_content = new_content.replace(
                    "# Database Settings", 
                    f"# Database Settings\n{key}={value}"
                )
            else:
                # Add at the end
                new_content += f"\n\n# Database Settings\n{key}={value}"
    
    # Write updated content
    with open(env_file, 'w', encoding='utf-8') as file:
        file.write(new_content)
    
    print("Successfully updated .env file.")
    return True

if __name__ == "__main__":
    try:
        if setup_database():
            print("\n✅ Database setup completed successfully!")
            print(f"Database: {DB_CONFIG['database']}")
            print(f"User: {DB_CONFIG['user']}")
            print(f"Password: {DB_CONFIG['password']}")
            print("\nTo run the bot, use the following command:")
            print("python src/main.py")
        else:
            print("\n❌ Database setup failed. Please check the errors above.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\nSetup canceled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1) 