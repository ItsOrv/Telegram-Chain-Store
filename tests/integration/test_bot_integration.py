import pytest
import asyncio
from telethon import TelegramClient, events
from telethon.tl.custom import Button
from src.core.database import SessionLocal
from src.core.models import (
    User, Product, Order, UserRole, OrderStatus, 
    Payment, PaymentStatus, Category, CartItem
)
from src.config.settings import get_settings
from decimal import Decimal
from datetime import datetime
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get settings from main .env
settings = get_settings()
API_ID = settings.API_ID
API_HASH = settings.API_HASH
BOT_TOKEN = settings.BOT_TOKEN
HEAD_ADMIN_ID = settings.HEAD_ADMIN_ID

@pytest.fixture(scope="session")
async def client():
    """Create a test client"""
    client = TelegramClient(
        'test_session',
        API_ID,
        API_HASH
    ).start(bot_token=BOT_TOKEN)
    await client.connect()
    yield client
    await client.disconnect()

@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
def db():
    """Create a database session"""
    db = SessionLocal()
    yield db
    db.close()

@pytest.fixture(scope="function")
async def test_user(db):
    """Create a test user"""
    user = User(
        telegram_id=HEAD_ADMIN_ID,
        username="test_user",
        role=UserRole.CUSTOMER,
        status="ACTIVE",
        joined_at=datetime.utcnow()
    )
    db.add(user)
    db.commit()
    yield user
    db.query(User).filter(User.telegram_id == HEAD_ADMIN_ID).delete()
    db.commit()

@pytest.mark.asyncio
async def test_complete_flow(client, db):
    """Test complete flow including all user roles and functionalities"""
    
    # 1. Test Admin Flow
    async def test_admin():
        # First check if admin exists
        existing_admin = db.query(User).filter(User.telegram_id == HEAD_ADMIN_ID).first()
        if existing_admin:
            return existing_admin

        admin = User(
            telegram_id=HEAD_ADMIN_ID,
            username="admin",
            role=UserRole.ADMIN,
            status="ACTIVE"
        )
        db.add(admin)
        db.commit()

        async with client.conversation(HEAD_ADMIN_ID) as conv:
            # Test start command
            await conv.send_message("/start")
            response = await conv.get_response()
            assert "Welcome" in response.text
            assert isinstance(response.buttons, list)

            # Test manage users
            await conv.send_message("👤 Manage Users")
            response = await conv.get_response()
            assert "Users Stats" in response.text

            # Test manage sellers
            await conv.send_message("👥 Manage Sellers")
            response = await conv.get_response()
            assert "Sellers Stats" in response.text

            # Test add seller
            await conv.send_message("➕ Add New Seller")
            response = await conv.get_response()
            assert "Enter seller ID" in response.text

            # Test back to main menu
            await conv.send_message("🔙 Back to Main Menu")
            response = await conv.get_response()
            assert isinstance(response.buttons, list)

        return admin

    # 2. Test Seller Flow
    async def test_seller(admin):
        seller = User(
            telegram_id="123456789",
            username="test_seller",
            role=UserRole.SELLER,
            status="ACTIVE"
        )
        db.add(seller)
        db.commit()

        # Create test category
        category = Category(
            name="Test Category",
            description="Test Category Description",
            slug="test-category"
        )
        db.add(category)
        db.commit()

        async with client.conversation(seller.telegram_id) as conv:
            # Test start command
            await conv.send_message("/start")
            response = await conv.get_response()
            assert isinstance(response.buttons, list)

            # Test add product
            await conv.send_message("➕ Add Product")
            response = await conv.get_response()
            assert "Enter product name" in response.text

            # Add product details
            await conv.send_message("Test Product")
            response = await conv.get_response()
            assert "Enter price" in response.text

            await conv.send_message("100")
            response = await conv.get_response()
            assert "Enter description" in response.text

            await conv.send_message("Test Description")
            response = await conv.get_response()
            assert "Select category" in response.text

            # Select category
            await conv.send_message(str(category.id))
            response = await conv.get_response()
            assert "Product added" in response.text

        return seller

    # 3. Test Customer Flow
    async def test_customer(seller):
        customer = User(
            telegram_id="987654321",
            username="test_customer",
            role=UserRole.CUSTOMER,
            status="ACTIVE",
            balance=Decimal("1000.00")
        )
        db.add(customer)
        db.commit()

        # Get the product
        product = db.query(Product).filter(Product.seller_id == seller.id).first()

        async with client.conversation(customer.telegram_id) as conv:
            # Test start
            await conv.send_message("/start")
            response = await conv.get_response()
            assert isinstance(response.buttons, list)

            # Browse products
            await conv.send_message("🛍 Browse Products")
            response = await conv.get_response()
            assert "Test Product" in response.text

            # Add to cart
            await conv.send_message(f"add_to_cart_{product.id}")
            response = await conv.get_response()
            assert "Added to cart" in response.text

            # View cart
            await conv.send_message("🛒 View Cart")
            response = await conv.get_response()
            assert "Test Product" in response.text
            assert "100.00" in response.text

            # Checkout
            await conv.send_message("💳 Checkout")
            response = await conv.get_response()
            assert "Payment Methods" in response.text

            # Pay with balance
            await conv.send_message("💰 Pay with Balance")
            response = await conv.get_response()
            assert "Order confirmed" in response.text

            # Verify order in database
            order = db.query(Order).filter(
                Order.buyer_id == customer.id,
                Order.product_id == product.id
            ).first()
            assert order is not None
            assert order.status == OrderStatus.PENDING_SELLER_CONFIRMATION

            # Verify payment
            payment = db.query(Payment).filter(
                Payment.user_id == customer.id,
                Payment.status == PaymentStatus.CONFIRMED
            ).first()
            assert payment is not None
            assert payment.amount == Decimal("100.00")

        return customer

    # 4. Test Seller Order Management
    async def test_seller_order_management(seller, customer):
        async with client.conversation(seller.telegram_id) as conv:
            # View orders
            await conv.send_message("📦 View Orders")
            response = await conv.get_response()
            assert "Test Product" in response.text

            # Accept order
            order = db.query(Order).filter(
                Order.buyer_id == customer.id
            ).first()
            await conv.send_message(f"accept_order_{order.id}")
            response = await conv.get_response()
            assert "Order accepted" in response.text

            # Verify order status
            order = db.query(Order).get(order.id)
            assert order.status == OrderStatus.CONFIRMED

    # Run all flows in sequence
    admin = await test_admin()
    seller = await test_seller(admin)
    customer = await test_customer(seller)
    await test_seller_order_management(seller, customer)

    # Cleanup
    db.query(Order).filter(Order.buyer_id == customer.id).delete()
    db.query(Payment).filter(Payment.user_id == customer.id).delete()
    db.query(CartItem).filter(CartItem.user_id == customer.id).delete()
    db.query(Product).filter(Product.seller_id == seller.id).delete()
    db.query(Category).delete()
    db.query(User).filter(User.id.in_([seller.id, customer.id])).delete()
    db.commit()

def test_database_integrity(db):
    """Test database model relationships"""
    # Create test data
    seller = User(
        telegram_id="123456",
        username="test_seller",
        role=UserRole.SELLER,
        status="ACTIVE"
    )
    db.add(seller)
    db.commit()

    product = Product(
        name="Test Product",
        price=Decimal("100.00"),
        description="Test Description",
        seller_id=seller.id,
        is_available=True
    )
    db.add(product)
    db.commit()

    # Test relationships
    assert product.seller == seller
    assert seller.products[0] == product

    # Cleanup
    db.query(Product).filter(Product.id == product.id).delete()
    db.query(User).filter(User.id == seller.id).delete()
    db.commit()

if __name__ == "__main__":
    pytest.main(["-v", "test_bot_integration.py"]) 