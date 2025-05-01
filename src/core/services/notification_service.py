from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc
from src.core.models.notification import Notification, NotificationType
from src.core.services.base_service import BaseService
from src.utils.logger import log_error, setup_logger
from datetime import datetime

# Initialize logger
logger = setup_logger("notification_service")

class NotificationService(BaseService[Notification]):
    """
    Service for managing notifications
    """
    
    def __init__(self, db_session: Session):
        """
        Initialize the notification service
        
        Args:
            db_session: SQLAlchemy database session
        """
        super().__init__(db_session, Notification)
    
    def create_notification(self, user_id: int, title: str, message: str, 
                         type: str = NotificationType.SYSTEM, is_urgent: bool = False,
                         order_id: Optional[int] = None, payment_id: Optional[int] = None,
                         data: Optional[Dict[str, Any]] = None, deliver_at: Optional[datetime] = None) -> Optional[Notification]:
        """
        Create a new notification
        
        Args:
            user_id: User ID
            title: Notification title
            message: Notification message
            type: Notification type
            is_urgent: Whether the notification is urgent
            order_id: Related order ID (optional)
            payment_id: Related payment ID (optional)
            data: Additional data (optional)
            deliver_at: Time to deliver the notification (optional)
            
        Returns:
            Created notification if successful, None otherwise
        """
        try:
            # Create notification data
            notification_data = {
                "user_id": user_id,
                "title": title,
                "message": message,
                "type": type,
                "is_urgent": is_urgent,
                "data": data,
                "deliver_at": deliver_at
            }
            
            # Add optional fields
            if order_id:
                notification_data["order_id"] = order_id
            if payment_id:
                notification_data["payment_id"] = payment_id
            
            # Create notification
            notification = self.create(notification_data)
            if notification:
                logger.info(f"Created notification {notification.id} for user {user_id}: {title}")
            return notification
        except Exception as e:
            log_error(f"Error creating notification for user {user_id}", e)
            return None
    
    def mark_as_read(self, notification_id: int) -> bool:
        """
        Mark a notification as read
        
        Args:
            notification_id: Notification ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            notification = self.get_by_id(notification_id)
            if not notification:
                return False
            
            notification.is_read = True
            notification.read_at = datetime.utcnow()
            
            self.db.commit()
            logger.info(f"Marked notification {notification_id} as read")
            return True
        except Exception as e:
            self.db.rollback()
            log_error(f"Error marking notification {notification_id} as read", e)
            return False
    
    def mark_all_as_read(self, user_id: int) -> bool:
        """
        Mark all of a user's notifications as read
        
        Args:
            user_id: User ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            notifications = self.db.query(Notification).filter(
                Notification.user_id == user_id,
                Notification.is_read == False
            ).all()
            
            for notification in notifications:
                notification.is_read = True
                notification.read_at = datetime.utcnow()
            
            self.db.commit()
            logger.info(f"Marked all notifications for user {user_id} as read")
            return True
        except Exception as e:
            self.db.rollback()
            log_error(f"Error marking all notifications for user {user_id} as read", e)
            return False
    
    def get_unread_notifications(self, user_id: int, skip: int = 0, limit: int = 20) -> List[Notification]:
        """
        Get a user's unread notifications
        
        Args:
            user_id: User ID
            skip: Number of notifications to skip
            limit: Maximum number of notifications to return
            
        Returns:
            List of unread notifications
        """
        try:
            current_time = datetime.utcnow()
            
            return self.db.query(Notification).filter(
                Notification.user_id == user_id,
                Notification.is_read == False,
                (Notification.deliver_at.is_(None) | (Notification.deliver_at <= current_time))
            ).order_by(desc(Notification.created_at)).offset(skip).limit(limit).all()
        except Exception as e:
            log_error(f"Error getting unread notifications for user {user_id}", e)
            return []
    
    def get_urgent_notifications(self, user_id: int, limit: int = 5) -> List[Notification]:
        """
        Get a user's urgent notifications
        
        Args:
            user_id: User ID
            limit: Maximum number of notifications to return
            
        Returns:
            List of urgent notifications
        """
        try:
            current_time = datetime.utcnow()
            
            return self.db.query(Notification).filter(
                Notification.user_id == user_id,
                Notification.is_urgent == True,
                Notification.is_read == False,
                (Notification.deliver_at.is_(None) | (Notification.deliver_at <= current_time))
            ).order_by(desc(Notification.created_at)).limit(limit).all()
        except Exception as e:
            log_error(f"Error getting urgent notifications for user {user_id}", e)
            return []
    
    def count_unread(self, user_id: int) -> int:
        """
        Count a user's unread notifications
        
        Args:
            user_id: User ID
            
        Returns:
            Number of unread notifications
        """
        try:
            current_time = datetime.utcnow()
            
            return self.db.query(Notification).filter(
                Notification.user_id == user_id,
                Notification.is_read == False,
                (Notification.deliver_at.is_(None) | (Notification.deliver_at <= current_time))
            ).count()
        except Exception as e:
            log_error(f"Error counting unread notifications for user {user_id}", e)
            return 0
    
    def delete_old_notifications(self, days: int = 30) -> int:
        """
        Delete old notifications
        
        Args:
            days: Age in days after which to delete notifications
            
        Returns:
            Number of deleted notifications
        """
        try:
            from datetime import timedelta
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            query = self.db.query(Notification).filter(Notification.created_at < cutoff_date)
            count = query.count()
            query.delete()
            
            self.db.commit()
            logger.info(f"Deleted {count} notifications older than {days} days")
            return count
        except Exception as e:
            self.db.rollback()
            log_error(f"Error deleting old notifications", e)
            return 0 