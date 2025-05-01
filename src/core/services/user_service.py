from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_
from src.core.models.user import User, UserRole, UserStatus
from src.core.models.base import BaseUser
from src.core.services.base_service import BaseService
from datetime import datetime
from src.utils.logger import log_error, setup_logger

# Initialize logger
logger = setup_logger("user_service")

class UserService(BaseService[User]):
    """
    Service for managing users
    """
    
    def __init__(self, db_session: Session):
        """
        Initialize the user service
        
        Args:
            db_session: SQLAlchemy database session
        """
        super().__init__(db_session, User)
    
    def get_by_telegram_id(self, telegram_id: int) -> Optional[BaseUser]:
        """
        Get a user by Telegram ID
        
        Args:
            telegram_id: Telegram user ID
            
        Returns:
            User if found, None otherwise
        """
        try:
            user = self.db.query(User).filter(User.telegram_id == telegram_id).first()
            if user:
                return self._to_base_user(user)
            return None
        except Exception as e:
            log_error(f"Error getting user by Telegram ID {telegram_id}", e)
            return None
    
    def _to_base_user(self, db_user: User) -> BaseUser:
        """Convert database model to base user model"""
        return BaseUser(
            id=db_user.id,
            telegram_id=db_user.telegram_id,
            first_name=db_user.first_name,
            last_name=db_user.last_name,
            username=db_user.username,
            phone_number=db_user.phone_number,
            email=db_user.email,
            role=db_user.role.value if db_user.role else "BUYER",
            status=db_user.status.value if db_user.status else "ACTIVE",
            balance=db_user.balance,
            is_verified=db_user.is_verified,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at,
            last_login=db_user.last_login,
            last_activity=db_user.last_activity,
            language=db_user.language,
            timezone=db_user.timezone
        )
    
    def _from_base_user(self, base_user: BaseUser) -> User:
        """Convert base user model to database model"""
        role = UserRole(base_user.role) if base_user.role else UserRole.BUYER
        status = UserStatus(base_user.status) if base_user.status else UserStatus.ACTIVE
        
        user = User(
            id=base_user.id,
            telegram_id=base_user.telegram_id,
            first_name=base_user.first_name,
            last_name=base_user.last_name,
            username=base_user.username,
            phone_number=base_user.phone_number,
            email=base_user.email,
            role=role,
            status=status,
            balance=base_user.balance,
            is_verified=base_user.is_verified,
            created_at=base_user.created_at,
            updated_at=base_user.updated_at,
            last_login=base_user.last_login,
            last_activity=base_user.last_activity,
            language=base_user.language,
            timezone=base_user.timezone
        )
        
        return user
    
    def create_user(self, user_data: Dict[str, Any]) -> Optional[BaseUser]:
        """
        Create a new user
        
        Args:
            user_data: Dictionary containing user data
            
        Returns:
            Created user if successful, None otherwise
        """
        try:
            # Check if user already exists
            existing_user = self.get_by_telegram_id(user_data["telegram_id"])
            if existing_user:
                return existing_user
            
            # If role is provided as string, convert to enum
            if "role" in user_data and isinstance(user_data["role"], str):
                user_data["role"] = UserRole(user_data["role"])
                
            # If status is provided as string, convert to enum
            if "status" in user_data and isinstance(user_data["status"], str):
                user_data["status"] = UserStatus(user_data["status"])
            
            # Create user in database
            user = User(**user_data)
            
            # Add user to database
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"Created new user with Telegram ID {user_data['telegram_id']}")
            return self._to_base_user(user)
        except Exception as e:
            self.db.rollback()
            log_error(f"Error creating user with data {user_data}", e)
            return None
    
    def create_admin_user(self, telegram_id: int, username: Optional[str] = None, first_name: str = "Admin") -> Optional[BaseUser]:
        """
        Create a new admin user
        
        Args:
            telegram_id: Telegram user ID
            username: Telegram username
            first_name: First name
            
        Returns:
            Created admin user if successful, None otherwise
        """
        return self.create_user({
            "telegram_id": telegram_id, 
            "username": username, 
            "first_name": first_name,
            "role": UserRole.ADMIN
        })
    
    def create_seller(self, telegram_id: int, username: Optional[str] = None, first_name: str = "Seller") -> Optional[BaseUser]:
        """
        Create a new seller
        
        Args:
            telegram_id: Telegram user ID
            username: Telegram username
            first_name: First name
            
        Returns:
            Created seller if successful, None otherwise
        """
        return self.create_user({
            "telegram_id": telegram_id, 
            "username": username, 
            "first_name": first_name,
            "role": UserRole.SELLER
        })
    
    def create_cardholder(self, telegram_id: int, username: Optional[str] = None, first_name: str = "Cardholder") -> Optional[BaseUser]:
        """
        Create a new cardholder (payment representative)
        
        Args:
            telegram_id: Telegram user ID
            username: Telegram username
            first_name: First name
            
        Returns:
            Created cardholder if successful, None otherwise
        """
        return self.create_user({
            "telegram_id": telegram_id, 
            "username": username, 
            "first_name": first_name,
            "role": UserRole.CARDHOLDER
        })
    
    def ban_user(self, user_id: int) -> bool:
        """
        Ban a user
        
        Args:
            user_id: User ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            user.status = UserStatus.BANNED
            self.db.commit()
            logger.info(f"Banned user {user_id}")
            return True
        except Exception as e:
            self.db.rollback()
            log_error(f"Error banning user {user_id}", e)
            return False
    
    def change_role(self, user_id: int, new_role: UserRole) -> bool:
        """
        Change a user's role
        
        Args:
            user_id: User ID
            new_role: New role
            
        Returns:
            True if successful, False otherwise
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            user.role = new_role
            self.db.commit()
            logger.info(f"Changed user {user_id} role to {new_role}")
            return True
        except Exception as e:
            self.db.rollback()
            log_error(f"Error changing user {user_id} role", e)
            return False
    
    def update_last_login(self, user_id: int) -> bool:
        """
        Update a user's last login time
        
        Args:
            user_id: User ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            user.last_login = datetime.utcnow()
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            log_error(f"Error updating user {user_id} last login", e)
            return False
    
    def search_users(self, query: str, skip: int = 0, limit: int = 20) -> List[BaseUser]:
        """
        Search for users by username or ID
        
        Args:
            query: Search query
            skip: Number of users to skip
            limit: Maximum number of users to return
            
        Returns:
            List of matching users
        """
        try:
            # Try to parse the query as an ID
            try:
                user_id = int(query)
                id_condition = User.id == user_id
                telegram_id_condition = User.telegram_id == user_id
            except (ValueError, TypeError):
                id_condition = False
                telegram_id_condition = False
            
            # Search by username or ID
            users = self.db.query(User).filter(
                or_(
                    User.username.ilike(f"%{query}%"),
                    id_condition,
                    telegram_id_condition
                )
            ).offset(skip).limit(limit).all()
            
            return [self._to_base_user(user) for user in users]
        except Exception as e:
            log_error(f"Error searching users with query {query}", e)
            return []
    
    def get_users_by_role(self, role: UserRole, skip: int = 0, limit: int = 100) -> List[BaseUser]:
        """
        Get users by role
        
        Args:
            role: User role
            skip: Number of users to skip
            limit: Maximum number of users to return
            
        Returns:
            List of users with the specified role
        """
        try:
            users = self.db.query(User).filter(User.role == role).offset(skip).limit(limit).all()
            return [self._to_base_user(user) for user in users]
        except Exception as e:
            log_error(f"Error getting users by role {role}", e)
            return []
    
    def add_balance(self, user_id: int, amount: float) -> bool:
        """
        Add balance to user account
        
        Args:
            user_id: User ID
            amount: Amount to add
            
        Returns:
            True if successful, False otherwise
        """
        if amount <= 0:
            return False
            
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
                
            user.balance += amount
            self.db.commit()
            logger.info(f"Added {amount} to user {user_id} balance")
            return True
        except Exception as e:
            self.db.rollback()
            log_error(f"Error adding balance to user {user_id}", e)
            return False
    
    def deduct_balance(self, user_id: int, amount: float) -> bool:
        """
        Deduct amount from a user's balance
        
        Args:
            user_id: User ID
            amount: Amount to deduct
            
        Returns:
            True if successful, False otherwise
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            if user.balance < amount:
                logger.warning(f"Insufficient balance for user {user_id} (current: {user.balance}, needed: {amount})")
                return False
            
            user.balance -= amount
            self.db.commit()
            logger.info(f"Deducted {amount} from user {user_id} balance, new balance: {user.balance}")
            return True
        except Exception as e:
            self.db.rollback()
            log_error(f"Error deducting from user {user_id} balance", e)
            return False
    
    def get_users(self, skip: int = 0, limit: int = 10) -> List[User]:
        """
        Get a list of users with pagination
        
        Args:
            skip: Number of users to skip (for pagination)
            limit: Maximum number of users to return
            
        Returns:
            List of users
        """
        try:
            users = self.db.query(User).order_by(User.created_at.desc()).offset(skip).limit(limit).all()
            return users
        except Exception as e:
            log_error("Error getting users list", e)
            return []
    
    def count_users(self) -> int:
        """
        Get total number of users
        
        Returns:
            Total count of users
        """
        try:
            return self.db.query(User).count()
        except Exception as e:
            log_error("Error counting users", e)
            return 0
    
    def count_users_by_role(self, role: UserRole) -> int:
        """
        Count users by role
        
        Args:
            role: User role to count
            
        Returns:
            Number of users with the specified role
        """
        try:
            return self.db.query(User).filter(User.role == role).count()
        except Exception as e:
            log_error(f"Error counting users with role {role}", e)
            return 0 