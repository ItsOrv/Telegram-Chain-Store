#!/usr/bin/env python3
"""
Database Setup Script
This script automates all database setup steps including
database creation, user creation, permission granting, and migration execution.
Supports both auth_socket and password authentication methods.
"""

import os
import sys
import subprocess
import argparse
import getpass
import logging
import time
import shutil
import re
from pathlib import Path
import pymysql
import dotenv
from alembic import command
from alembic.config import Config
from alembic.util import exc as alembic_exceptions
from contextlib import contextmanager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('database_setup.log')
    ]
)
logger = logging.getLogger('database_setup')

def find_project_root():
    """Find the project root directory"""
    current_dir = Path(__file__).resolve().parent
    while current_dir.name:
        if (current_dir / 'alembic.ini').exists() or (current_dir / '.env').exists():
            return current_dir
        current_dir = current_dir.parent
    
    # If project root not found, use the current directory's parent
    return Path(__file__).resolve().parent.parent

def load_env_file(env_file=None):
    """Load the .env file"""
    project_root = find_project_root()
    
    if env_file is None:
        env_file = project_root / '.env'
    
    if not env_file.exists():
        logger.error(f".env file not found at {env_file}.")
        sys.exit(1)
    
    logger.info(f"Loading environment file from {env_file}")
    dotenv.load_dotenv(env_file)
    
    return project_root

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Automated database setup')
    
    # Add new automated mode argument
    parser.add_argument('--auto', action='store_true', 
                       help='Automatic mode - use default passwords without prompting')
    
    # General arguments
    parser.add_argument('--env-file', type=str, help='Path to .env file')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show more detailed output')
    parser.add_argument('--skip-migrations', action='store_true', help='Skip running migrations')
    
    # Authentication arguments
    auth_group = parser.add_argument_group('Authentication options')
    auth_exclusive = auth_group.add_mutually_exclusive_group()
    auth_exclusive.add_argument('--auth-socket', action='store_true', help='Use auth_socket for authentication')
    auth_exclusive.add_argument('--password-auth', action='store_true', help='Use password for authentication')
    
    # MySQL arguments
    mysql_group = parser.add_argument_group('MySQL options')
    mysql_group.add_argument('--db-host', type=str, help='MySQL host address')
    mysql_group.add_argument('--db-port', type=int, help='MySQL port')
    mysql_group.add_argument('--db-user', type=str, help='MySQL username')
    mysql_group.add_argument('--db-password', type=str, help='MySQL password (not recommended, better to enter interactively)')
    mysql_group.add_argument('--db-name', type=str, help='Database name')
    mysql_group.add_argument('--admin-user', type=str, default='root', help='MySQL admin username (for creating user and database)')
    mysql_group.add_argument('--admin-password', type=str, help='MySQL admin password (not recommended)')
    
    # Add default passwords
    mysql_group.add_argument('--default-admin-password', type=str,
                            default='root', help='Default admin password for auto mode')
    mysql_group.add_argument('--default-user-password', type=str,
                            default='chainstore123', help='Default user password for auto mode')
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    return args

def get_mysql_config(args):
    """Get MySQL settings from arguments or .env file"""
    config = {
        'host': args.db_host or os.getenv('DB_HOST', 'localhost'),
        'port': args.db_port or int(os.getenv('DB_PORT', 3306)),
        'user': args.db_user or os.getenv('DB_USER', 'chainstore_user'),
        'password': args.db_password or os.getenv('DB_PASSWORD', ''),
        'database': args.db_name or os.getenv('DB_NAME', 'chainstore_db'),
        'admin_user': args.admin_user,
        'admin_password': args.admin_password,
        'use_auth_socket': args.auth_socket or os.getenv('DB_AUTH_SOCKET', 'false').lower() in ('true', '1', 'yes')
    }
    
    # Use default passwords in auto mode
    if args.auto:
        if not config['admin_password']:
            config['admin_password'] = args.default_admin_password
        if not config['password']:
            config['password'] = args.default_user_password
        logger.info(f"Auto mode: Using default passwords")
        return config
    
    # If not in auto mode, use existing password prompt logic
    if not config['admin_password'] and not (config['use_auth_socket'] and args.auth_socket):
        try:
            config['admin_password'] = getpass.getpass(f"Please enter password for MySQL {config['admin_user']}: ")
        except Exception as e:
            logger.warning(f"Could not get password interactively: {e}. Using default password.")
            config['admin_password'] = args.default_admin_password
    
    if not config['password'] and not config['use_auth_socket'] and args.password_auth:
        try:
            config['password'] = getpass.getpass(f"Please enter password for user {config['user']}: ")
        except Exception as e:
            logger.warning(f"Could not get password interactively: {e}. Using default password.")
            config['password'] = args.default_user_password
    
    return config

def test_mysql_connection(config, admin=False):
    """Test MySQL connection"""
    user = config['admin_user'] if admin else config['user']
    password = config['admin_password'] if admin else config['password']
    
    # Try different connection methods
    connection_methods = []
    
    # Method 1: Try auth_socket if enabled
    if config['use_auth_socket']:
        connection_methods.append({
            'type': 'auth_socket',
            'params': {
                'host': 'localhost',
                'user': user,
                'unix_socket': '/var/run/mysqld/mysqld.sock',
                'db': config['database'] if not admin else None,
                'charset': 'utf8mb4'
            }
        })
    
    # Method 2: Try password authentication
    connection_methods.append({
        'type': 'password',
        'params': {
            'host': config['host'],
            'port': config['port'],
            'user': user,
            'password': password,
            'charset': 'utf8mb4'
        }
    })
    
    # Try each connection method
    for method in connection_methods:
        try:
            logger.debug(f"Trying {method['type']} connection for user {user}")
            connection = pymysql.connect(**method['params'])
            connection.close()
            logger.info(f"Successfully connected to MySQL with user {user} using {method['type']} authentication.")
            
            # If we're using a different method than configured, update the config
            if method['type'] == 'password' and config['use_auth_socket']:
                logger.warning(f"Auth socket failed but password auth worked. Updating configuration.")
                config['use_auth_socket'] = False
                
            return True
        except pymysql.Error as e:
            logger.debug(f"Error connecting to MySQL with user {user} using {method['type']}: {e}")
    
    # If we get here, all connection methods failed
    return False

def create_database(config, args):
    """Create database"""
    connection = None
    
    try:
        # Try auth_socket first if enabled
        if config['use_auth_socket']:
            try:
                connection = pymysql.connect(
                    host='localhost',
                    user=config['admin_user'],
                    unix_socket='/var/run/mysqld/mysqld.sock',
                    charset='utf8mb4'
                )
                logger.info(f"Connected to MySQL using auth_socket.")
            except pymysql.Error as e:
                logger.warning(f"Auth socket connection failed: {e}")
                connection = None
        
        # If auth_socket failed or not enabled, try password
        if connection is None:
            connection = pymysql.connect(
                host=config['host'],
                port=config['port'],
                user=config['admin_user'],
                password=config['admin_password'],
                charset='utf8mb4'
            )
            logger.info(f"Connected to MySQL using password authentication.")
            # Update config to use password auth since it worked
            config['use_auth_socket'] = False
        
        with connection.cursor() as cursor:
            # Drop and create database
            cursor.execute(f"DROP DATABASE IF EXISTS `{config['database']}`;")
            cursor.execute(f"""
                CREATE DATABASE `{config['database']}` 
                CHARACTER SET utf8mb4 
                COLLATE utf8mb4_unicode_ci;
            """)
            
            # Important: Always use password auth for new user in auto mode
            if args.auto or args.password_auth:
                # Drop existing user
                cursor.execute(f"DROP USER IF EXISTS '{config['user']}'@'localhost';")
                cursor.execute(f"DROP USER IF EXISTS '{config['user']}'@'%';")
                
                # Create user with password and allow connection from anywhere
                cursor.execute(f"CREATE USER '{config['user']}'@'localhost' IDENTIFIED BY '{config['password']}';")
                cursor.execute(f"CREATE USER '{config['user']}'@'%' IDENTIFIED BY '{config['password']}';")
                
                # Grant privileges
                cursor.execute(f"GRANT ALL PRIVILEGES ON `{config['database']}`.* TO '{config['user']}'@'localhost';")
                cursor.execute(f"GRANT ALL PRIVILEGES ON `{config['database']}`.* TO '{config['user']}'@'%';")
                
                config['use_auth_socket'] = False
                logger.info(f"User `{config['user']}` created successfully with password authentication.")
            else:
                # Use auth_socket if specifically requested
                cursor.execute(f"DROP USER IF EXISTS '{config['user']}'@'localhost';")
                cursor.execute(f"CREATE USER '{config['user']}'@'localhost' IDENTIFIED WITH auth_socket;")
                cursor.execute(f"GRANT ALL PRIVILEGES ON `{config['database']}`.* TO '{config['user']}'@'localhost';")
                logger.info(f"User `{config['user']}` created successfully with auth_socket.")
            
            cursor.execute("FLUSH PRIVILEGES;")
            
        return True
        
    except pymysql.Error as e:
        logger.error(f"Error setting up database: {e}")
        if connection:
            connection.close()
        return False

def update_env_file(config, env_file):
    """Update .env file with database settings"""
    if not env_file.exists():
        logger.error(f".env file not found at {env_file}.")
        return False
    
    # Read content of .env file
    with open(env_file, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Update or add database settings
    db_settings = {
        'DB_HOST': config['host'],
        'DB_PORT': str(config['port']),
        'DB_USER': config['user'],
        'DB_PASSWORD': config['password'],
        'DB_NAME': config['database'],
        'DB_CHARSET': 'utf8mb4',
        'DB_AUTH_SOCKET': str(config['use_auth_socket']).lower()
    }
    
    # Create backup of .env file
    backup_file = env_file.with_suffix('.env.bak')
    shutil.copy2(env_file, backup_file)
    logger.info(f"Created backup of .env file at {backup_file}.")
    
    # Update or add settings in .env file
    for key, value in db_settings.items():
        # Regex pattern to find and replace value
        pattern = f"^{key}=.*$"
        replacement = f"{key}={value}"
        
        # Search for existing value
        match = re.search(pattern, content, re.MULTILINE)
        
        if match:
            # If value exists, replace it
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        else:
            # If value doesn't exist, add it to database settings section
            # First check if database settings section exists
            db_section = re.search(r"# Database Settings", content)
            if db_section:
                # Add setting after section heading
                section_pos = db_section.end()
                content = content[:section_pos] + f"\n{replacement}" + content[section_pos:]
            else:
                # If section doesn't exist, add it at the end of file
                content += f"\n\n# Database Settings\n{replacement}"
    
    # Save changes to .env file
    with open(env_file, 'w', encoding='utf-8') as file:
        file.write(content)
    
    logger.info(f"Database settings updated in {env_file}.")
    return True

def run_alembic_migrations(project_root):
    """Run Alembic migrations"""
    try:
        logger.info("Starting Alembic migrations...")
        
        # Find Alembic config file
        alembic_ini = project_root / 'alembic.ini'
        if not alembic_ini.exists():
            logger.error(f"alembic.ini file not found at {alembic_ini}.")
            return False
        
        # Load Alembic config
        alembic_config = Config(alembic_ini)
        
        # Run migrations
        command.upgrade(alembic_config, "head")
        
        logger.info("Alembic migrations ran successfully.")
        return True
    except alembic_exceptions.CommandError as e:
        logger.error(f"Error running Alembic migrations: {e}")
        return False

def main():
    """Main function"""
    args = parse_arguments()
    
    # Convert .env file path to Path
    if args.env_file:
        env_file = Path(args.env_file)
    else:
        env_file = None
    
    # Load .env file and find project root
    project_root = load_env_file(env_file)
    
    if env_file is None:
        env_file = project_root / '.env'
    
    # Get MySQL settings
    mysql_config = get_mysql_config(args)
    
    # Test connection to MySQL with admin user
    logger.info("Testing connection to MySQL with admin user...")
    if not test_mysql_connection(mysql_config, admin=True):
        logger.error(f"Error connecting to MySQL with admin user {mysql_config['admin_user']}.")
        logger.error("Could not connect with either auth_socket or password authentication.")
        logger.error("Please make sure MySQL is installed and running.")
        logger.error("For auth_socket: Make sure the system user matches MySQL username.")
        logger.error("For password auth: Make sure the password is correct.")
        sys.exit(1)
    
    # Create database and user
    logger.info("Creating database and user...")
    if not create_database(mysql_config, args):
        logger.error("Error creating database and user.")
        sys.exit(1)
    
    # Update .env file
    logger.info("Updating .env file...")
    if not update_env_file(mysql_config, env_file):
        logger.error("Error updating .env file.")
        sys.exit(1)
    
    # Test connection to database with new user
    logger.info("Testing connection to database with new user...")
    if not test_mysql_connection(mysql_config, admin=False):
        logger.error(f"Error connecting to database with user {mysql_config['user']}.")
        sys.exit(1)
    
    # Run Alembic migrations
    if not args.skip_migrations:
        logger.info("Running Alembic migrations...")
        if not run_alembic_migrations(project_root):
            logger.error("Error running Alembic migrations.")
            sys.exit(1)
    
    logger.info("Database setup completed successfully.")
    print("\n✅ Database setup completed successfully!")
    print(f"Database: {mysql_config['database']}")
    print(f"User: {mysql_config['user']}")
    print(f"Authentication method: {'auth_socket' if mysql_config['use_auth_socket'] else 'password'}")
    print("\nTo run the bot, use the following command:")
    print("python src/main.py")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        sys.exit(1)