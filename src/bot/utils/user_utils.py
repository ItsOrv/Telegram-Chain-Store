from sqlalchemy.orm import Session
from typing import Optional

from src.core.models import User, UserRole
from src.core.database import SessionLocal

def get_user_role(db: Session, user_id: int) -> Optional[UserRole]:
    """Get the role of a user by their Telegram ID"""
    user = db.query(User).filter(User.telegram_id == str(user_id)).first()
    return user.role if user else None

def get_user_by_telegram_id(telegram_id: int) -> Optional[User]:
    """Get user by Telegram ID"""
    with SessionLocal() as db:
        return db.query(User).filter(User.telegram_id == str(telegram_id)).first()

# Add other utility functions as needed 