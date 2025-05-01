from telethon import events
from src.utils.logger import setup_logger, log_error
from src.core.database import get_db_session
from src.core.services.cart_service import CartService
from src.core.services.user_service import UserService
from src.core.services.product_service import ProductService
from src.core.services.order_service import OrderService
from src.bot.handlers.callback_router import register_callback
from typing import List

# Initialize logger
logger = setup_logger("cart_callbacks")

def register_cart_callbacks():
    """Register cart-related callback handlers"""
    logger.info("Registering cart callbacks")
    
    @register_callback("view_cart")
    async def handle_view_cart(event: events.CallbackQuery.Event, params: List[str]) -> None:
        """Handle view cart callback"""
        try:
            sender = await event.get_sender()
            page = int(params[0]) if params else 1
            
            with get_db_session() as session:
                user_service = UserService(session)
                user = user_service.get_by_telegram_id(sender.id)
                
                if not user:
                    await event.answer("Please start the bot first", alert=True)
                    return
                
                cart_service = CartService(session)
                cart_items = cart_service.get_cart_items(user.id)
                
                if not cart_items:
                    await event.edit("Your cart is empty. Browse products to add items.")
                    return
                
                # Calculate total
                total = sum(item.quantity * item.product.price for item in cart_items)
                
                # Build cart message
                message = f"🛒 **Your Cart**\n\n"
                
                for i, item in enumerate(cart_items, 1):
                    message += (
                        f"{i}. **{item.product.name}**\n"
                        f"   Quantity: {item.quantity} x ${item.product.price:.2f} = ${item.quantity * item.product.price:.2f}\n\n"
                    )
                
                message += f"\n**Total: ${total:.2f}**"
                
                # Create keyboard with cart actions
                from src.bot.keyboards.cart_keyboard import get_cart_keyboard
                keyboard = get_cart_keyboard(cart_items)
                
                await event.edit(message, buttons=keyboard)
                
        except Exception as e:
            log_error("Error in handle_view_cart", e, event.sender_id)
            await event.answer("An error occurred. Please try again later.", alert=True)
    
    @register_callback("update_quantity")
    async def handle_update_quantity(event: events.CallbackQuery.Event, params: List[str]) -> None:
        """Handle update quantity callback"""
        try:
            if len(params) < 2:
                await event.answer("Invalid parameters", alert=True)
                return
                
            product_id = int(params[0])
            action = params[1]  # inc or dec
            sender = await event.get_sender()
            
            with get_db_session() as session:
                user_service = UserService(session)
                user = user_service.get_by_telegram_id(sender.id)
                
                if not user:
                    await event.answer("Please start the bot first", alert=True)
                    return
                
                cart_service = CartService(session)
                product_service = ProductService(session)
                
                cart_item = cart_service.get_cart_item(user.id, product_id)
                
                if not cart_item:
                    await event.answer("Item not found in your cart", alert=True)
                    return
                
                product = product_service.get_by_id(product_id)
                
                if action == "inc":
                    # Check if we can increment based on product stock
                    if cart_item.quantity + 1 > product.stock:
                        await event.answer("Cannot add more, reached maximum available stock", alert=True)
                        return
                    
                    cart_service.update_quantity(user.id, product_id, cart_item.quantity + 1)
                    await event.answer(f"Increased {product.name} quantity to {cart_item.quantity + 1}")
                
                elif action == "dec":
                    if cart_item.quantity <= 1:
                        cart_service.remove_from_cart(user.id, product_id)
                        await event.answer(f"Removed {product.name} from cart")
                    else:
                        cart_service.update_quantity(user.id, product_id, cart_item.quantity - 1)
                        await event.answer(f"Decreased {product.name} quantity to {cart_item.quantity - 1}")
                
                # Refresh cart view
                await handle_view_cart(event, [])
                
        except Exception as e:
            log_error("Error in handle_update_quantity", e, event.sender_id)
            await event.answer("An error occurred. Please try again later.", alert=True)
    
    @register_callback("clear_cart")
    async def handle_clear_cart(event: events.CallbackQuery.Event, params: List[str]) -> None:
        """Handle clear cart callback"""
        try:
            sender = await event.get_sender()
            
            with get_db_session() as session:
                user_service = UserService(session)
                user = user_service.get_by_telegram_id(sender.id)
                
                if not user:
                    await event.answer("Please start the bot first", alert=True)
                    return
                
                cart_service = CartService(session)
                cart_service.clear_cart(user.id)
                
                await event.answer("Your cart has been cleared")
                await event.edit("Your cart is now empty. Browse products to add items.")
                
        except Exception as e:
            log_error("Error in handle_clear_cart", e, event.sender_id)
            await event.answer("An error occurred. Please try again later.", alert=True)
    
    @register_callback("checkout")
    async def handle_checkout(event: events.CallbackQuery.Event, params: List[str]) -> None:
        """Handle checkout callback"""
        try:
            sender = await event.get_sender()
            
            with get_db_session() as session:
                user_service = UserService(session)
                user = user_service.get_by_telegram_id(sender.id)
                
                if not user:
                    await event.answer("Please start the bot first", alert=True)
                    return
                
                cart_service = CartService(session)
                cart_items = cart_service.get_cart_items(user.id)
                
                if not cart_items:
                    await event.answer("Your cart is empty", alert=True)
                    return
                
                # Send message to start checkout process
                message = (
                    "🛒 **Checkout Process**\n\n"
                    "You're about to place an order. Choose a delivery location to continue.\n\n"
                    "Select a delivery location or add a new one:"
                )
                
                # Create keyboard with locations
                from src.bot.keyboards.location_keyboard import get_checkout_location_keyboard
                keyboard = get_checkout_location_keyboard(user.id)
                
                await event.edit(message, buttons=keyboard)
                
        except Exception as e:
            log_error("Error in handle_checkout", e, event.sender_id)
            await event.answer("An error occurred. Please try again later.", alert=True)
    
    logger.info("Cart callbacks registered") 