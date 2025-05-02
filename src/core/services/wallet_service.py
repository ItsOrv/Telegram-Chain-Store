from sqlalchemy.orm import Session
from src.core.models.wallet import Wallet, Transaction, TransactionType, TransactionStatus
from src.core.models.user import User
from typing import List, Optional, Dict, Any, Union
from src.utils.logger import setup_logger, log_error
from datetime import datetime
import uuid

# Initialize logger
logger = setup_logger("wallet_service")

class WalletService:
    """Service for handling wallet operations"""
    
    def __init__(self, session: Session):
        """Initialize service with database session"""
        self.session = session
    
    def get_user_wallet(self, user_id: int) -> Optional[Wallet]:
        """Get a user's wallet"""
        try:
            return self.session.query(Wallet).filter(Wallet.user_id == user_id).first()
        except Exception as e:
            log_error(f"Error getting wallet for user {user_id}", e)
            return None
    
    def create_wallet(self, user_id: int) -> Optional[Wallet]:
        """Create a new wallet for user"""
        try:
            # Check if wallet already exists
            existing_wallet = self.get_user_wallet(user_id)
            if existing_wallet:
                return existing_wallet
            
            # Create new wallet
            wallet = Wallet(
                user_id=user_id,
                balance=0,
                currency="IRR",
                is_active=True
            )
            
            self.session.add(wallet)
            self.session.commit()
            logger.info(f"Created new wallet for user {user_id}")
            return wallet
        except Exception as e:
            self.session.rollback()
            log_error(f"Error creating wallet for user {user_id}", e)
            return None
    
    def get_wallet_balance(self, user_id: int) -> float:
        """Get user's wallet balance"""
        wallet = self.get_user_wallet(user_id)
        if not wallet:
            # If wallet doesn't exist, create one
            wallet = self.create_wallet(user_id)
        
        return wallet.balance if wallet else 0.0
    
    def add_funds(self, user_id: int, amount: float, description: str = None, reference_id: str = None) -> bool:
        """Add funds to user's wallet"""
        try:
            # Get or create wallet
            wallet = self.get_user_wallet(user_id)
            if not wallet:
                wallet = self.create_wallet(user_id)
                if not wallet:
                    return False
            
            # Update balance
            wallet.balance += amount
            wallet.last_updated = datetime.utcnow()
            
            # Create transaction
            transaction = Transaction(
                wallet_id=wallet.id,
                amount=amount,
                type=TransactionType.DEPOSIT,
                status=TransactionStatus.COMPLETED,
                description=description or "Deposit to wallet",
                reference_id=reference_id or str(uuid.uuid4()),
                created_at=datetime.utcnow()
            )
            
            self.session.add(transaction)
            self.session.commit()
            logger.info(f"Added {amount} funds to wallet for user {user_id}")
            return True
        except Exception as e:
            self.session.rollback()
            log_error(f"Error adding funds to wallet for user {user_id}", e)
            return False
    
    def deduct_funds(self, user_id: int, amount: float, description: str = None, reference_id: str = None) -> bool:
        """Deduct funds from user's wallet"""
        try:
            # Get wallet
            wallet = self.get_user_wallet(user_id)
            if not wallet:
                return False
            
            # Check if sufficient balance
            if wallet.balance < amount:
                logger.warning(f"Insufficient balance for user {user_id}: {wallet.balance} < {amount}")
                return False
            
            # Update balance
            wallet.balance -= amount
            wallet.last_updated = datetime.utcnow()
            
            # Create transaction
            transaction = Transaction(
                wallet_id=wallet.id,
                amount=-amount,  # Negative for deduction
                type=TransactionType.WITHDRAWAL,
                status=TransactionStatus.COMPLETED,
                description=description or "Withdrawal from wallet",
                reference_id=reference_id or str(uuid.uuid4()),
                created_at=datetime.utcnow()
            )
            
            self.session.add(transaction)
            self.session.commit()
            logger.info(f"Deducted {amount} funds from wallet for user {user_id}")
            return True
        except Exception as e:
            self.session.rollback()
            log_error(f"Error deducting funds from wallet for user {user_id}", e)
            return False
    
    def transfer_funds(self, from_user_id: int, to_user_id: int, amount: float, description: str = None) -> bool:
        """Transfer funds between wallets"""
        try:
            # Generate reference ID for linking transactions
            reference_id = str(uuid.uuid4())
            
            # Deduct from sender
            if not self.deduct_funds(from_user_id, amount, 
                                   f"Transfer to user {to_user_id}: {description or ''}", 
                                   reference_id):
                return False
            
            # Add to recipient
            if not self.add_funds(to_user_id, amount, 
                                f"Transfer from user {from_user_id}: {description or ''}", 
                                reference_id):
                # Rollback the deduction if adding fails
                self.add_funds(from_user_id, amount, "Reversal of failed transfer", reference_id)
                return False
            
            logger.info(f"Transferred {amount} from user {from_user_id} to user {to_user_id}")
            return True
        except Exception as e:
            self.session.rollback()
            log_error(f"Error transferring funds from {from_user_id} to {to_user_id}", e)
            return False
    
    def get_user_transactions(self, user_id: int, limit: int = 10, offset: int = 0) -> List[Transaction]:
        """Get transactions for a user"""
        try:
            wallet = self.get_user_wallet(user_id)
            if not wallet:
                return []
            
            return self.session.query(Transaction)\
                .filter(Transaction.wallet_id == wallet.id)\
                .order_by(Transaction.created_at.desc())\
                .limit(limit).offset(offset).all()
        except Exception as e:
            log_error(f"Error getting transactions for user {user_id}", e)
            return []
    
    def count_user_transactions(self, user_id: int) -> int:
        """Count total transactions for a user"""
        try:
            wallet = self.get_user_wallet(user_id)
            if not wallet:
                return 0
            
            return self.session.query(Transaction)\
                .filter(Transaction.wallet_id == wallet.id)\
                .count()
        except Exception as e:
            log_error(f"Error counting transactions for user {user_id}", e)
            return 0
    
    def get_transaction_by_id(self, transaction_id: int) -> Optional[Transaction]:
        """Get a specific transaction by ID"""
        try:
            return self.session.query(Transaction).filter(Transaction.id == transaction_id).first()
        except Exception as e:
            log_error(f"Error getting transaction {transaction_id}", e)
            return None
    
    def get_transactions_by_reference(self, reference_id: str) -> List[Transaction]:
        """Get transactions by reference ID"""
        try:
            return self.session.query(Transaction)\
                .filter(Transaction.reference_id == reference_id)\
                .order_by(Transaction.created_at.desc())\
                .all()
        except Exception as e:
            log_error(f"Error getting transactions for reference {reference_id}", e)
            return []
    
    def activate_wallet(self, user_id: int) -> bool:
        """Activate a user's wallet"""
        try:
            wallet = self.get_user_wallet(user_id)
            if not wallet:
                return False
            
            wallet.is_active = True
            self.session.commit()
            logger.info(f"Activated wallet for user {user_id}")
            return True
        except Exception as e:
            self.session.rollback()
            log_error(f"Error activating wallet for user {user_id}", e)
            return False
    
    def deactivate_wallet(self, user_id: int) -> bool:
        """Deactivate a user's wallet"""
        try:
            wallet = self.get_user_wallet(user_id)
            if not wallet:
                return False
            
            wallet.is_active = False
            self.session.commit()
            logger.info(f"Deactivated wallet for user {user_id}")
            return True
        except Exception as e:
            self.session.rollback()
            log_error(f"Error deactivating wallet for user {user_id}", e)
            return False 