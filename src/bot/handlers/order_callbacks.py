from telethon import events
from src.utils.logger import setup_logger, log_error
from src.core.database import get_db_session
from src.core.services.order_service import OrderService
from src.core.services.user_service import UserService
from src.core.services.product_service import ProductService
from src.core.services.payment_service import PaymentService
from src.bot.handlers.callback_router import register_callback
from typing import List

# Initialize logger
logger = setup_logger("order_callbacks")

def register_order_callbacks():
    """Register order-related callback handlers"""
    logger.info("Registering order callbacks")
    
    @register_callback("view_order")
    async def handle_view_order(event: events.CallbackQuery.Event, params: List[str]) -> None:
        """Handle view order callback"""
        try:
            if len(params) < 1:
                await event.answer("Invalid order ID", alert=True)
                return
                
            order_id = int(params[0])
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
                
                # Check if this user is authorized to view this order
                if order.user_id != user.id and not user.is_admin and not user.is_seller:
                    await event.answer("You are not authorized to view this order", alert=True)
                    return
                
                # Build order details message
                message = (
                    f"🧾 **Order #{order.id}**\n\n"
                    f"📅 Date: {order.created_at.strftime('%Y-%m-%d %H:%M')}\n"
                    f"🔄 Status: {order.status}\n"
                    f"💰 Total: ${order.total_amount:.2f}\n\n"
                    f"**Items:**\n"
                )
                
                for i, item in enumerate(order.items, 1):
                    message += (
                        f"{i}. **{item.product.name}**\n"
                        f"   Quantity: {item.quantity} x ${item.price:.2f} = ${item.quantity * item.price:.2f}\n\n"
                    )
                
                message += f"\n**Delivery Location:** {order.location.name if order.location else 'Not specified'}"
                
                # Create keyboard with order actions
                from src.bot.keyboards.order_keyboard import get_order_detail_keyboard
                keyboard = get_order_detail_keyboard(order, user)
                
                await event.edit(message, buttons=keyboard)
                
        except Exception as e:
            log_error("Error in handle_view_order", e, event.sender_id)
            await event.answer("An error occurred. Please try again later.", alert=True)
    
    @register_callback("cancel_order")
    async def handle_cancel_order(event: events.CallbackQuery.Event, params: List[str]) -> None:
        """Handle cancel order callback"""
        try:
            if len(params) < 1:
                await event.answer("Invalid order ID", alert=True)
                return
                
            order_id = int(params[0])
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
                
                # Check if this user is authorized to cancel this order
                if order.user_id != user.id and not user.is_admin:
                    await event.answer("You are not authorized to cancel this order", alert=True)
                    return
                
                # Check if order can be cancelled
                if order.status not in ["pending", "payment_pending"]:
                    await event.answer("This order cannot be cancelled in its current state", alert=True)
                    return
                
                # Cancel the order
                order_service.cancel_order(order_id, user.id)
                
                await event.answer("Order has been cancelled")
                
                # Return to updated order view
                await handle_view_order(event, [str(order_id)])
                
        except Exception as e:
            log_error("Error in handle_cancel_order", e, event.sender_id)
            await event.answer("An error occurred. Please try again later.", alert=True)
    
    @register_callback("pay_order")
    async def handle_pay_order(event: events.CallbackQuery.Event, params: List[str]) -> None:
        """Handle pay order callback"""
        try:
            if len(params) < 1:
                await event.answer("Invalid order ID", alert=True)
                return
                
            order_id = int(params[0])
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
                
                # Check if order can be paid
                if order.status != "payment_pending":
                    await event.answer("This order cannot be paid in its current state", alert=True)
                    return
                
                # Show payment options
                message = (
                    f"💰 **Pay for Order #{order.id}**\n\n"
                    f"Total Amount: ${order.total_amount:.2f}\n\n"
                    "Choose a payment method:"
                )
                
                # Create keyboard with payment options
                from src.bot.keyboards.payment_keyboard import get_payment_method_keyboard
                keyboard = get_payment_method_keyboard(order_id)
                
                await event.edit(message, buttons=keyboard)
                
        except Exception as e:
            log_error("Error in handle_pay_order", e, event.sender_id)
            await event.answer("An error occurred. Please try again later.", alert=True)
    
    @register_callback("track_order")
    async def handle_track_order(event: events.CallbackQuery.Event, params: List[str]) -> None:
        """Handle track order callback"""
        try:
            if len(params) < 1:
                await event.answer("Invalid order ID", alert=True)
                return
                
            order_id = int(params[0])
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
                
                # Check if this user is authorized to track this order
                if order.user_id != user.id and not user.is_admin and not user.is_seller:
                    await event.answer("You are not authorized to track this order", alert=True)
                    return
                
                # Build order tracking message
                message = (
                    f"🔍 **Tracking Order #{order.id}**\n\n"
                    f"Current Status: {order.status}\n\n"
                    "Order Timeline:\n"
                )
                
                # Add timeline events
                message += (
                    f"✅ Order Placed: {order.created_at.strftime('%Y-%m-%d %H:%M')}\n"
                )
                
                if order.payment:
                    message += (
                        f"{'✅' if order.payment.status in ['COMPLETED', 'ADMIN_VERIFIED'] else '⏳'} "
                        f"Payment: {order.payment.status}\n"
                    )
                
                message += (
                    f"{'✅' if order.status in ['shipped', 'delivered'] else '⏳'} Shipping: "
                    f"{'Shipped' if order.status in ['shipped', 'delivered'] else 'Pending'}\n"
                    
                    f"{'✅' if order.status == 'delivered' else '⏳'} Delivery: "
                    f"{'Delivered' if order.status == 'delivered' else 'Pending'}\n"
                )
                
                # Add location details if available
                if order.location:
                    message += (
                        f"\n**Delivery Location:**\n"
                        f"{order.location.name}\n"
                        f"{order.location.address}\n"
                        f"{order.location.area}, {order.location.city.name}\n"
                    )
                
                # Create keyboard with tracking actions
                from src.bot.keyboards.order_keyboard import get_tracking_keyboard
                keyboard = get_tracking_keyboard(order)
                
                await event.edit(message, buttons=keyboard)
                
        except Exception as e:
            log_error("Error in handle_track_order", e, event.sender_id)
            await event.answer("An error occurred. Please try again later.", alert=True)
            
    logger.info("Order callbacks registered") 