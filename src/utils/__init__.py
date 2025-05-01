# Import the logger module to make it available application-wide
from src.utils.logger import (
    APP_LOGGER,
    log_user_action,
    log_product_action,
    log_order_action,
    log_payment_action,
    log_admin_action,
    log_location_action,
    log_error,
    log_db_operation,
    log_ui_event,
    log_function_execution,
    setup_logger,
    log_to_file
) 