#!/usr/bin/env python3
"""
Run script for Telegram Chain Store Bot with path adjustment
This script adds the current directory to Python's path before importing modules
"""
import os
import sys
import asyncio

# Add the current directory to Python's path
sys.path.insert(0, os.path.abspath("."))

from src.main import main

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 