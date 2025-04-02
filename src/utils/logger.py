import logging
import os
import asyncio
from datetime import datetime
import json
import traceback
from functools import wraps
from logging.handlers import RotatingFileHandler
from src.config.settings import get_settings

# Get settings
settings = get_settings()

# Create logs directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

# Configure root logger
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Create specialized loggers
USER_LOGGER = logging.getLogger('user_actions')
PRODUCT_LOGGER = logging.getLogger('product_actions')
ORDER_LOGGER = logging.getLogger('order_actions')
PAYMENT_LOGGER = logging.getLogger('payment_actions')
ADMIN_LOGGER = logging.getLogger('admin_actions')
LOCATION_LOGGER = logging.getLogger('location_actions')
ERROR_LOGGER = logging.getLogger('error_logger')
DB_LOGGER = logging.getLogger('database')
UI_LOGGER = logging.getLogger('ui_interactions')

# Configure specialized loggers
def setup_logger(logger, log_file, level=logging.INFO):
    """Configure a logger with file handler"""
    handler = RotatingFileHandler(
        f'logs/{log_file}',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        '%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(level)
    logger.propagate = False  # Don't propagate to parent logger
    return logger

# Setup all loggers
setup_logger(USER_LOGGER, 'user_actions.log')
setup_logger(PRODUCT_LOGGER, 'product_actions.log')
setup_logger(ORDER_LOGGER, 'order_actions.log')
setup_logger(PAYMENT_LOGGER, 'payment_actions.log')
setup_logger(ADMIN_LOGGER, 'admin_actions.log')
setup_logger(LOCATION_LOGGER, 'location_actions.log')
setup_logger(ERROR_LOGGER, 'errors.log', level=logging.ERROR)
setup_logger(DB_LOGGER, 'database.log')
setup_logger(UI_LOGGER, 'ui_interactions.log')

# Main application logger
APP_LOGGER = logging.getLogger('telegram_store')
setup_logger(APP_LOGGER, 'app.log')

def log_user_action(user_id, action, details=None):
    """Log user actions with details"""
    message = f"User {user_id} - {action}"
    if details:
        if isinstance(details, dict):
            details_str = json.dumps(details)
        else:
            details_str = str(details)
        message += f" - Details: {details_str}"
    USER_LOGGER.info(message)

def log_product_action(user_id, action, product_id=None, details=None):
    """Log product related actions"""
    message = f"User {user_id} - {action}"
    if product_id:
        message += f" - Product ID: {product_id}"
    if details:
        if isinstance(details, dict):
            details_str = json.dumps(details)
        else:
            details_str = str(details)
        message += f" - Details: {details_str}"
    PRODUCT_LOGGER.info(message)

def log_order_action(user_id, action, order_id=None, details=None):
    """Log order related actions"""
    message = f"User {user_id} - {action}"
    if order_id:
        message += f" - Order ID: {order_id}"
    if details:
        if isinstance(details, dict):
            details_str = json.dumps(details)
        else:
            details_str = str(details)
        message += f" - Details: {details_str}"
    ORDER_LOGGER.info(message)

def log_payment_action(user_id, action, payment_id=None, amount=None, details=None):
    """Log payment related actions"""
    message = f"User {user_id} - {action}"
    if payment_id:
        message += f" - Payment ID: {payment_id}"
    if amount:
        message += f" - Amount: {amount}"
    if details:
        if isinstance(details, dict):
            details_str = json.dumps(details)
        else:
            details_str = str(details)
        message += f" - Details: {details_str}"
    PAYMENT_LOGGER.info(message)

def log_admin_action(admin_id, action, target_id=None, details=None):
    """Log administrative actions"""
    message = f"Admin {admin_id} - {action}"
    if target_id:
        message += f" - Target ID: {target_id}"
    if details:
        if isinstance(details, dict):
            details_str = json.dumps(details)
        else:
            details_str = str(details)
        message += f" - Details: {details_str}"
    ADMIN_LOGGER.info(message)

def log_location_action(user_id, action, location_id=None, details=None):
    """Log location related actions"""
    message = f"User {user_id} - {action}"
    if location_id:
        message += f" - Location ID: {location_id}"
    if details:
        if isinstance(details, dict):
            details_str = json.dumps(details)
        else:
            details_str = str(details)
        message += f" - Details: {details_str}"
    LOCATION_LOGGER.info(message)

def log_error(error_msg, error=None, user_id=None):
    """Log detailed error information"""
    message = f"ERROR: {error_msg}"
    if user_id:
        message += f" - User ID: {user_id}"
    if error:
        message += f" - Exception: {str(error)}"
        if hasattr(error, '__traceback__'):
            tb_str = ''.join(traceback.format_tb(error.__traceback__))
            message += f"\nTraceback: {tb_str}"
    ERROR_LOGGER.error(message)
    APP_LOGGER.error(f"Error occurred: {error_msg}")

def log_db_operation(operation, table, record_id=None, details=None):
    """Log database operations"""
    message = f"DB {operation} - Table: {table}"
    if record_id:
        message += f" - Record ID: {record_id}"
    if details:
        if isinstance(details, dict):
            details_str = json.dumps(details)
        else:
            details_str = str(details)
        message += f" - Details: {details_str}"
    DB_LOGGER.info(message)

def log_ui_event(user_id, event_type, component=None, details=None):
    """Log UI interactions like button clicks, menu selections etc."""
    message = f"User {user_id} - {event_type}"
    if component:
        message += f" - Component: {component}"
    if details:
        if isinstance(details, dict):
            details_str = json.dumps(details)
        else:
            details_str = str(details)
        message += f" - Details: {details_str}"
    UI_LOGGER.info(message)

# Decorator for logging function execution with timing
def log_function_execution(logger=APP_LOGGER):
    """Decorator to log function execution with timing"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = datetime.now()
            try:
                result = await func(*args, **kwargs)
                execution_time = (datetime.now() - start_time).total_seconds()
                logger.info(f"Function {func.__name__} executed in {execution_time:.4f}s")
                return result
            except Exception as e:
                execution_time = (datetime.now() - start_time).total_seconds()
                logger.error(f"Function {func.__name__} failed after {execution_time:.4f}s - Error: {str(e)}")
                log_error(f"Error in {func.__name__}", e)
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = datetime.now()
            try:
                result = func(*args, **kwargs)
                execution_time = (datetime.now() - start_time).total_seconds()
                logger.info(f"Function {func.__name__} executed in {execution_time:.4f}s")
                return result
            except Exception as e:
                execution_time = (datetime.now() - start_time).total_seconds()
                logger.error(f"Function {func.__name__} failed after {execution_time:.4f}s - Error: {str(e)}")
                log_error(f"Error in {func.__name__}", e)
                raise
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator 