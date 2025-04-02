import os
import logging
import sys
import json
from datetime import datetime

# Create logs directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')
    print("Created logs directory")

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler('logs/test_bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger('test_bot')

class TestBot:
    def __init__(self):
        self.logger = logger
        self.logger.info("Initializing TestBot")
        
    def log_user_action(self, user_id, action, details=None):
        """Log user actions with details"""
        message = f"User {user_id} - {action}"
        if details:
            if isinstance(details, dict):
                details_str = json.dumps(details)
            else:
                details_str = str(details)
            message += f" - Details: {details_str}"
        self.logger.info(message)
        
    def simulate_user_interaction(self):
        """Simulate user interactions with the bot"""
        self.logger.info("Starting user interaction simulation")
        
        # Simulate user registration
        user_id = 123456789
        self.log_user_action(user_id, "REGISTRATION", {"username": "test_user", "timestamp": datetime.now().isoformat()})
        
        # Simulate button click
        self.log_user_action(user_id, "BUTTON_CLICK", {"button": "start_shopping", "timestamp": datetime.now().isoformat()})
        
        # Simulate product view
        self.log_user_action(user_id, "VIEW_PRODUCT", {"product_id": 42, "product_name": "Test Product", "timestamp": datetime.now().isoformat()})
        
        # Simulate adding to cart
        self.log_user_action(user_id, "ADD_TO_CART", {"product_id": 42, "quantity": 2, "timestamp": datetime.now().isoformat()})
        
        # Simulate checkout
        self.log_user_action(user_id, "CHECKOUT", {"cart_total": 100, "payment_method": "crypto", "timestamp": datetime.now().isoformat()})
        
        self.logger.info("User interaction simulation completed")

if __name__ == "__main__":
    print("Starting TestBot...")
    bot = TestBot()
    bot.simulate_user_interaction()
    print("TestBot simulation completed. Check logs/test_bot.log for output.") 