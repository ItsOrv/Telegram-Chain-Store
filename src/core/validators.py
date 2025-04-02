from typing import Dict, Any, Optional
from datetime import datetime
import re
from src.core.exceptions import ValidationError

class Validators:
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            raise ValidationError("Invalid email format")
        return True

    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number format"""
        pattern = r'^\+?[1-9]\d{1,14}$'
        if not re.match(pattern, phone):
            raise ValidationError("Invalid phone number format")
        return True

    @staticmethod
    def validate_password(password: str) -> bool:
        """Validate password strength"""
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long")
        if not re.search(r'[A-Z]', password):
            raise ValidationError("Password must contain at least one uppercase letter")
        if not re.search(r'[a-z]', password):
            raise ValidationError("Password must contain at least one lowercase letter")
        if not re.search(r'\d', password):
            raise ValidationError("Password must contain at least one number")
        return True

    @staticmethod
    def validate_amount(amount: float) -> bool:
        """Validate payment amount"""
        if amount <= 0:
            raise ValidationError("Amount must be greater than 0")
        if amount > 1000000:  # Maximum amount limit
            raise ValidationError("Amount exceeds maximum limit")
        return True

    @staticmethod
    def validate_date(date_str: str) -> bool:
        """Validate date format"""
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            raise ValidationError("Invalid date format. Use YYYY-MM-DD")

    @staticmethod
    def validate_address(address: Dict[str, Any]) -> bool:
        """Validate address data"""
        required_fields = ['street', 'city', 'province', 'postal_code']
        for field in required_fields:
            if field not in address or not address[field]:
                raise ValidationError(f"Missing required field: {field}")
        
        if not re.match(r'^\d{10}$', address['postal_code']):
            raise ValidationError("Invalid postal code format")
        return True

    @staticmethod
    def validate_product_data(product: Dict[str, Any]) -> bool:
        """Validate product data"""
        required_fields = ['name', 'description', 'price', 'category_id']
        for field in required_fields:
            if field not in product or not product[field]:
                raise ValidationError(f"Missing required field: {field}")
        
        if product['price'] <= 0:
            raise ValidationError("Price must be greater than 0")
        return True

    @staticmethod
    def validate_order_data(order: Dict[str, Any]) -> bool:
        """Validate order data"""
        required_fields = ['user_id', 'items', 'total_amount']
        for field in required_fields:
            if field not in order:
                raise ValidationError(f"Missing required field: {field}")
        
        if not order['items']:
            raise ValidationError("Order must contain at least one item")
        
        if order['total_amount'] <= 0:
            raise ValidationError("Total amount must be greater than 0")
        return True

    @staticmethod
    def validate_crypto_address(address: str) -> bool:
        """Validate cryptocurrency address"""
        if not address or len(address) < 26 or len(address) > 35:
            raise ValidationError("Invalid cryptocurrency address")
        return True

    @staticmethod
    def validate_transaction_hash(tx_hash: str) -> bool:
        """Validate transaction hash"""
        if not tx_hash or len(tx_hash) != 64:
            raise ValidationError("Invalid transaction hash")
        return True
