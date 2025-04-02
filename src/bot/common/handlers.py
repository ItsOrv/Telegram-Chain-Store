from telethon import TelegramClient, events, Button
from datetime import datetime
from src.config.settings import get_settings
from src.bot.common.messages import Messages
from src.bot.common.keyboards import (
    RoleKeyboard, DialogKeyboards, 
    LocationKeyboards, BaseKeyboard
)
from src.core.database import SessionLocal
from src.core.models import (
    User, Product, Order, Payment, 
    UserRole, OrderStatus, PaymentStatus
)
from src.bot.utils import get_user_role
from src.bot.common.dialogs import ProductDialog
from src.bot.handlers.location_handler import LocationHandler
from src.bot.handlers.category_handler import CategoryHandler
from src.bot.handlers.user_handler import UserHandler
from src.bot.handlers.backup_handler import BackupHandler
from src.bot.handlers.seller_handler import SellerHandler
from src.bot.handlers.product_handler import ProductHandler
from src.utils.logger import (
    APP_LOGGER as logger,
    log_user_action,
    log_error,
    log_ui_event,
    log_product_action,
    log_order_action,
    log_admin_action,
    log_function_execution
)
from src.bot.common.middleware import (
    error_handler,
    log_action,
    log_callback_query,
    log_message
)
import traceback

@log_function_execution()
def setup_handlers(client: TelegramClient):
    """Setup event handlers for the bot"""
    logger.info("Setting up bot event handlers")
    
    # Initialize handlers
    location_handler = LocationHandler(client)
    category_handler = CategoryHandler(client)
    user_handler = UserHandler(client)
    backup_handler = BackupHandler(client)
    seller_handler = SellerHandler(client)
    product_handler = ProductHandler(client)
    settings = get_settings()
    
    @client.on(events.NewMessage(pattern='/start'))
    @error_handler
    @log_message
    async def start(event):
        try:
            user_id = event.sender_id
            logger.info(f"Start command received from user {user_id}")
            log_user_action(user_id, "START_COMMAND")
            
            with SessionLocal() as db:
                user = db.query(User).filter(User.telegram_id == str(user_id)).first()
                
                # Check if this is the head admin
                is_head_admin = str(user_id) == str(settings.HEAD_ADMIN_ID)
                
                if user:
                    # Check user status first (without showing keyboard)
                    if user.status == 'BANNED' and not is_head_admin:
                        logger.warning(f"Banned user {user_id} attempted to access the bot")
                        log_user_action(user_id, "BANNED_USER_ACCESS_ATTEMPT")
                        await event.respond(Messages.USER_BANNED.format(
                            support_username=settings.SUPPORT_USERNAME
                        ))
                        return
                    elif user.status == 'SUSPENDED' and not is_head_admin:
                        logger.warning(f"Suspended user {user_id} attempted to access the bot")
                        log_user_action(user_id, "SUSPENDED_USER_ACCESS_ATTEMPT")
                        await event.respond(Messages.USER_SUSPENDED.format(
                            support_username=settings.SUPPORT_USERNAME
                        ))
                        return
                    
                    if is_head_admin:
                        logger.info(f"Head admin {user_id} accessed the bot")
                        log_admin_action(user_id, "HEAD_ADMIN_ACCESS")
                        # Update role to ADMIN if this is head admin
                        user.role = UserRole.ADMIN
                        user.status = 'ACTIVE'
                        db.commit()
                        log_admin_action(user_id, "UPDATE_ROLE", details={"role": "ADMIN"})
                    
                    # Check location for non-admin users
                    if not is_head_admin:
                        has_location = await location_handler.check_user_location(event)
                        if not has_location:
                            logger.info(f"User {user_id} needs to set location")
                            return

                    # Show appropriate keyboard
                    role = user.role
                    buttons = RoleKeyboard.get_keyboard(user.role.lower())
                    logger.info(f"Showing {role.lower()} keyboard to user {user_id}")
                    log_ui_event(user_id, "SHOW_KEYBOARD", "main_menu", {"role": role.lower()})
                    await event.respond(
                        Messages.WELCOME_BACK.format(
                            username=user.username, 
                            role=role.lower()
                        ), 
                        buttons=buttons
                    )
                else:
                    # Create new user with ACTIVE status
                    logger.info(f"Creating new user record for {user_id}")
                    log_user_action(user_id, "NEW_USER_REGISTRATION")
                    
                    new_user = User(
                        telegram_id=str(user_id),
                        username=event.sender.username,
                        role=UserRole.ADMIN if is_head_admin else UserRole.CUSTOMER,
                        status='ACTIVE',
                        joined_at=datetime.utcnow()
                    )
                    db.add(new_user)
                    db.commit()
                    logger.info(f"New user {user_id} added to database")
                    
                    if is_head_admin:
                        log_admin_action(user_id, "NEW_ADMIN_REGISTRATION")
                        buttons = RoleKeyboard.get_keyboard("admin")
                        log_ui_event(user_id, "SHOW_KEYBOARD", "main_menu", {"role": "admin"})
                        await event.respond(
                            Messages.WELCOME_BACK.format(
                                username=new_user.username,
                                role="admin"
                            ),
                            buttons=buttons
                        )
                    else:
                        await location_handler.show_provinces(event)
        except Exception as e:
            log_error(f"Error in start handler", e, user_id)
            logger.error(f"Exception in start handler: {str(e)}")
            logger.error(traceback.format_exc())
            buttons = DialogKeyboards.get_error_handling()
            await event.respond(Messages.ERROR_OCCURRED, buttons=buttons)

    @client.on(events.NewMessage(pattern='/help'))
    @error_handler
    @log_message
    async def help(event):
        user_id = event.sender_id
        logger.info(f"Help command received from user {user_id}")
        log_user_action(user_id, "HELP_COMMAND")
        await event.respond(Messages.WELCOME)

    @client.on(events.NewMessage(pattern='/add_product'))
    @error_handler
    @log_message
    async def add_product(event):
        user_id = event.sender_id
        logger.info(f"Add product command received from user {user_id}")
        log_user_action(user_id, "ADD_PRODUCT_COMMAND")
        
        with SessionLocal() as db:
            user = db.query(User).filter(User.telegram_id == str(user_id)).first()
            if not user or user.role != UserRole.SELLER:
                logger.warning(f"Unauthorized add_product attempt by user {user_id}")
                log_user_action(user_id, "UNAUTHORIZED_ADD_PRODUCT")
                await event.respond(Messages.UNAUTHORIZED)
                return
            
            # Start product creation dialog
            logger.info(f"Starting product creation dialog for user {user_id}")
            log_product_action(user_id, "START_PRODUCT_CREATION")
            await event.respond(Messages.ADD_PRODUCT_NAME)

    @client.on(events.NewMessage(pattern='/my_orders'))
    @error_handler
    @log_message
    async def view_orders(event):
        user_id = event.sender_id
        logger.info(f"My orders command received from user {user_id}")
        log_user_action(user_id, "VIEW_ORDERS_COMMAND")
        
        with SessionLocal() as db:
            user = db.query(User).filter(User.telegram_id == str(user_id)).first()
            if not user:
                logger.warning(f"Unauthorized view_orders attempt by user {user_id}")
                log_user_action(user_id, "UNAUTHORIZED_VIEW_ORDERS")
                await event.respond(Messages.UNAUTHORIZED)
                return
            
            if user.role == UserRole.CUSTOMER:
                logger.info(f"Retrieving customer orders for user {user_id}")
                log_order_action(user_id, "VIEW_CUSTOMER_ORDERS")
                orders = db.query(Order).filter(Order.buyer_id == user.id).all()
            elif user.role == UserRole.SELLER:
                logger.info(f"Retrieving seller orders for user {user_id}")
                log_order_action(user_id, "VIEW_SELLER_ORDERS")
                orders = db.query(Order).join(Product).filter(Product.seller_id == user.id).all()
            else:
                logger.info(f"Retrieving all orders for admin {user_id}")
                log_admin_action(user_id, "VIEW_ALL_ORDERS")
                orders = db.query(Order).all()
            
            logger.info(f"Found {len(orders)} orders for user {user_id}")

    @client.on(events.CallbackQuery)
    @error_handler
    @log_callback_query
    async def callback_handler(event):
        """Handle inline button callbacks"""
        data = event.data.decode()
        user_id = event.sender_id
        
        logger.info(f"Callback query from user {user_id}: {data}")
        
        with SessionLocal() as db:
            user = db.query(User).filter(User.telegram_id == str(user_id)).first()
            if not user:
                logger.warning(f"Unauthorized callback from user {user_id}")
                log_user_action(user_id, "UNAUTHORIZED_CALLBACK")
                await event.answer(Messages.UNAUTHORIZED, alert=True)
                return

            # Handle different button callbacks
            if data in ["confirm", "cancel", "retry"]:
                log_ui_event(user_id, "DIALOG_ACTION", "button", {"action": data})
                
                if data == "confirm":
                    logger.info(f"User {user_id} confirmed action")
                    buttons = BaseKeyboard.get_confirmation("yes", "no")
                    await event.edit(Messages.CONFIRM_ACTION, buttons=buttons)
                elif data == "cancel":
                    logger.info(f"User {user_id} cancelled action")
                    buttons = RoleKeyboard.get_keyboard(user.role.lower())
                    await event.edit(Messages.ACTION_CANCELLED, buttons=buttons)
                else:  # retry
                    logger.info(f"User {user_id} requested retry")
                    buttons = DialogKeyboards.get_retry_cancel()
                    await event.edit(Messages.RETRY_ACTION, buttons=buttons)
                    
            elif data.startswith("edit_product_") or data.startswith("delete_product_"):
                product_id = data.split("_")[-1]
                log_product_action(user_id, f"PRODUCT_ACTION_{data.split('_')[0].upper()}", product_id)
                logger.info(f"User {user_id} initiated {data.split('_')[0]} for product {product_id}")
                await product_handler.handle_product_action(event, user_id)
                
            elif data.startswith("product_"):
                log_product_action(user_id, "PRODUCT_VIEW", data.split("_")[-1])
                await handle_product_action(event, data, user)
                
            elif data.startswith("order_"):
                order_id = data.split("_")[-1]
                log_order_action(user_id, "ORDER_ACTION", order_id)
                await handle_order_action(event, data, user)

    async def handle_confirmation(event, action):
        """Handle confirmation button actions"""
        user_id = event.sender_id
        logger.info(f"User {user_id} handling confirmation: {action}")
        log_ui_event(user_id, "CONFIRMATION", "dialog", {"action": action})
        
        if action == "confirm":
            await event.answer("Action confirmed!")
            # Handle the confirmation
        elif action == "cancel":
            await event.answer("Action cancelled!")
            # Handle the cancellation
        elif action == "retry":
            await event.answer("Retrying...")
            # Handle the retry

    @client.on(events.CallbackQuery(pattern="back_to_main"))
    @error_handler
    @log_callback_query
    async def handle_back_to_main(event):
        """Handle back to main menu"""
        try:
            user_id = event.sender_id
            logger.info(f"User {user_id} returning to main menu")
            log_ui_event(user_id, "NAVIGATION", "main_menu", {"action": "back_to_main"})
            
            with SessionLocal() as db:
                user = db.query(User).filter(User.telegram_id == str(user_id)).first()
                if user:
                    buttons = RoleKeyboard.get_keyboard(user.role.lower())
                    await event.edit(
                        Messages.WELCOME_BACK.format(
                            username=user.username,
                            role=user.role.lower()
                        ),
                        buttons=buttons
                    )
        except Exception as e:
            log_error(f"Error in handle_back_to_main", e, user_id)
            buttons = DialogKeyboards.get_error_handling()
            await event.edit(Messages.ERROR_OCCURRED, buttons=buttons)

    logger.info("All handlers have been set up successfully")
    return True  # Indicate successful handler setup
