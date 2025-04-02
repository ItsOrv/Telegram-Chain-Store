from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from src.core.exceptions import AuthenticationError, AuthorizationError
from src.core.validators import Validators
from src.config.settings import get_settings

settings = get_settings()

class Auth:
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> Dict[str, Any]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token has expired")
        except jwt.JWTError:
            raise AuthenticationError("Invalid token")

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt"""
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def validate_user_data(user_data: Dict[str, Any]) -> bool:
        """Validate user registration data"""
        required_fields = ['email', 'password', 'phone']
        for field in required_fields:
            if field not in user_data:
                raise ValidationError(f"Missing required field: {field}")

        Validators.validate_email(user_data['email'])
        Validators.validate_password(user_data['password'])
        Validators.validate_phone(user_data['phone'])
        return True

    @staticmethod
    def check_permissions(user_id: int, required_role: str) -> bool:
        """Check if user has required role"""
        from src.core.models import User
        user = User.get_by_id(user_id)
        if not user:
            raise AuthenticationError("User not found")
        if user.role != required_role:
            raise AuthorizationError(f"User does not have required role: {required_role}")
        return True

    @staticmethod
    def create_session(user_id: int) -> Dict[str, Any]:
        """Create user session"""
        session_data = {
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat()
        }
        return session_data

    @staticmethod
    def update_session(session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update session last activity"""
        session_data["last_activity"] = datetime.utcnow().isoformat()
        return session_data

    @staticmethod
    def is_session_valid(session_data: Dict[str, Any], max_age_hours: int = 24) -> bool:
        """Check if session is still valid"""
        last_activity = datetime.fromisoformat(session_data["last_activity"])
        age = datetime.utcnow() - last_activity
        return age.total_seconds() < (max_age_hours * 3600)

    @staticmethod
    def generate_reset_token(email: str) -> str:
        """Generate password reset token"""
        data = {
            "email": email,
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        return jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @staticmethod
    def verify_reset_token(token: str) -> str:
        """Verify password reset token"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload["email"]
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Reset token has expired")
        except jwt.JWTError:
            raise AuthenticationError("Invalid reset token")
