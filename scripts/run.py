#!/usr/bin/env python3
"""
Run script for Telegram Chain Store Bot
This file serves as an entry point to run the bot from the project root
"""
import asyncio
import sys
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