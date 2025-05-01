from telethon import events, Button
from src.utils.logger import setup_logger, log_error
from src.core.database import get_db_session
from src.core.services.product_service import ProductService
from src.core.services.cart_service import CartService
from src.core.services.user_service import UserService
from src.bot.handlers.callback_router import register_callback
from typing import List

# Initialize logger
logger = setup_logger("product_callbacks")

def register_product_callbacks():
    """Register product-related callback handlers"""
    logger.info("Registering product callbacks")
    
    @register_callback("view_product")
    async def handle_view_product(event: events.CallbackQuery.Event, params: List[str]) -> None:
        """Handle view product callback"""
        try:
            if len(params) < 1:
                await event.answer("Invalid product ID", alert=True)
                return
                
            product_id = int(params[0])
            sender = await event.get_sender()
            
            with get_db_session() as session:
                product_service = ProductService(session)
                product = product_service.get_by_id(product_id)
                
                if not product:
                    await event.answer("Product not found", alert=True)
                    return
                
                # Increment views counter
                product_service.increment_views(product_id)
                
                # Build product details message
                message = (
                    f"🛍️ **{product.name}**\n\n"
                    f"💰 Price: ${product.price:.2f}\n"
                    f"📦 Stock: {product.stock}\n\n"
                    f"📝 **Description:**\n{product.description or 'No description available'}\n\n"
                    f"📍 Location: {product.city.name}, {product.area}\n"
                    f"👤 Seller: {product.seller.display_name}\n"
                )
                
                # Create keyboard with product actions
                from src.bot.keyboards.product_keyboard import get_product_details_keyboard
                keyboard = get_product_details_keyboard(product_id)
                
                await event.edit(message, buttons=keyboard)
                
        except Exception as e:
            log_error("Error in handle_view_product", e, event.sender_id)
            await event.answer("An error occurred. Please try again later.", alert=True)
    
    @register_callback("add_to_cart")
    async def handle_add_to_cart(event: events.CallbackQuery.Event, params: List[str]) -> None:
        """Handle add to cart callback"""
        try:
            if len(params) < 1:
                await event.answer("Invalid product ID", alert=True)
                return
                
            product_id = int(params[0])
            quantity = int(params[1]) if len(params) > 1 else 1
            sender = await event.get_sender()
            
            with get_db_session() as session:
                user_service = UserService(session)
                user = user_service.get_by_telegram_id(sender.id)
                
                if not user:
                    await event.answer("Please start the bot first", alert=True)
                    return
                
                product_service = ProductService(session)
                product = product_service.get_by_id(product_id)
                
                if not product:
                    await event.answer("Product not found", alert=True)
                    return
                
                if not product.is_in_stock:
                    await event.answer("This product is out of stock", alert=True)
                    return
                
                cart_service = CartService(session)
                cart_service.add_to_cart(user.id, product_id, quantity)
                
                await event.answer(f"{product.name} added to your cart!")
                
                # Return to product view with updated buttons
                from src.bot.keyboards.product_keyboard import get_product_details_keyboard
                keyboard = get_product_details_keyboard(product_id, in_cart=True)
                
                await event.edit(buttons=keyboard)
                
        except Exception as e:
            log_error("Error in handle_add_to_cart", e, event.sender_id)
            await event.answer("An error occurred. Please try again later.", alert=True)
    
    @register_callback("remove_from_cart")
    async def handle_remove_from_cart(event: events.CallbackQuery.Event, params: List[str]) -> None:
        """Handle remove from cart callback"""
        try:
            if len(params) < 1:
                await event.answer("Invalid product ID", alert=True)
                return
                
            product_id = int(params[0])
            sender = await event.get_sender()
            
            with get_db_session() as session:
                user_service = UserService(session)
                user = user_service.get_by_telegram_id(sender.id)
                
                if not user:
                    await event.answer("Please start the bot first", alert=True)
                    return
                
                product_service = ProductService(session)
                product = product_service.get_by_id(product_id)
                
                if not product:
                    await event.answer("Product not found", alert=True)
                    return
                
                cart_service = CartService(session)
                cart_service.remove_from_cart(user.id, product_id)
                
                await event.answer(f"{product.name} removed from your cart!")
                
                # Return to product view with updated buttons
                from src.bot.keyboards.product_keyboard import get_product_details_keyboard
                keyboard = get_product_details_keyboard(product_id, in_cart=False)
                
                await event.edit(buttons=keyboard)
                
        except Exception as e:
            log_error("Error in handle_remove_from_cart", e, event.sender_id)
            await event.answer("An error occurred. Please try again later.", alert=True)
    
    @register_callback("browse_category")
    async def handle_browse_category(event: events.CallbackQuery.Event, params: List[str]) -> None:
        """Handle browse category callback"""
        try:
            if len(params) < 1:
                await event.answer("Invalid category ID", alert=True)
                return
                
            category_id = int(params[0])
            page = int(params[1]) if len(params) > 1 else 1
            sender = await event.get_sender()
            
            with get_db_session() as session:
                product_service = ProductService(session)
                products = product_service.get_by_category(category_id, page=page, per_page=5)
                category = product_service.get_category_by_id(category_id)
                
                if not category:
                    await event.answer("Category not found", alert=True)
                    return
                
                if not products:
                    message = f"No products found in category: {category.name}"
                    await event.edit(message)
                    return
                
                # Build products list message
                message = f"📂 **Category: {category.name}**\n\n"
                
                for i, product in enumerate(products, 1):
                    message += (
                        f"{i}. **{product.name}**\n"
                        f"   💰 Price: ${product.price:.2f}\n"
                        f"   📍 Location: {product.city.name}, {product.area}\n\n"
                    )
                
                # Create keyboard with product list
                from src.bot.keyboards.product_keyboard import get_product_list_keyboard
                keyboard = get_product_list_keyboard(products, category_id, page)
                
                await event.edit(message, buttons=keyboard)
                
        except Exception as e:
            log_error("Error in handle_browse_category", e, event.sender_id)
            await event.answer("An error occurred. Please try again later.", alert=True)
    
    @register_callback("browse")
    async def handle_browse_products(event: events.CallbackQuery.Event, params: List[str]) -> None:
        """Handle browse products callback"""
        try:
            action = params[0] if params else None
            
            if action == "products":
                # Show product categories or all products
                sender = await event.get_sender()
                
                with get_db_session() as session:
                    product_service = ProductService(session)
                    categories = product_service.get_categories()
                    
                    if categories:
                        # Show categories
                        message = "🏷️ **دسته‌بندی محصولات**\n\nلطفاً یک دسته‌بندی را برای مشاهده محصولات انتخاب کنید:"
                        
                        keyboard = []
                        # Create buttons for categories (2 per row)
                        row = []
                        for i, category in enumerate(categories):
                            if i % 2 == 0 and i > 0:
                                keyboard.append(row)
                                row = []
                            row.append(Button.inline(category.name, f"browse_category:{category.id}"))
                        
                        if row:  # Add any remaining categories
                            keyboard.append(row)
                        
                        # Add "All Products" button
                        keyboard.append([Button.inline("🛒 همه محصولات", "browse_all:1")])
                        
                        # Add back button
                        keyboard.append([Button.inline("« بازگشت به منوی اصلی", "navigation:main_menu")])
                        
                        await event.edit(message, buttons=keyboard)
                    else:
                        # No categories, show all products directly
                        return await handle_browse_all(event, ["1"])  # Page 1
            else:
                await event.answer("عملیات نامعتبر", alert=True)
                
        except Exception as e:
            log_error("Error in handle_browse_products", e, event.sender_id)
            await event.answer("خطایی رخ داد. لطفاً دوباره تلاش کنید.", alert=True)
    
    @register_callback("browse_all")
    async def handle_browse_all(event: events.CallbackQuery.Event, params: List[str]) -> None:
        """Handle browse all products callback"""
        try:
            page = int(params[0]) if params else 1
            sender = await event.get_sender()
            
            with get_db_session() as session:
                product_service = ProductService(session)
                products = product_service.get_products(page=page, per_page=5)
                total_count = product_service.count_products()
                
                if not products:
                    message = "هیچ محصولی یافت نشد."
                    await event.edit(message, buttons=[[Button.inline("« بازگشت", "navigation:main_menu")]])
                    return
                
                # Build product list message
                message = f"🛍️ **محصولات**\n\n"
                
                for i, product in enumerate(products, 1):
                    message += (
                        f"{i}. **{product.name}**\n"
                        f"   💰 قیمت: {product.price:,} تومان\n"
                        f"   📍 مکان: {product.city.name if hasattr(product, 'city') else 'نامشخص'}\n\n"
                    )
                
                # Calculate pagination
                total_pages = (total_count + 4) // 5  # Ceiling division
                
                # Create keyboard with pagination
                keyboard = []
                
                # Add pagination buttons
                row = []
                if page > 1:
                    row.append(Button.inline("« قبلی", f"browse_all:{page-1}"))
                
                if page < total_pages:
                    row.append(Button.inline("بعدی »", f"browse_all:{page+1}"))
                
                if row:
                    keyboard.append(row)
                
                # Add products as buttons
                for product in products:
                    keyboard.append([Button.inline(f"🛒 {product.name}", f"view_product:{product.id}")])
                
                # Add filter and back buttons
                keyboard.append([
                    Button.inline("🔍 فیلتر محصولات", "browse:filter"),
                    Button.inline("🏷️ دسته‌بندی‌ها", "browse:products")
                ])
                
                keyboard.append([Button.inline("« بازگشت به منوی اصلی", "navigation:main_menu")])
                
                await event.edit(message, buttons=keyboard)
                
        except Exception as e:
            log_error("Error in handle_browse_all", e, event.sender_id)
            await event.answer("خطایی رخ داد. لطفاً دوباره تلاش کنید.", alert=True)
            
    logger.info("Product callbacks registered") 