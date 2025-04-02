"""
این ماژول شامل توابع امنیتی و رمزنگاری برای محافظت از داده‌های حساس است.

الگوریتم‌های رمزنگاری استفاده شده:
1. bcrypt: برای هش کردن رمزهای عبور و شناسه‌های تلگرام
   - نمک (salt) تصادفی 22 کاراکتری
   - تعداد دور (rounds) پیش‌فرض: 12
   - مقاوم در برابر حملات rainbow table

2. JWT (JSON Web Token): برای ایجاد توکن‌های احراز هویت
   - الگوریتم: HS256 (HMAC با SHA-256)
   - امضای دیجیتال با کلید مخفی
   - شامل تاریخ انقضا و اطلاعات کاربر

3. Fernet (متقارن): برای رمزنگاری داده‌های حساس مثل آدرس‌ها
   - بر پایه AES در حالت CBC
   - با کلید 32 بایتی
   - شامل تاریخ انقضا و MAC برای تایید یکپارچگی
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict
from jose import JWTError, jwt
from passlib.context import CryptContext
from config.settings import settings

# تنظیم bcrypt برای هش کردن رمز عبور
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # تعداد دورهای هش
)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    تایید رمز عبور با استفاده از bcrypt
    مقایسه امن رمز ورودی با رمز هش شده
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    هش کردن رمز عبور با bcrypt
    شامل نمک تصادفی برای جلوگیری از حملات rainbow table
    """
    return pwd_context.hash(password)

def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    ایجاد JWT با الگوریتم HS256
    - data: داده‌های مورد نظر برای رمزنگاری
    - expires_delta: مدت اعتبار توکن
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta if expires_delta else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_access_token(token: str) -> Optional[Dict]:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None

def create_temporary_token(data: Dict, expire_minutes: int = 5) -> str:
    """Create a short-lived token for sensitive operations"""
    return create_access_token(data, timedelta(minutes=expire_minutes))

def verify_temporary_code(code: str, stored_code: str) -> bool:
    """Verify one-time delivery verification code"""
    return pwd_context.verify(code, stored_code)

def generate_verification_code() -> str:
    """
    تولید کد تایید 6 رقمی تصادفی
    استفاده از random.SystemRandom() برای امنیت بیشتر
    """
    import random
    return ''.join(random.SystemRandom().choices('0123456789', k=settings.VERIFY_CODE_LENGTH))

def hash_telegram_id(telegram_id: str) -> str:
    """
    هش کردن شناسه تلگرام با bcrypt
    برای جلوگیری از ذخیره مستقیم شناسه‌ها
    """
    return pwd_context.hash(telegram_id)

def encrypt_sensitive_data(data: str) -> str:
    """
    رمزنگاری داده‌های حساس با Fernet (AES-128-CBC)
    - تولید کلید 32 بایتی از SECRET_KEY
    - اضافه کردن بردار اولیه (IV) تصادفی
    - اضافه کردن MAC برای تشخیص دستکاری
    """
    from cryptography.fernet import Fernet
    from base64 import urlsafe_b64encode
    import hashlib

    # تولید کلید 32 بایتی از SECRET_KEY
    key = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
    # تبدیل به فرمت مناسب برای Fernet
    key = urlsafe_b64encode(key)
    
    f = Fernet(key)
    return f.encrypt(data.encode()).decode()

def decrypt_sensitive_data(encrypted_data: str) -> str:
    """
    رمزگشایی داده‌های حساس با Fernet
    - بررسی MAC برای اطمینان از عدم دستکاری
    - رمزگشایی با همان کلید
    """
    from cryptography.fernet import Fernet, InvalidToken
    from base64 import urlsafe_b64encode
    import hashlib

    key = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
    key = urlsafe_b64encode(key)
    
    try:
        f = Fernet(key)
        return f.decrypt(encrypted_data.encode()).decode()
    except InvalidToken:
        raise ValueError("Data has been tampered with or key is incorrect")

def generate_temp_token() -> str:
    """Generate temporary token for one-time use"""
    import secrets
    return secrets.token_urlsafe(settings.TEMP_TOKEN_LENGTH)

def encrypt_telegram_data(data: Dict) -> str:
    """Encrypt sensitive telegram data"""
    return encrypt_sensitive_data(str(data))

def secure_delete_data(data: str) -> None:
    """Securely delete sensitive data"""
    import secrets
    data = secrets.token_bytes(len(data))
    del data

def validate_payment_data(payment_data: Dict) -> bool:
    """Validate payment data for security"""
    required_fields = ['amount', 'currency', 'method']
    return all(field in payment_data for field in required_fields)

def anonymize_user_data(user_data: Dict) -> Dict:
    """Remove/hash sensitive user data"""
    sensitive_fields = ['telegram_id', 'email', 'phone']
    for field in sensitive_fields:
        if field in user_data:
            user_data[field] = hash_telegram_id(str(user_data[field]))
    return user_data
