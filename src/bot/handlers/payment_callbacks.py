from telethon import events
from src.utils.logger import setup_logger, log_error
from src.core.database import get_db_session
from src.core.services.payment_service import PaymentService
from src.core.services.user_service import UserService
from src.core.services.order_service import OrderService
from src.bot.handlers.callback_router import register_callback
from typing import List
from src.core.models.payment import PaymentMethod, PaymentStatus

# Initialize logger
logger = setup_logger("payment_callbacks")

def register_payment_callbacks():
    """Register payment-related callback handlers"""
    logger.info("Registering payment callbacks")
    
    @register_callback("payment_method")
    async def handle_payment_method(event: events.CallbackQuery.Event, params: List[str]) -> None:
        """Handle payment method callback"""
        try:
            if len(params) < 2:
                await event.answer("Invalid parameters", alert=True)
                return
                
            order_id = int(params[0])
            method = params[1]  # wallet, crypto, cash
            sender = await event.get_sender()
            
            with get_db_session() as session:
                user_service = UserService(session)
                user = user_service.get_by_telegram_id(sender.id)
                
                if not user:
                    await event.answer("Please start the bot first", alert=True)
                    return
                
                order_service = OrderService(session)
                order = order_service.get_by_id(order_id)
                
                if not order:
                    await event.answer("Order not found", alert=True)
                    return
                
                # Check if this user is authorized to pay for this order
                if order.user_id != user.id:
                    await event.answer("You are not authorized to pay for this order", alert=True)
                    return
                
                # Create payment based on method
                payment_service = PaymentService(session)
                
                if method == "wallet":
                    # Check if user has enough balance
                    if user.balance < order.total_amount:
                        await event.answer("Insufficient wallet balance", alert=True)
                        message = (
                            f"❌ **Insufficient Balance**\n\n"
                            f"Your wallet balance: ${user.balance:.2f}\n"
                            f"Order total: ${order.total_amount:.2f}\n\n"
                            f"Please add funds to your wallet or choose a different payment method."
                        )
                        from src.bot.keyboards.payment_keyboard import get_payment_method_keyboard
                        keyboard = get_payment_method_keyboard(order_id)
                        await event.edit(message, buttons=keyboard)
                        return
                    
                    # Create wallet payment
                    payment = payment_service.create_payment(
                        user_id=user.id,
                        order_id=order_id,
                        amount=order.total_amount,
                        payment_method=PaymentMethod.WALLET
                    )
                    
                    # Process wallet payment immediately
                    payment_service.process_wallet_payment(payment.id)
                    
                    # Update order status
                    order_service.update_order_status(order_id, "processing")
                    
                    message = (
                        f"✅ **Payment Successful**\n\n"
                        f"Order #{order_id} has been paid using your wallet balance.\n"
                        f"Amount: ${order.total_amount:.2f}\n\n"
                        f"Your order is now being processed."
                    )
                    
                    from src.bot.keyboards.order_keyboard import get_order_success_keyboard
                    keyboard = get_order_success_keyboard(order_id)
                    
                    await event.edit(message, buttons=keyboard)
                
                elif method == "crypto":
                    # Create crypto payment
                    payment = payment_service.create_payment(
                        user_id=user.id,
                        order_id=order_id,
                        amount=order.total_amount,
                        payment_method=PaymentMethod.CRYPTO
                    )
                    
                    # Show crypto payment instructions
                    from src.config.settings import get_settings
                    settings = get_settings()
                    
                    message = (
                        f"💸 **Crypto Payment**\n\n"
                        f"Order #{order_id} - Amount: ${order.total_amount:.2f}\n\n"
                        f"Please send exactly ${order.total_amount:.2f} worth of USDT "
                        f"to the following address:\n\n"
                        f"`{settings.CRYPTO_WALLET_ADDRESS}`\n\n"
                        f"Network: {settings.CRYPTO_NETWORK}\n\n"
                        f"⚠️ **Important:**\n"
                        f"• Include your order ID ({order_id}) in the transaction memo\n"
                        f"• After sending, click 'I've Paid' to upload your receipt\n"
                        f"• Payment will be verified manually by our team\n"
                    )
                    
                    from src.bot.keyboards.payment_keyboard import get_crypto_payment_keyboard
                    keyboard = get_crypto_payment_keyboard(payment.id)
                    
                    await event.edit(message, buttons=keyboard)
                
                elif method == "cash":
                    # Create cash payment
                    payment = payment_service.create_payment(
                        user_id=user.id,
                        order_id=order_id,
                        amount=order.total_amount,
                        payment_method=PaymentMethod.CASH
                    )
                    
                    # Show cash payment instructions
                    message = (
                        f"💵 **Cash Payment**\n\n"
                        f"Order #{order_id} - Amount: ${order.total_amount:.2f}\n\n"
                        f"Instructions for cash payment:\n\n"
                        f"1. Visit any of our partner locations\n"
                        f"2. Show your order ID ({order_id}) to the cashier\n"
                        f"3. Pay the amount in cash\n"
                        f"4. Upload a photo of your receipt using the button below\n\n"
                        f"⚠️ Your order will be processed after payment verification."
                    )
                    
                    from src.bot.keyboards.payment_keyboard import get_cash_payment_keyboard
                    keyboard = get_cash_payment_keyboard(payment.id)
                    
                    await event.edit(message, buttons=keyboard)
                
                else:
                    await event.answer("Invalid payment method", alert=True)
                
        except Exception as e:
            log_error("Error in handle_payment_method", e, event.sender_id)
            await event.answer("An error occurred. Please try again later.", alert=True)
    
    @register_callback("upload_receipt")
    async def handle_upload_receipt(event: events.CallbackQuery.Event, params: List[str]) -> None:
        """Handle upload receipt callback"""
        try:
            if len(params) < 1:
                await event.answer("Invalid payment ID", alert=True)
                return
                
            payment_id = int(params[0])
            sender = await event.get_sender()
            
            with get_db_session() as session:
                user_service = UserService(session)
                user = user_service.get_by_telegram_id(sender.id)
                
                if not user:
                    await event.answer("Please start the bot first", alert=True)
                    return
                
                payment_service = PaymentService(session)
                payment = payment_service.get_by_id(payment_id)
                
                if not payment:
                    await event.answer("Payment not found", alert=True)
                    return
                
                # Check if this user is authorized to upload receipt for this payment
                if payment.user_id != user.id:
                    await event.answer("You are not authorized to upload receipt for this payment", alert=True)
                    return
                
                # Update user state to wait for receipt upload
                user_service.set_user_state(user.id, f"upload_receipt:{payment_id}")
                
                message = (
                    "📸 **Upload Payment Receipt**\n\n"
                    "Please send a photo of your payment receipt.\n\n"
                    "The receipt should clearly show:\n"
                    "• Payment amount\n"
                    "• Transaction ID or reference number\n"
                    "• Date and time of payment\n\n"
                    "You can cancel this operation by clicking the button below."
                )
                
                from src.bot.keyboards.payment_keyboard import get_cancel_upload_keyboard
                keyboard = get_cancel_upload_keyboard()
                
                await event.edit(message, buttons=keyboard)
                
        except Exception as e:
            log_error("Error in handle_upload_receipt", e, event.sender_id)
            await event.answer("An error occurred. Please try again later.", alert=True)
    
    @register_callback("verify_payment")
    async def handle_verify_payment(event: events.CallbackQuery.Event, params: List[str]) -> None:
        """Handle verify payment callback - for cardholders and admins"""
        try:
            if len(params) < 2:
                await event.answer("Invalid parameters", alert=True)
                return
                
            payment_id = int(params[0])
            action = params[1]  # approve or reject
            sender = await event.get_sender()
            
            with get_db_session() as session:
                user_service = UserService(session)
                user = user_service.get_by_telegram_id(sender.id)
                
                if not user:
                    await event.answer("Please start the bot first", alert=True)
                    return
                
                # Check if user is authorized to verify payments
                if not (user.is_cardholder or user.is_admin):
                    await event.answer("You are not authorized to verify payments", alert=True)
                    return
                
                payment_service = PaymentService(session)
                payment = payment_service.get_by_id(payment_id)
                
                if not payment:
                    await event.answer("Payment not found", alert=True)
                    return
                
                if action == "approve":
                    if user.is_cardholder:
                        # Cardholder approval
                        payment_service.cardholder_verify_payment(payment_id, user.id)
                        await event.answer("Payment approved by cardholder")
                    elif user.is_admin:
                        # Admin approval
                        payment_service.admin_verify_payment(payment_id, user.id)
                        await event.answer("Payment approved by admin")
                        
                        # If admin approved, check if order needs to be updated
                        if payment.order_id:
                            order_service = OrderService(session)
                            order_service.update_order_status(payment.order_id, "processing")
                else:
                    # Reject payment
                    payment_service.reject_payment(payment_id, user.id)
                    await event.answer("Payment rejected")
                
                # Return to payments list
                if user.is_admin:
                    from src.bot.handlers.admin_handlers import payments_handler
                    # Create a new event to pass to the payments handler
                    await payments_handler(event)
                elif user.is_cardholder:
                    from src.bot.handlers.cardholder_handlers import verify_payments_handler
                    await verify_payments_handler(event)
                
        except Exception as e:
            log_error("Error in handle_verify_payment", e, event.sender_id)
            await event.answer("An error occurred. Please try again later.", alert=True)
            
    logger.info("Payment callbacks registered") 