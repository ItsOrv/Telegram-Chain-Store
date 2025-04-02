#!/usr/bin/env python
"""
Secure Environment Setup Script for Telegram Chain Store Bot

This script helps set up a secure environment for the Telegram Chain Store Bot by:
1. Generating a secure .env file with proper credentials
2. Creating a strong SECRET_KEY
3. Setting up secure database credentials

Usage:
    python setup_secure_environment.py
"""

import os
import secrets
import string
import hashlib
import base64
import getpass
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent
ENV_FILE = PROJECT_ROOT / ".env"
ENV_EXAMPLE_FILE = PROJECT_ROOT / ".env.example"


def generate_secure_key(length=32, method="urlsafe"):
    """Generate a cryptographically secure key"""
    if method == "urlsafe":
        return secrets.token_urlsafe(length)
    elif method == "hex":
        return secrets.token_hex(length)
    elif method == "base64":
        return base64.b64encode(secrets.token_bytes(length)).decode()
    elif method == "sha256":
        base_key = secrets.token_bytes(length)
        return hashlib.sha256(base_key).hexdigest()
    else:
        raise ValueError(f"Unknown method: {method}")


def generate_strong_password(length=16):
    """Generate a strong password with mixed characters"""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    while True:
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        # Check if password has at least one of each character type
        if (any(c.islower() for c in password) and
                any(c.isupper() for c in password) and
                any(c.isdigit() for c in password) and
                any(c in string.punctuation for c in password)):
            return password


def load_env_example():
    """Load the .env.example file as a template"""
    if not ENV_EXAMPLE_FILE.exists():
        print(f"Error: {ENV_EXAMPLE_FILE} not found")
        return {}

    env_vars = {}
    with open(ENV_EXAMPLE_FILE, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, value = line.split('=', 1)
                env_vars[key] = value
    return env_vars


def create_secure_env_file():
    """Create a secure .env file with proper credentials"""
    if ENV_FILE.exists():
        overwrite = input(f"{ENV_FILE} already exists. Overwrite? (y/n): ").lower()
        if overwrite != 'y':
            print("Operation cancelled.")
            return

    # Load template from .env.example
    env_vars = load_env_example()
    if not env_vars:
        print("Could not load template from .env.example")
        return

    # Generate secure values
    env_vars['SECRET_KEY'] = generate_secure_key(32, "urlsafe")
    env_vars['DB_PASSWORD'] = generate_strong_password(16)
    env_vars['REDIS_PASSWORD'] = generate_strong_password(16)

    # Ask for Telegram credentials
    print("\nPlease enter your Telegram API credentials:")
    env_vars['API_ID'] = input("API_ID: ")
    env_vars['API_HASH'] = input("API_HASH: ")
    env_vars['BOT_TOKEN'] = input("BOT_TOKEN: ")
    env_vars['BOT_USERNAME'] = input("BOT_USERNAME (without @): ")
    env_vars['HEAD_ADMIN_ID'] = input("HEAD_ADMIN_ID (your Telegram ID): ")
    env_vars['SUPPORT_USERNAME'] = input("SUPPORT_USERNAME (with @): ")
    env_vars['SUPPORT_ID'] = input("SUPPORT_ID: ")

    # Ask for crypto wallet address
    env_vars['CRYPTO_WALLET_ADDRESS'] = input("\nCRYPTO_WALLET_ADDRESS: ")

    # Write to .env file
    with open(ENV_FILE, 'w') as f:
        for section in ['App Settings', 'Telegram Settings', 'Database Settings', 
                       'Redis Settings', 'Security Settings', 'Rate Limiting',
                       'Crypto Settings', 'Address Settings', 'Notification Settings']:
            f.write(f"# {section}\n")
            
            # Write variables for this section
            for key, value in env_vars.items():
                if section == 'App Settings' and key in ['DEBUG', 'LOG_LEVEL']:
                    f.write(f"{key}={value}\n")
                elif section == 'Telegram Settings' and key in ['API_ID', 'API_HASH', 'BOT_TOKEN', 'BOT_USERNAME', 
                                                              'HEAD_ADMIN_ID', 'SUPPORT_USERNAME', 'SUPPORT_ID',
                                                              'PAYMENT_GATEWAY_TOKEN']:
                    f.write(f"{key}={value}\n")
                elif section == 'Database Settings' and key in ['DB_HOST', 'DB_PORT', 'DB_USER', 'DB_PASSWORD', 'DB_NAME']:
                    f.write(f"{key}={value}\n")
                elif section == 'Redis Settings' and key in ['REDIS_HOST', 'REDIS_PORT', 'REDIS_DB', 'REDIS_PASSWORD', 'REDIS_SSL']:
                    f.write(f"{key}={value}\n")
                elif section == 'Security Settings' and key in ['SECRET_KEY', 'PASSWORD_MIN_LENGTH', 'TOKEN_EXPIRE_MINUTES']:
                    f.write(f"{key}={value}\n")
                elif section == 'Rate Limiting' and key in ['RATE_LIMIT_REQUESTS', 'RATE_LIMIT_WINDOW']:
                    f.write(f"{key}={value}\n")
                elif section == 'Crypto Settings' and key in ['CRYPTO_WALLET_ADDRESS', 'CRYPTO_NETWORK', 'CRYPTO_PAYMENT_TIMEOUT', 'CRYPTO_MIN_AMOUNT']:
                    f.write(f"{key}={value}\n")
                elif section == 'Address Settings' and key in ['MAX_ADDRESSES_PER_CITY', 'ADDRESS_EXPIRY_HOURS']:
                    f.write(f"{key}={value}\n")
                elif section == 'Notification Settings' and key in ['ENABLE_NOTIFICATIONS', 'NOTIFICATION_DELAY']:
                    f.write(f"{key}={value}\n")
            
            f.write("\n")

    print(f"\nSecure .env file created at {ENV_FILE}")
    print("\nIMPORTANT: Add .env to your .gitignore file to prevent committing sensitive information!")


def update_gitignore():
    """Update .gitignore to include .env file"""
    gitignore_file = PROJECT_ROOT / ".gitignore"
    env_entry = ".env"

    # Check if .gitignore exists
    if not gitignore_file.exists():
        with open(gitignore_file, 'w') as f:
            f.write(f"{env_entry}\n")
        print(f"Created .gitignore file with {env_entry} entry")
        return

    # Check if .env is already in .gitignore
    with open(gitignore_file, 'r') as f:
        content = f.read()

    if env_entry in content.split('\n'):
        print(f"{env_entry} is already in .gitignore")
        return

    # Add .env to .gitignore
    with open(gitignore_file, 'a') as f:
        f.write(f"\n{env_entry}\n")

    print(f"Added {env_entry} to .gitignore")


def main():
    """Main function"""
    print("=== Telegram Chain Store Bot - Secure Environment Setup ===")
    print("This script will help you set up a secure environment for the bot.")
    print("It will generate secure credentials and create a .env file.")
    print("\nWARNING: This will overwrite your existing .env file if you confirm.")
    print("Make sure to backup any important credentials before proceeding.")

    proceed = input("\nDo you want to proceed? (y/n): ").lower()
    if proceed != 'y':
        print("Setup cancelled.")
        return

    create_secure_env_file()
    update_gitignore()

    print("\n=== Setup Complete ===")
    print("You can now start the bot with secure credentials.")


if __name__ == "__main__":
    main()