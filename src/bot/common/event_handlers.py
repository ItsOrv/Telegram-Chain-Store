from telethon import events
from core.models import User, Product, Order
from core.database import SessionLocal
from bot.middleware import restrict_access
from bot.utils import format_product_info
from bot.messages import Messages
from src.bot.common.keyboards import (
    RoleKeyboard, DialogKeyboards, 
    BalanceKeyboards, SupportKeyboards,
    get_role_keyboard
)
import logging

logger = logging.getLogger(__name__)

def register_handlers(client):
    """Register all event handlers"""

    @client.on(events.NewMessage(pattern=r'/start'))
    async def start_handler(event):
        sender = await event.get_sender()
        with SessionLocal() as db:
            user = db.query(User).filter(User.telegram_id == sender.id).first()
            keyboard = RoleKeyboard.get_keyboard("customer" if not user else user.role.lower())
            await event.respond(
                Messages.WELCOME if not user else Messages.WELCOME_BACK.format(
                    username=sender.username,
                    role=user.role
                ),
                buttons=keyboard
            )

    @client.on(events.CallbackQuery(pattern=r'buy_(\d+)'))
    async def buy_product_handler(event):
        product_id = int(event.pattern_match.group(1))
        with SessionLocal() as db:
            product = db.query(Product).get(product_id)
            if product and product.is_available:
                # Show order confirmation
                buttons = OrderKeyboard.get_confirmation()
                await event.respond(Messages.SELECT_QUANTITY, buttons=buttons)
            else:
                buttons = DialogKeyboard.get_error_handling()
                await event.respond(Messages.PRODUCT_NOT_AVAILABLE, buttons=buttons)

    @client.on(events.CallbackQuery(pattern=r'confirm_order_(\d+)'))
    async def confirm_order_handler(event):
        order_id = event.pattern_match.group(1)
        with SessionLocal() as db:
            order = db.query(Order).filter(Order.order_id == order_id).first()
            if order and order.status == "pending":
                # Show payment options
                buttons = PaymentKeyboard.get_payment_methods(
                    order.total_amount,
                    order.user.balance
                )
                await event.edit(Messages.ORDER_CONFIRMED.format(order_id=order_id), 
                               buttons=buttons)
            else:
                buttons = DialogKeyboard.get_error_handling()
                await event.edit(Messages.ORDER_NOT_FOUND, buttons=buttons)

    @client.on(events.CallbackQuery(pattern="retry"))
    async def handle_retry(event):
        buttons = DialogKeyboard.get_retry_cancel()
        await event.edit(Messages.RETRY_MESSAGE, buttons=buttons)

    @client.on(events.CallbackQuery(pattern="confirm_action"))
    async def handle_confirmation(event):
        buttons = BaseKeyboard.get_confirmation()
        await event.edit(Messages.CONFIRM_ACTION, buttons=buttons)

    # ...rest of the handlers remain unchanged...

from telegram import Update
from telegram.ext import (
    CommandHandler, MessageHandler, CallbackQueryHandler,
    ConversationHandler, filters, ContextTypes, Application
)
from core.database import SessionLocal
from core.models import User, Product, Order
from bot.keyboards import get_role_keyboard, KeyboardTexts
from bot.states import *
from bot.messages import Messages
from bot.middleware import restrict_access, log_action
from bot.utils import *
from src.config.settings import settings
from telethon import events, Button
from core.models import User, Product, Order, ProductImage
from core.database import SessionLocal
from core.order_manager import OrderManager
from core.payment_manager import PaymentManager
from bot.messages import Messages
from bot.keyboards import get_role_keyboard, get_payment_keyboard
from bot.middleware import restrict_access, log_action
from bot.utils import format_product_info
import logging

logger = logging.getLogger(__name__)

@log_action
@error_handler
@rate_limit(5)  # Allow 5 requests per minute
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler"""
    user = update.effective_user
    with SessionLocal() as db:
        try:
            db_user = db.query(User).filter(User.telegram_id == user.id).first()
            if db_user:
                keyboard = get_role_keyboard(db_user.role)
                await update.message.reply_text(
                    _(Messages.WELCOME_BACK, db_user.language),
                    reply_markup=keyboard
                )
                return ConversationHandler.END
            else:
                await update.message.reply_text(
                    _(Messages.WELCOME),
                    reply_markup=get_role_keyboard("buyer")
                )
                return CHOOSE_ROLE
        except Exception as e:
            logger.error(f"Error in start handler: {e}")
            await update.message.reply_text(_(Messages.ERROR_OCCURRED))
            return ConversationHandler.END

@restrict_access(["head"])
async def manage_sellers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle seller management for head admin"""
    with SessionLocal() as db:
        sellers = db.query(User).filter(User.role == "seller").all()
        seller_list = "\n".join([f"ID: {s.id} | {s.username}" for s in sellers])
        await update.message.reply_text(f"Seller List:\n{seller_list}")

@restrict_access(["head"])
async def get_database(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle database backup request"""
    # تولید فایل پشتیبان از دیتابیس
    try:
        backup_file = "backup.db"
        await update.message.reply_document(
            document=open(backup_file, 'rb'),
            caption="Database backup file"
        )
    except Exception as e:
        await update.message.reply_text("Error creating backup")

@restrict_access(["head", "seller"])
async def get_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle report generation"""
    user_id = update.effective_user.id
    with SessionLocal() as db:
        # Generate report based on user role
        if get_user_role(db, user_id) == "head":
            # Generate admin report
            pass
        else:
            # Generate seller report
            pass

@restrict_access(["seller"])
async def add_product_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start product addition process"""
    await update.message.reply_text(Messages.ADD_PRODUCT_NAME)
    return SET_PRODUCT_NAME

@restrict_access(["buyer"])
async def show_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show available products to buyer"""
    with SessionLocal() as db:
            user = db.query(User).filter(User.telegram_id == update.effective_user.id).first()
        products = db.query(Product).filter(
            Product.city == user.city,
            Product.is_available == True
        ).all()
        
        if not products:
            await update.message.reply_text("No products available in your area.")
            return
        
        for product in products:
            await update.message.reply_text(format_product_info(product))

async def set_product_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle product name input"""
    context.user_data['product_name'] = update.message.text
    await update.message.reply_text(Messages.ADD_PRODUCT_PRICE)
    return SET_PRODUCT_PRICE

async def set_product_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle product price input"""
    try:
        price = float(update.message.text)
        context.user_data['product_price'] = price
        await update.message.reply_text(Messages.ADD_PRODUCT_DESCRIPTION)
        return SET_PRODUCT_DESCRIPTION
    except ValueError:
        await update.message.reply_text("Invalid price. Please enter a number.")
        return SET_PRODUCT_PRICE

async def set_product_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle product description input"""
    context.user_data['product_description'] = update.message.text
    await update.message.reply_text("Please send a photo of your product.")
    return SET_PRODUCT_IMAGE

async def set_product_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle product image upload"""
    photo = update.message.photo[-1]
    context.user_data['product_image'] = photo.file_id
    await update.message.reply_text("Please enter product location (city, province):")
    return SET_PRODUCT_LOCATION

async def set_product_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle product location input and save product"""
    try:
        city, province = update.message.text.split(',')
        with SessionLocal() as db:
            product = Product(
                name=context.user_data['product_name'],
                price=context.user_data['product_price'],
                description=context.user_data['product_description'],
                city=city.strip(),
                province=province.strip(),
                seller_id=update.effective_user.id
            )
            db.add(product)
            db.commit()
            
            # Add product image
            product_image = ProductImage(
                product_id=product.id,
                image_url=context.user_data['product_image']
            )
            db.add(product_image)
            db.commit()
            
        await update.message.reply_text(Messages.PRODUCT_ADDED)
        return ConversationHandler.END
    except Exception as e:
        logger.error(f"Error saving product: {e}")
        await update.message.reply_text("Error saving product. Please try again.")
        return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel the current operation"""
    await update.message.reply_text("Operation cancelled.")
    return ConversationHandler.END

def setup_handlers(application: Application):
    """Setup all handlers"""
    # Basic handlers
    application.add_handler(CommandHandler("start", start))
    
    # Head admin handlers
    application.add_handler(CommandHandler("manage_sellers", manage_sellers))
    
    # Head admin additional handlers
    application.add_handler(MessageHandler(
        filters.Regex(f"^{KeyboardTexts.HEAD_GET_DATABASE}$"),
        get_database
    ))
    application.add_handler(MessageHandler(
        filters.Regex(f"^{KeyboardTexts.HEAD_GET_REPORT}$"),
        get_report
    ))
    
    # Seller handlers
    conv_handler_product = ConversationHandler(
        entry_points=[MessageHandler(
            filters.Regex(f"^{KeyboardTexts.SELLER_ADD_CATEGORY}$"),
            add_product_start
        )],
        states={
            SET_PRODUCT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_product_name)],
            SET_PRODUCT_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_product_price)],
            SET_PRODUCT_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_product_description)],
            SET_PRODUCT_IMAGE: [MessageHandler(filters.PHOTO, set_product_image)],
            SET_PRODUCT_LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_product_location)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    application.add_handler(conv_handler_product)
    
    # Buyer handlers
    application.add_handler(MessageHandler(
        filters.Regex(f"^{KeyboardTexts.BUYER_PRODUCT_LIST}$"),
        show_products
    ))
    
    # Error handler
    application.add_error_handler(error_handler)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}")

def setup_handlers(client):
    """Setup all event handlers"""
    
    @client.on(events.NewMessage(pattern='/start'))
    @log_action
    async def start_handler(event):
        """Handle /start command"""
        sender = await event.get_sender()
        with SessionLocal() as db:
            user = db.query(User).filter(User.telegram_id == sender.id).first()
            if user:
                keyboard = get_role_keyboard(user.role)
                await event.respond(
                    Messages.WELCOME_BACK.format(username=sender.username, role=user.role),
                    buttons=keyboard
                )
            else:
                await event.respond(Messages.WELCOME, buttons=get_role_keyboard("buyer"))

    @client.on(events.NewMessage(pattern='/add_product'))
    @restrict_access(["seller"])
    async def add_product_handler(event):
        """Handle product addition"""
        sender = await event.get_sender()
        await event.respond(Messages.ADD_PRODUCT_NAME)
        
    @client.on(events.CallbackQuery(pattern=r'buy_(\d+)'))
    async def buy_product_handler(event):
        """Handle product purchase"""
        product_id = int(event.pattern_match.group(1))
        sender = await event.get_sender()
        
        with SessionLocal() as db:
            product = db.query(Product).get(product_id)
            if not product or not product.is_available:
                await event.respond(Messages.PRODUCT_NOT_AVAILABLE)
                return
                
            # Create order
            try:
                order = await OrderManager.create_order(
                    sender.id,
                    product_id,
                    1  # Default quantity
                )
                # Show payment options
                await event.respond(
                    Messages.PAYMENT_METHODS,
                    buttons=get_payment_keyboard(order.id)
                )
            except Exception as e:
                logger.error(f"Error creating order: {e}")
                await event.respond(Messages.ERROR_OCCURRED)

    @client.on(events.CallbackQuery(pattern=r'retry'))
    async def handle_retry(event):
        buttons = DialogKeyboard.get_retry_cancel()
        await event.edit(Messages.RETRY_MESSAGE, buttons=buttons)

    @client.on(events.CallbackQuery(pattern=r'confirm_action'))
    async def handle_confirmation(event):
        buttons = BaseKeyboard.get_confirmation()
        await event.edit(Messages.CONFIRM_ACTION, buttons=buttons)

from typing import Dict, List, Optional
from datetime import datetime
from core.models import User, Order, Product
from sqlalchemy.orm import Session
from src.config.security import encrypt_sensitive_data
from src.bot.common.keyboards import DialogKeyboards, BalanceKeyboards, SupportKeyboards  # Add imports

def get_user_role(db: Session, telegram_id: int) -> Optional[str]:
    """Get user role from database"""
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    return user.role if user else None

def format_product_info(product: Product) -> str:
    """Format product information for display"""
    return (
        f"📦 {product.name}\n"
        f"💰 Price: {product.price} {product.currency}\n"
        f"📍 Location: {product.city}, {product.province}\n"
        f"ℹ️ {product.description}\n"
    )

def format_order_info(order: Order) -> str:
    """Format order information for display"""
    return (
        f"🛍 Order #{order.id}\n"
        f"💰 Total: {order.total_price}\n"
        f"📦 Status: {order.status}\n"
        f"🕒 Created: {order.created_at}\n"
    )

def generate_order_id() -> str:
    """Generate unique order ID"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"ORD-{timestamp}"

def encrypt_delivery_address(address: str) -> str:
    """Encrypt delivery address"""
    return encrypt_sensitive_data(address)

def validate_product_data(data: Dict) -> List[str]:
    """Validate product data"""
    errors = []
    required_fields = ['name', 'price', 'description', 'city', 'province']
    for field in required_fields:
        if field not in data or not data[field]:
            errors.append(f"Missing {field}")
    return errors

async def handle_error(event):
    """Handle error cases"""
    # ...existing code...
    buttons = DialogKeyboards.get_retry_cancel()
    await event.edit(Messages.ERROR_OCCURRED, buttons=buttons)

async def show_balance_options(event):
    """Show balance charge options"""
    # ...existing code...
    buttons = BalanceKeyboards.get_charge_options()
    await event.edit(Messages.SELECT_CHARGE_METHOD, buttons=buttons)

async def show_charge_amounts(event):
    """Show available charge amounts"""
    # ...existing code...
    buttons = BalanceKeyboards.get_charge_amounts()
    await event.edit(Messages.SELECT_AMOUNT, buttons=buttons)
