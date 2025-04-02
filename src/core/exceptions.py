class BaseError(Exception):
    """Base exception class for all custom exceptions"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class ValidationError(BaseError):
    """Raised when data validation fails"""
    pass

class DatabaseError(BaseError):
    """Raised when database operations fail"""
    pass

class AuthenticationError(BaseError):
    """Raised when authentication fails"""
    pass

class AuthorizationError(BaseError):
    """Raised when user is not authorized to perform an action"""
    pass

class PaymentError(BaseError):
    """Raised when payment operations fail"""
    pass

class OrderError(BaseError):
    """Raised when order operations fail"""
    pass

class ProductError(BaseError):
    """Raised when product operations fail"""
    pass

class DeliveryError(BaseError):
    """Raised when delivery operations fail"""
    pass

class NotificationError(BaseError):
    """Raised when notification operations fail"""
    pass

class CryptoError(BaseError):
    """Raised when cryptocurrency operations fail"""
    pass

class TransactionError(BaseError):
    """Raised when transaction operations fail"""
    pass

class RateLimitError(BaseError):
    """Raised when rate limit is exceeded"""
    pass

class ConfigurationError(BaseError):
    """Raised when configuration is invalid"""
    pass

class NetworkError(BaseError):
    """Raised when network operations fail"""
    pass

class CacheError(BaseError):
    """Raised when cache operations fail"""
    pass

class LoggingError(BaseError):
    """Raised when logging operations fail"""
    pass

class BackupError(BaseError):
    """Raised when backup operations fail"""
    pass

class ReportError(BaseError):
    """Raised when report generation fails"""
    pass
