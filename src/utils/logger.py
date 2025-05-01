import logging
import sys
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Union
from functools import wraps
import traceback
import time
import inspect
from logging.handlers import RotatingFileHandler

# Create logs directory if it doesn't exist
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Configure basic logging format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

def setup_logger(name: str, log_level: Optional[str] = None) -> logging.Logger:
    """
    Set up a logger with file and console handlers
    
    Args:
        name: Name of the logger
        log_level: Log level override (defaults to environment LOG_LEVEL)
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Set log level from parameter or environment
    if log_level:
        level = getattr(logging, log_level.upper())
    else:
        level = getattr(logging, LOG_LEVEL)
    logger.setLevel(level)
    
    # Clear existing handlers if any
    if logger.hasHandlers():
        logger.handlers.clear()
    
    # Create file handler
    file_handler = RotatingFileHandler(
        f"logs/{name}.log", 
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5
    )
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(file_handler)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(console_handler)
    
    return logger

# Application-wide logger
APP_LOGGER = setup_logger("app")

def log_to_file(data: Dict[str, Any], file_name: str) -> None:
    """
    Log structured data to a JSON file
    
    Args:
        data (Dict[str, Any]): Data to log
        file_name (str): Name of the log file
    """
    try:
        log_file = log_dir / file_name
        
        # Add timestamp if not present
        if 'timestamp' not in data:
            data['timestamp'] = datetime.now().isoformat()
            
        # Append to file
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(data) + '\n')
    except Exception as e:
        APP_LOGGER.error(f"Failed to write log to file {file_name}: {e}")

def log_error(message: str, exception: Optional[Exception] = None, user_id: Optional[int] = None) -> None:
    """
    Log an error with exception details
    
    Args:
        message: Error message
        exception: Exception object
        user_id: Telegram user ID (if available)
    """
    error_logger = logging.getLogger("error")
    
    # Create error message
    error_text = f"{message}"
    if user_id:
        error_text += f" (User ID: {user_id})"
    
    # Add exception details if provided
    if exception:
        error_text += f"\nException: {str(exception)}"
        error_text += f"\nTraceback: {traceback.format_exc()}"
    
    # Log the error
    error_logger.error(error_text)

def log_user_action(user_id: Union[int, str], action: str, details: Optional[Dict[str, Any]] = None) -> None:
    """
    Log a user action
    
    Args:
        user_id (int or str): User ID
        action (str): Action name
        details (Dict[str, Any], optional): Additional details
    """
    try:
        user_data = {
            "user_id": user_id,
            "action": action,
            "timestamp": datetime.now().isoformat()
        }
        
        if details:
            user_data["details"] = details
            
        # Log to user actions file
        log_to_file(user_data, "user_actions.log")
        
        # Log to app logger
        APP_LOGGER.info(f"User {user_id} performed action: {action}")
        
    except Exception as e:
        log_error("Failed to log user action", e)

def log_function_execution(include_args: bool = False):
    """
    Decorator to log function execution time and result
    
    Args:
        include_args (bool): Whether to include function arguments in the log
        
    Returns:
        Function decorator
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            func_name = func.__name__
            
            # Log function call
            log_message = f"Executing {func_name}"
            if include_args:
                log_message += f" with args={args[1:] if len(args) > 1 else ''}, kwargs={kwargs}"
            APP_LOGGER.info(log_message)
            
            try:
                # Execute function
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # Log successful completion
                APP_LOGGER.info(f"Completed {func_name} in {execution_time:.4f}s")
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                APP_LOGGER.error(f"Failed {func_name} after {execution_time:.4f}s: {str(e)}")
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            func_name = func.__name__
            
            # Log function call
            log_message = f"Executing {func_name}"
            if include_args:
                log_message += f" with args={args[1:] if len(args) > 1 else ''}, kwargs={kwargs}"
            APP_LOGGER.info(log_message)
            
            try:
                # Execute function
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # Log successful completion
                APP_LOGGER.info(f"Completed {func_name} in {execution_time:.4f}s")
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                APP_LOGGER.error(f"Failed {func_name} after {execution_time:.4f}s: {str(e)}")
                raise
        
        # Return the appropriate wrapper based on function type
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator 

def log_ui_event(user_id: Union[int, str], action: str, event_type: str, details: Optional[Dict[str, Any]] = None) -> None:
    """
    Log a UI event (button click, menu selection, etc.)
    
    Args:
        user_id (int or str): User ID
        action (str): Action name
        event_type (str): Event type
        details (Dict[str, Any], optional): Additional details
    """
    try:
        event_data = {
            "user_id": user_id,
            "action": action,
            "event_type": event_type,
            "timestamp": datetime.now().isoformat()
        }
        
        if details:
            event_data["details"] = details
            
        # Log to UI events file
        log_to_file(event_data, "ui_events.log")
        
    except Exception as e:
        log_error("Failed to log UI event", e)

# Additional specialized logging functions

def log_product_action(user_id: Union[int, str], product_id: int, action: str, details: Optional[Dict[str, Any]] = None) -> None:
    """
    Log a product-related action
    
    Args:
        user_id: User ID
        product_id: Product ID
        action: Action name (e.g., 'view', 'add', 'update', 'delete')
        details: Additional details
    """
    try:
        product_data = {
            "user_id": user_id,
            "product_id": product_id,
            "action": action,
            "timestamp": datetime.now().isoformat()
        }
        
        if details:
            product_data["details"] = details
            
        # Log to product actions file
        log_to_file(product_data, "product_actions.log")
        
        # Log to app logger
        APP_LOGGER.info(f"User {user_id} performed product action: {action} on product {product_id}")
        
    except Exception as e:
        log_error("Failed to log product action", e)

def log_order_action(user_id: Union[int, str], order_id: int, action: str, details: Optional[Dict[str, Any]] = None) -> None:
    """
    Log an order-related action
    
    Args:
        user_id: User ID
        order_id: Order ID
        action: Action name (e.g., 'create', 'update', 'cancel', 'complete')
        details: Additional details
    """
    try:
        order_data = {
            "user_id": user_id,
            "order_id": order_id,
            "action": action,
            "timestamp": datetime.now().isoformat()
        }
        
        if details:
            order_data["details"] = details
            
        # Log to order actions file
        log_to_file(order_data, "order_actions.log")
        
        # Log to app logger
        APP_LOGGER.info(f"User {user_id} performed order action: {action} on order {order_id}")
        
    except Exception as e:
        log_error("Failed to log order action", e)

def log_payment_action(user_id: Union[int, str], payment_id: int, action: str, amount: Optional[float] = None, details: Optional[Dict[str, Any]] = None) -> None:
    """
    Log a payment-related action
    
    Args:
        user_id: User ID
        payment_id: Payment ID
        action: Action name (e.g., 'create', 'verify', 'approve', 'reject')
        amount: Payment amount
        details: Additional details
    """
    try:
        payment_data = {
            "user_id": user_id,
            "payment_id": payment_id,
            "action": action,
            "timestamp": datetime.now().isoformat()
        }
        
        if amount is not None:
            payment_data["amount"] = amount
            
        if details:
            payment_data["details"] = details
            
        # Log to payment actions file
        log_to_file(payment_data, "payment_actions.log")
        
        # Log to app logger
        APP_LOGGER.info(f"User {user_id} performed payment action: {action} on payment {payment_id}")
        
    except Exception as e:
        log_error("Failed to log payment action", e)

def log_admin_action(admin_id: Union[int, str], action: str, target_type: Optional[str] = None, target_id: Optional[Union[int, str]] = None, details: Optional[Dict[str, Any]] = None) -> None:
    """
    Log an admin action
    
    Args:
        admin_id: Admin user ID
        action: Action name
        target_type: Type of target (e.g., 'user', 'product', 'order')
        target_id: ID of the target
        details: Additional details
    """
    try:
        admin_data = {
            "admin_id": admin_id,
            "action": action,
            "timestamp": datetime.now().isoformat()
        }
        
        if target_type:
            admin_data["target_type"] = target_type
            
        if target_id:
            admin_data["target_id"] = target_id
            
        if details:
            admin_data["details"] = details
            
        # Log to admin actions file
        log_to_file(admin_data, "admin_actions.log")
        
        # Log to app logger
        log_msg = f"Admin {admin_id} performed action: {action}"
        if target_type and target_id:
            log_msg += f" on {target_type} {target_id}"
        APP_LOGGER.info(log_msg)
        
    except Exception as e:
        log_error("Failed to log admin action", e)

def log_location_action(user_id: Union[int, str], location_id: int, action: str, details: Optional[Dict[str, Any]] = None) -> None:
    """
    Log a location-related action
    
    Args:
        user_id: User ID
        location_id: Location ID
        action: Action name (e.g., 'add', 'update', 'delete')
        details: Additional details
    """
    try:
        location_data = {
            "user_id": user_id,
            "location_id": location_id,
            "action": action,
            "timestamp": datetime.now().isoformat()
        }
        
        if details:
            location_data["details"] = details
            
        # Log to location actions file
        log_to_file(location_data, "location_actions.log")
        
        # Log to app logger
        APP_LOGGER.info(f"User {user_id} performed location action: {action} on location {location_id}")
        
    except Exception as e:
        log_error("Failed to log location action", e)

def log_db_operation(operation: str, table: str, record_id: Optional[Union[int, str]] = None, details: Optional[Dict[str, Any]] = None, user_id: Optional[Union[int, str]] = None) -> None:
    """
    Log a database operation
    
    Args:
        operation: Database operation (e.g., 'insert', 'update', 'delete', 'query')
        table: Database table
        record_id: Record ID (if applicable)
        details: Additional details
        user_id: User ID (if applicable)
    """
    try:
        db_data = {
            "operation": operation,
            "table": table,
            "timestamp": datetime.now().isoformat()
        }
        
        if record_id is not None:
            db_data["record_id"] = record_id
            
        if user_id is not None:
            db_data["user_id"] = user_id
            
        if details:
            db_data["details"] = details
            
        # Log to database operations file
        log_to_file(db_data, "db_operations.log")
        
        # Log to app logger (for non-query operations)
        if operation != 'query':
            log_msg = f"DB {operation} on {table}"
            if record_id is not None:
                log_msg += f" ID {record_id}"
            APP_LOGGER.debug(log_msg)
        
    except Exception as e:
        log_error("Failed to log database operation", e) 