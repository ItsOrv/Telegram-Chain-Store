from src.bot.common.keyboards import PaymentKeyboards  # Add this import
from typing import Dict, Any
from datetime import datetime
from src.core.exceptions import ValidationError, PaymentError
from src.core.services.payment_manager import PaymentManager
from src.core.services.crypto_manager import CryptoManager

class PaymentHandler:
    def __init__(self):
        self.payment_manager = PaymentManager()
        self.crypto_manager = CryptoManager()

    async def handle_payment_command(self, message: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Handle payment commands"""
        try:
            command = message.get('text', '').split()[0].lower()
            
            if command == '/confirm_payment':
                await self.handle_confirm_payment(message, context)
            elif command == '/payment_status':
                await self.handle_payment_status(message, context)
            elif command == '/payment_history':
                await self.handle_payment_history(message, context)
            else:
                await context.bot.send_message(
                    chat_id=message['chat']['id'],
                    text="Invalid payment command. Available commands:\n"
                         "/confirm_payment <tx_hash> - Confirm your payment\n"
                         "/payment_status <payment_id> - Check payment status\n"
                         "/payment_history - View payment history"
                )
        except Exception as e:
            await context.bot.send_message(
                chat_id=message['chat']['id'],
                text=f"Error processing payment command: {str(e)}"
            )

    async def handle_confirm_payment(self, message: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Handle /confirm_payment command"""
        try:
            # Get transaction hash from message
            parts = message.get('text', '').split()
            if len(parts) < 2:
                raise ValidationError("Please provide the transaction hash")
            
            tx_hash = parts[1]
            
            # Validate transaction hash
            if not self.crypto_manager.validate_transaction_hash(tx_hash):
                raise ValidationError("Invalid transaction hash")
            
            # Process payment
            payment_data = {
                "transaction_hash": tx_hash,
                "user_id": message['from']['id']
            }
            
            payment = self.payment_manager.process_payment(payment_data)
            
            confirm_text = (
                "✅ Payment Confirmed!\n\n"
                f"Payment ID: #{payment.id}\n"
                f"Amount: {payment.amount} USDT\n"
                f"Status: {payment.status}\n"
                f"Date: {payment.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                "Your order will be processed shortly."
            )
            
            await context.bot.send_message(
                chat_id=message['chat']['id'],
                text=confirm_text
            )
        except Exception as e:
            await context.bot.send_message(
                chat_id=message['chat']['id'],
                text=f"Error confirming payment: {str(e)}"
            )

    async def handle_payment_status(self, message: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Handle /payment_status command"""
        try:
            # Get payment ID from message
            parts = message.get('text', '').split()
            if len(parts) < 2:
                raise ValidationError("Please provide the payment ID")
            
            payment_id = int(parts[1])
            
            # Get payment status
            payment = self.payment_manager.get_payment(payment_id)
            if not payment:
                raise PaymentError("Payment not found")
            
            status_text = (
                "💳 Payment Status:\n\n"
                f"Payment ID: #{payment.id}\n"
                f"Amount: {payment.amount} USDT\n"
                f"Status: {payment.status}\n"
                f"Date: {payment.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"Transaction Hash: {payment.transaction_hash}"
            )
            
            await context.bot.send_message(
                chat_id=message['chat']['id'],
                text=status_text
            )
        except Exception as e:
            await context.bot.send_message(
                chat_id=message['chat']['id'],
                text=f"Error checking payment status: {str(e)}"
            )

    async def handle_payment_history(self, message: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Handle /payment_history command"""
        try:
            user_id = message['from']['id']
            payments = self.payment_manager.get_user_payments(user_id)
            
            if not payments:
                await context.bot.send_message(
                    chat_id=message['chat']['id'],
                    text="You haven't made any payments yet."
                )
                return
            
            history_text = "📋 Payment History:\n\n"
            for payment in payments:
                history_text += (
                    f"Payment #{payment.id}\n"
                    f"Amount: {payment.amount} USDT\n"
                    f"Status: {payment.status}\n"
                    f"Date: {payment.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"Transaction Hash: {payment.transaction_hash}\n\n"
                )
            
            await context.bot.send_message(
                chat_id=message['chat']['id'],
                text=history_text
            )
        except Exception as e:
            await context.bot.send_message(
                chat_id=message['chat']['id'],
                text=f"Error viewing payment history: {str(e)}"
            )

    async def show_crypto_options(self, event):
        # ...existing code...
        buttons = PaymentKeyboards.get_crypto_payment_options()
        await event.edit(message, buttons=buttons)

    async def show_payment_verification(self, event):
        # ...existing code...
        buttons = PaymentKeyboards.get_payment_verification()
        await event.edit(message, buttons=buttons)
