import os
import sys
import pytest
import random
import string
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine, text
from decimal import Decimal
from datetime import datetime, timedelta, timezone

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)

from src.core.models import (
    User, Product, Order, Category, City, Payment, Review, CartItem,
    UserRole, OrderStatus, PaymentStatus, PaymentMethod, UserStatus,
    ProductImage, Notification, Province
)
from src.core.database import Base, get_db

# Create test database engine
TEST_DATABASE_URL = "mysql+pymysql://chainstore_user:chainstore123@localhost/chainstore_db"
engine = create_engine(TEST_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def generate_unique_telegram_id():
    """Generate unique telegram ID for testing"""
    return random.randint(10000000, 999999999)

def generate_unique_slug(base_slug: str):
    """Generate unique slug with random suffix"""
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"{base_slug}-{random_suffix}"

def generate_unique_transaction_id():
    """Generate unique transaction ID for testing"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"TEST_TX_{timestamp}_{random_suffix}"

@pytest.fixture(scope="session", autouse=True)
def setup_db():
    """Setup database once for all tests"""
    # Drop all tables first to ensure clean state
    Base.metadata.drop_all(bind=engine)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    yield
    
    # Cleanup after all tests
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db():
    """Create fresh database session for each test"""
    connection = engine.connect()
    transaction = connection.begin()
    session = SessionLocal(bind=connection)
    
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()

@pytest.fixture
def sample_data(db: Session):
    """Create comprehensive sample data for testing"""
    # Create provinces
    tehran_province = Province(name="Tehran Province")
    isfahan_province = Province(name="Isfahan Province")
    db.add_all([tehran_province, isfahan_province])
    db.commit()

    # Create cities
    tehran = City(name="Tehran", province_id=tehran_province.id)
    isfahan = City(name="Isfahan", province_id=isfahan_province.id)
    db.add_all([tehran, isfahan])
    db.commit()

    # Create users with different roles and random telegram_ids
    users = {
        'admin': User(
            telegram_id=generate_unique_telegram_id(),
            username="admin_user",
            role=UserRole.ADMIN,
            phone_number="+989123456789",
            balance=1000.0,
            status=UserStatus.ACTIVE
        ),
        'seller': User(
            telegram_id=generate_unique_telegram_id(),
            username="seller_user",
            role=UserRole.SELLER,
            phone_number="+989123456788",
            balance=500.0,
            status=UserStatus.ACTIVE
        ),
        'customer': User(
            telegram_id=generate_unique_telegram_id(),
            username="customer_user",
            role=UserRole.CUSTOMER,
            phone_number="+989123456787",
            balance=200.0,
            status=UserStatus.ACTIVE
        )
    }
    db.add_all(users.values())
    db.commit()

    # Create parent category first
    electronics = Category(
        name="Electronics",
        slug=generate_unique_slug("electronics")
    )
    db.add(electronics)
    db.commit()

    # Create child category after parent is committed
    phones = Category(
        name="Phones",
        slug=generate_unique_slug("phones"),
        parent_id=electronics.id
    )
    db.add(phones)
    db.commit()

    # Create product
    product = Product(
        seller_id=users['seller'].id,
        category_id=phones.id,
        name="Test Phone",
        description="A test phone",
        price=Decimal('500.00'),
        stock=10,
        city_id=tehran.id,
        min_order=1,
        max_order=5
    )
    db.add(product)
    db.commit()

    # Add product image
    image = ProductImage(
        product_id=product.id,
        image_url="https://example.com/test.jpg"
    )
    db.add(image)
    db.commit()

    return {
        'provinces': {'tehran_province': tehran_province, 'isfahan_province': isfahan_province},
        'cities': {'tehran': tehran, 'isfahan': isfahan},
        'users': users,
        'categories': {'electronics': electronics, 'phones': phones},
        'products': {'phone': product},
        'images': {'phone_image': image}
    }

def test_user_management(db: Session):
    """Test user CRUD operations and relationships"""
    # Test user creation with random telegram_id
    new_user = User(
        telegram_id=generate_unique_telegram_id(),
        username="new_user",
        role=UserRole.CUSTOMER,
        status=UserStatus.ACTIVE
    )
    db.add(new_user)
    db.commit()

    # Test user retrieval
    assert db.query(User).filter_by(telegram_id=new_user.telegram_id).first() is not None

    # Test user update
    new_user.balance = Decimal('100.00')
    db.commit()
    assert new_user.balance == Decimal('100.00')

    # Test user soft delete
    new_user.deleted_at = datetime.now(timezone.utc)
    db.commit()
    assert new_user.deleted_at is not None

def test_product_management(db: Session, sample_data):
    """Test product CRUD and related operations"""
    seller = sample_data['users']['seller']
    category = sample_data['categories']['phones']
    city = sample_data['cities']['tehran']

    # Test product creation with multiple images
    product = Product(
        seller_id=seller.id,
        category_id=category.id,
        name="New Phone",
        price=Decimal('600.00'),
        stock=15,
        city_id=city.id
    )
    db.add(product)
    db.commit()

    # Add multiple images
    images = [
        ProductImage(product_id=product.id, image_url=f"https://example.com/img{i}.jpg")
        for i in range(3)
    ]
    db.add_all(images)
    db.commit()

    # Verify product and images
    loaded_product = db.query(Product).filter_by(id=product.id).first()
    assert len(loaded_product.images) == 3
    assert loaded_product.seller == seller

def test_order_flow(db: Session, sample_data):
    """Test complete order flow with payment"""
    customer = sample_data['users']['customer']
    product = sample_data['products']['phone']
    initial_stock = product.stock

    # Create order
    order = Order(
        buyer_id=customer.id,
        product_id=product.id,
        quantity=2,
        unit_price=product.price,
        total_price=product.price * 2,
        status=OrderStatus.PENDING_SELLER_CONFIRMATION
    )
    db.add(order)
    db.commit()

    # Create payment with unique transaction ID
    payment = Payment(
        order_id=order.id,
        amount=order.total_price,
        status=PaymentStatus.PENDING,
        transaction_id=generate_unique_transaction_id()
    )
    db.add(payment)
    db.commit()

    # Update order status through states
    status_flow = [
        OrderStatus.PENDING_ADMIN_CONFIRMATION,
        OrderStatus.TRANSFERRING_TO_PUBLIC_LOCATION,
        OrderStatus.AT_PUBLIC_LOCATION_PENDING_PICKUP,
        OrderStatus.COMPLETED
    ]
    for status in status_flow:
        order.status = status
        db.commit()
        assert order.status == status

    # Verify final state
    assert order.status == OrderStatus.COMPLETED
    assert payment.order_id == order.id

def test_cart_operations(db: Session, sample_data):
    """Test shopping cart operations"""
    customer = sample_data['users']['customer']
    product = sample_data['products']['phone']

    # Add to cart
    cart_item = CartItem(
        user_id=customer.id,
        product_id=product.id,
        quantity=1
    )
    db.add(cart_item)
    db.commit()

    # Verify cart
    user_cart = db.query(CartItem).filter_by(user_id=customer.id).all()
    assert len(user_cart) == 1
    assert user_cart[0].quantity == 1

def test_review_system(db: Session, sample_data):
    """Test product review system"""
    customer = sample_data['users']['customer']
    product = sample_data['products']['phone']
    
    # Create order first
    order = Order(
        buyer_id=customer.id,
        product_id=product.id,
        quantity=1,
        unit_price=product.price,
        total_price=product.price,
        status=OrderStatus.COMPLETED
    )
    db.add(order)
    db.commit()

    # Add review
    review = Review(
        user_id=customer.id,
        product_id=product.id,
        order_id=order.id,
        rating=5,
        comment="Great product!"
    )
    db.add(review)
    db.commit()

    # Verify review
    assert len(product.reviews) == 1
    assert product.reviews[0].rating == 5

def test_notification_system(db: Session, sample_data):
    """Test user notification system"""
    user = sample_data['users']['customer']
    
    # Create notifications
    notification = Notification(
        user_id=user.id,
        title="Order Update",
        message="Your order has been shipped!"
    )
    db.add(notification)
    db.commit()

    # Verify notifications
    user_notifications = db.query(Notification).filter_by(user_id=user.id).all()
    assert len(user_notifications) == 1
    assert user_notifications[0].is_read == False

def test_cascade_deletes(db: Session, sample_data):
    """Test cascade delete behaviors"""
    seller = sample_data['users']['seller']
    seller_id = seller.id
    
    # Get product count before delete
    initial_count = db.query(Product).filter_by(seller_id=seller_id).count()
    assert initial_count > 0, "Should have products before delete"
    
    # Delete seller
    db.delete(seller)
    db.commit()

    # Verify seller and products are deleted without refreshing
    deleted_seller = db.query(User).filter_by(id=seller_id).first()
    assert deleted_seller is None, "Seller should be deleted"
    
    remaining_products = db.query(Product).filter_by(seller_id=seller_id).all()
    assert len(remaining_products) == 0, "All products should be deleted"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
