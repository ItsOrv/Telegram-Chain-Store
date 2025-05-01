from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from src.core.models.payment import Payment, PaymentStatus, PaymentMethod, PaymentType
from src.core.services.base_service import BaseService
from src.core.services.user_service import UserService
from src.core.services.notification_service import NotificationService
from src.utils.logger import log_error, setup_logger
from datetime import datetime
import json

# Initialize logger
logger = setup_logger("payment_service")

class PaymentService(BaseService[Payment]):
    """
    Service for managing payments with two-step verification flow
    """
    
    def __init__(self, db_session: Session):
        """
        Initialize the payment service
        
        Args:
            db_session: SQLAlchemy database session
        """
        super().__init__(db_session, Payment)
        self.user_service = UserService(db_session)
        self.notification_service = NotificationService(db_session)
    
    def create_payment(self, user_id: int, amount: float, payment_method: PaymentMethod, 
                     payment_type: PaymentType = PaymentType.ORDER, order_id: Optional[int] = None,
                     transaction_id: Optional[str] = None, transaction_data: Optional[Dict] = None) -> Optional[Payment]:
        """
        Create a new payment
        
        Args:
            user_id: User ID
            amount: Payment amount
            payment_method: Payment method
            payment_type: Payment type (ORDER or WALLET_CHARGE)
            order_id: Order ID (optional, for order payments)
            transaction_id: Transaction ID (optional)
            transaction_data: Transaction data (optional)
            
        Returns:
            Created payment if successful, None otherwise
        """
        try:
            # Verify user exists
            user = self.user_service.get_by_id(user_id)
            if not user:
                logger.error(f"Cannot create payment: User {user_id} not found")
                return None
            
            # Create payment data
            payment_data = {
                "user_id": user_id,
                "amount": amount,
                "payment_method": payment_method,
                "payment_type": payment_type,
                "status": PaymentStatus.PENDING,
                "transaction_id": transaction_id
            }
            
            # Add order ID if provided
            if order_id:
                payment_data["order_id"] = order_id
            
            # Add transaction data if provided
            if transaction_data:
                payment_data["transaction_data"] = json.dumps(transaction_data)
            
            # Create payment
            payment = self.create(payment_data)
            if payment:
                logger.info(f"Created payment {payment.id} for user {user_id}, amount {amount}")
                
                # Notify user
                self.notification_service.create_notification(
                    user_id=user_id,
                    title="Payment Created",
                    message=f"Your payment of {amount} has been created and is awaiting verification.",
                    type="PAYMENT",
                    payment_id=payment.id
                )
            return payment
        except Exception as e:
            log_error(f"Error creating payment for user {user_id}", e)
            return None
    
    def verify_by_cardholder(self, payment_id: int, cardholder_id: int, notes: Optional[str] = None) -> bool:
        """
        Verify a payment by a cardholder (first step of verification)
        
        Args:
            payment_id: Payment ID
            cardholder_id: Cardholder user ID
            notes: Verification notes (optional)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Verify payment exists and is pending
            payment = self.get_by_id(payment_id)
            if not payment or payment.status != PaymentStatus.PENDING:
                logger.error(f"Cannot verify payment {payment_id}: Not found or not pending")
                return False
            
            # Verify cardholder exists and is a cardholder
            cardholder = self.user_service.get_by_id(cardholder_id)
            if not cardholder or not cardholder.is_cardholder:
                logger.error(f"User {cardholder_id} is not a valid cardholder")
                return False
            
            # Update payment status
            payment.status = PaymentStatus.CARDHOLDER_VERIFIED
            payment.cardholder_id = cardholder_id
            payment.cardholder_verified_at = datetime.utcnow()
            if notes:
                payment.cardholder_notes = notes
            
            self.db.commit()
            logger.info(f"Payment {payment_id} verified by cardholder {cardholder_id}")
            
            # Notify user
            self.notification_service.create_notification(
                user_id=payment.user_id,
                title="Payment Verified by Cardholder",
                message=f"Your payment of {payment.amount} has been verified by a cardholder and is awaiting admin verification.",
                type="PAYMENT",
                payment_id=payment_id
            )
            
            # Notify admin
            # Assuming the admin IDs are configured in settings or retrieved from user service
            admin_ids = self.user_service.get_users_by_role("ADMIN")
            for admin in admin_ids:
                self.notification_service.create_notification(
                    user_id=admin.id,
                    title="Payment Needs Admin Verification",
                    message=f"Payment {payment_id} of {payment.amount} has been verified by cardholder and needs admin verification.",
                    type="PAYMENT",
                    payment_id=payment_id,
                    is_urgent=True
                )
            
            return True
        except Exception as e:
            self.db.rollback()
            log_error(f"Error verifying payment {payment_id} by cardholder {cardholder_id}", e)
            return False
    
    def verify_by_admin(self, payment_id: int, admin_id: int, notes: Optional[str] = None) -> bool:
        """
        Verify a payment by an admin (second step of verification)
        
        Args:
            payment_id: Payment ID
            admin_id: Admin user ID
            notes: Verification notes (optional)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Verify payment exists and is cardholder verified
            payment = self.get_by_id(payment_id)
            if not payment or payment.status != PaymentStatus.CARDHOLDER_VERIFIED:
                logger.error(f"Cannot verify payment {payment_id}: Not found or not cardholder verified")
                return False
            
            # Verify admin exists and is an admin
            admin = self.user_service.get_by_id(admin_id)
            if not admin or not admin.is_admin:
                logger.error(f"User {admin_id} is not a valid admin")
                return False
            
            # Update payment status
            payment.status = PaymentStatus.ADMIN_VERIFIED
            payment.admin_id = admin_id
            payment.admin_verified_at = datetime.utcnow()
            if notes:
                payment.admin_notes = notes
            
            self.db.commit()
            logger.info(f"Payment {payment_id} verified by admin {admin_id}")
            
            # Notify user
            self.notification_service.create_notification(
                user_id=payment.user_id,
                title="Payment Fully Verified",
                message=f"Your payment of {payment.amount} has been fully verified and is being processed.",
                type="PAYMENT",
                payment_id=payment_id
            )
            
            # Based on payment type, handle differently
            if payment.payment_type == PaymentType.WALLET_CHARGE:
                # Add balance to user's wallet
                self.user_service.add_balance(payment.user_id, float(payment.amount))
                
                # Mark payment as completed
                payment.status = PaymentStatus.COMPLETED
                payment.completed_at = datetime.utcnow()
                self.db.commit()
                
                # Notify user about wallet charge
                self.notification_service.create_notification(
                    user_id=payment.user_id,
                    title="Wallet Charged",
                    message=f"Your wallet has been charged with {payment.amount}.",
                    type="PAYMENT",
                    payment_id=payment_id
                )
            
            return True
        except Exception as e:
            self.db.rollback()
            log_error(f"Error verifying payment {payment_id} by admin {admin_id}", e)
            return False
    
    def complete_payment(self, payment_id: int) -> bool:
        """
        Mark a payment as completed
        
        Args:
            payment_id: Payment ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Verify payment exists and is admin verified
            payment = self.get_by_id(payment_id)
            if not payment or payment.status != PaymentStatus.ADMIN_VERIFIED:
                logger.error(f"Cannot complete payment {payment_id}: Not found or not admin verified")
                return False
            
            # Update payment status
            payment.status = PaymentStatus.COMPLETED
            payment.completed_at = datetime.utcnow()
            
            self.db.commit()
            logger.info(f"Payment {payment_id} marked as completed")
            
            # Notify user
            self.notification_service.create_notification(
                user_id=payment.user_id,
                title="Payment Completed",
                message=f"Your payment of {payment.amount} has been completed.",
                type="PAYMENT",
                payment_id=payment_id
            )
            
            return True
        except Exception as e:
            self.db.rollback()
            log_error(f"Error completing payment {payment_id}", e)
            return False
    
    def reject_payment(self, payment_id: int, rejected_by_id: int, reason: str) -> bool:
        """
        Reject a payment
        
        Args:
            payment_id: Payment ID
            rejected_by_id: User ID of rejector
            reason: Rejection reason
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Verify payment exists and is not already completed or failed
            payment = self.get_by_id(payment_id)
            if not payment or payment.status in [PaymentStatus.COMPLETED, PaymentStatus.FAILED, PaymentStatus.REFUNDED]:
                logger.error(f"Cannot reject payment {payment_id}: Not found or already processed")
                return False
            
            # Update payment status
            payment.status = PaymentStatus.FAILED
            
            # Add notes based on who rejected it
            rejector = self.user_service.get_by_id(rejected_by_id)
            if rejector.is_cardholder:
                payment.cardholder_id = rejected_by_id
                payment.cardholder_verified_at = datetime.utcnow()
                payment.cardholder_notes = f"Rejected: {reason}"
            elif rejector.is_admin:
                payment.admin_id = rejected_by_id
                payment.admin_verified_at = datetime.utcnow()
                payment.admin_notes = f"Rejected: {reason}"
            
            self.db.commit()
            logger.info(f"Payment {payment_id} rejected by user {rejected_by_id}: {reason}")
            
            # Notify user
            self.notification_service.create_notification(
                user_id=payment.user_id,
                title="Payment Rejected",
                message=f"Your payment of {payment.amount} has been rejected: {reason}",
                type="PAYMENT",
                payment_id=payment_id,
                is_urgent=True
            )
            
            return True
        except Exception as e:
            self.db.rollback()
            log_error(f"Error rejecting payment {payment_id}", e)
            return False
    
    def get_pending_payments(self, skip: int = 0, limit: int = 20) -> List[Payment]:
        """
        Get pending payments
        
        Args:
            skip: Number of payments to skip
            limit: Maximum number of payments to return
            
        Returns:
            List of pending payments
        """
        try:
            return self.db.query(Payment).filter(Payment.status == PaymentStatus.PENDING)\
                .order_by(desc(Payment.created_at))\
                .offset(skip).limit(limit).all()
        except Exception as e:
            log_error("Error getting pending payments", e)
            return []
    
    def get_cardholder_verified_payments(self, skip: int = 0, limit: int = 20) -> List[Payment]:
        """
        Get payments verified by cardholders but not by admin
        
        Args:
            skip: Number of payments to skip
            limit: Maximum number of payments to return
            
        Returns:
            List of cardholder verified payments
        """
        try:
            return self.db.query(Payment).filter(Payment.status == PaymentStatus.CARDHOLDER_VERIFIED)\
                .order_by(desc(Payment.cardholder_verified_at))\
                .offset(skip).limit(limit).all()
        except Exception as e:
            log_error("Error getting cardholder verified payments", e)
            return []
    
    def get_user_payments(self, user_id: int, skip: int = 0, limit: int = 20) -> List[Payment]:
        """
        Get payments for a specific user
        
        Args:
            user_id: User ID
            skip: Number of payments to skip
            limit: Maximum number of payments to return
            
        Returns:
            List of payments
        """
        try:
            payments = self.db.query(Payment).filter(
                Payment.user_id == user_id
            ).order_by(desc(Payment.created_at)).offset(skip).limit(limit).all()
            
            return payments
        except Exception as e:
            log_error(f"Error getting payments for user {user_id}", e)
            return []
    
    def get_recent_payments(self, skip: int = 0, limit: int = 5) -> List[Payment]:
        """
        Get most recent payments across all users
        
        Args:
            skip: Number of payments to skip
            limit: Maximum number of payments to return
            
        Returns:
            List of payments sorted by creation date (newest first)
        """
        try:
            payments = self.db.query(Payment).order_by(
                desc(Payment.created_at)
            ).offset(skip).limit(limit).all()
            
            return payments
        except Exception as e:
            log_error("Error getting recent payments", e)
            return []
    
    def count_payments(self) -> int:
        """
        Count total number of payments
        
        Returns:
            Total count of payments
        """
        try:
            return self.db.query(Payment).count()
        except Exception as e:
            log_error("Error counting payments", e)
            return 0
    
    def count_pending_payments(self) -> int:
        """
        Count payments that are still pending verification
        
        Returns:
            Count of pending payments
        """
        try:
            return self.db.query(Payment).filter(
                Payment.status == PaymentStatus.PENDING
            ).count()
        except Exception as e:
            log_error("Error counting pending payments", e)
            return 0 