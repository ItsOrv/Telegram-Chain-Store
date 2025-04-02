from sqlalchemy import Column, Integer, String, Enum, DECIMAL, DateTime, Text, BigInteger, ForeignKey, Boolean, MetaData
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import text
import enum
from datetime import datetime

metadata = MetaData(naming_convention={
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
})

Base = declarative_base(metadata=metadata)

# Enums
class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    SELLER = "SELLER"
    CUSTOMER = "CUSTOMER"

class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    BANNED = "banned"
    SUSPENDED = "suspended"

class OrderStatus(str, enum.Enum):
    PENDING_SELLER_CONFIRMATION = "PENDING_SELLER_CONFIRMATION"
    PENDING_ADMIN_CONFIRMATION = "PENDING_ADMIN_CONFIRMATION"
    TRANSFERRING_TO_PUBLIC_LOCATION = "TRANSFERRING_TO_PUBLIC_LOCATION"
    AT_PUBLIC_LOCATION_PENDING_PICKUP = "AT_PUBLIC_LOCATION_PENDING_PICKUP"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    REFUNDED = "REFUNDED"

class PaymentMethod(str, enum.Enum):
    CRYPTO = "crypto"
    CARD = "card"
    CASH = "cash"

class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    UNKNOWN = "unknown"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, nullable=False, unique=True)
    username = Column(String(255), nullable=True)
    phone_number = Column(String(20), nullable=True)
    wallet_address = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    role = Column(Enum(UserRole), nullable=False, server_default=UserRole.CUSTOMER.value)
    balance = Column(DECIMAL(18, 8), nullable=False, server_default=text('0'))
    status = Column(Enum(UserStatus), nullable=False, server_default=UserStatus.ACTIVE.value)
    language = Column(String(10), nullable=False, server_default='en')
    is_verified = Column(Boolean, nullable=False, server_default=text('0'))
    last_login = Column(DateTime, nullable=True)
    joined_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    products = relationship("Product", 
                          back_populates="seller",
                          cascade="all, delete-orphan",
                          passive_deletes=True)
    orders = relationship("Order", back_populates="buyer")
    cities = relationship("City", secondary="user_cities", back_populates="users")
    reviews = relationship("Review", back_populates="user")
    cart_items = relationship("CartItem", back_populates="user")
    notifications = relationship("Notification", back_populates="user")

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), nullable=False, unique=True)
    parent_id = Column(Integer, ForeignKey('categories.id', ondelete='SET NULL'), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))

    # Relationships
    products = relationship("Product", back_populates="category")
    subcategories = relationship("Category")

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    seller_id = Column(Integer, 
                      ForeignKey('users.id', ondelete='CASCADE'), 
                      nullable=False,
                      index=True)
    category_id = Column(Integer, ForeignKey('categories.id', ondelete='RESTRICT'), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(DECIMAL(18, 8), nullable=False)
    discount_price = Column(DECIMAL(18, 8), nullable=True)
    stock = Column(Integer, nullable=False, server_default=text('0'))
    min_order = Column(Integer, nullable=False, server_default=text('1'))
    max_order = Column(Integer, nullable=True)
    city_id = Column(Integer, ForeignKey('cities.id', ondelete='RESTRICT'), nullable=False)
    views_count = Column(Integer, nullable=False, server_default=text('0'))
    status = Column(Enum('active', 'inactive', 'suspended'), nullable=False, server_default='active')
    weight = Column(DECIMAL(10, 2), nullable=True, comment='Product weight in kilograms')
    zone = Column(String(100), nullable=True, comment='Specific area/zone within the city')
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    deleted_at = Column(DateTime, nullable=True)  # For soft delete
    is_available = Column(Boolean, default=True, nullable=False)

    # Relationships
    seller = relationship("User", 
                        back_populates="products",
                        single_parent=True)
    category = relationship("Category", back_populates="products")
    city = relationship("City", back_populates="products")
    orders = relationship("Order", back_populates="product")
    images = relationship("ProductImage", back_populates="product")
    reviews = relationship("Review", back_populates="product")
    cart_items = relationship("CartItem", back_populates="product")

class ProductImage(Base):
    __tablename__ = "product_images"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    image_url = Column(String(500), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))

    # Relationships
    product = relationship("Product", back_populates="images")

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    buyer_id = Column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id', ondelete='RESTRICT'), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(DECIMAL(18, 8), nullable=False)
    total_price = Column(DECIMAL(18, 8), nullable=False)
    status = Column(Enum(OrderStatus), nullable=False, server_default=OrderStatus.PENDING_SELLER_CONFIRMATION.value)
    payment_method = Column(Enum(PaymentMethod), nullable=True)
    payment_id = Column(String(255), nullable=True)
    pre_shipping_address = Column(Text, nullable=True)
    final_shipping_address = Column(Text, nullable=True)
    tracking_code = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    deleted_at = Column(DateTime, nullable=True)  # For soft delete

    # Relationships
    buyer = relationship("User", back_populates="orders")
    product = relationship("Product", back_populates="orders")
    payment = relationship("Payment", back_populates="order", uselist=False)
    reviews = relationship("Review", back_populates="order")
    main_location = relationship("MainLocation", back_populates="order", uselist=False)

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.id', ondelete='RESTRICT'), nullable=True)  # تغییر به nullable=True
    user_id = Column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), nullable=False)  # اضافه کردن فیلد user_id
    amount = Column(DECIMAL(18, 8), nullable=False)
    status = Column(Enum(PaymentStatus), nullable=False, server_default=PaymentStatus.PENDING.value)
    payment_type = Column(Enum('ORDER', 'CHARGE'), nullable=False, default='ORDER')  # اضافه کردن نوع پرداخت
    transaction_id = Column(String(255), unique=True)
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    # Relationships
    order = relationship("Order", back_populates="payment")
    user = relationship("User")  # اضافه کردن رابطه با کاربر

class Province(Base):
    __tablename__ = "provinces"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))

    # Relationships
    cities = relationship("City", back_populates="province")

class City(Base):
    __tablename__ = "cities"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    province_id = Column(Integer, ForeignKey('provinces.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))

    # Relationships
    province = relationship("Province", back_populates="cities")
    users = relationship("User", secondary="user_cities", back_populates="cities")
    products = relationship("Product", back_populates="city")
    pre_locations = relationship("PreLocation", back_populates="city")

class UserCity(Base):
    __tablename__ = "user_cities"
    
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    city_id = Column(Integer, ForeignKey('cities.id', ondelete='CASCADE'), primary_key=True)
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))

class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    order_id = Column(Integer, ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    
    # Relationships
    user = relationship("User", back_populates="reviews")
    product = relationship("Product", back_populates="reviews")
    order = relationship("Order", back_populates="reviews")

class CartItem(Base):
    __tablename__ = "cart_items"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    
    # Relationships
    user = relationship("User", back_populates="cart_items")
    product = relationship("Product", back_populates="cart_items")

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, nullable=False, server_default=text('0'))
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    
    # Relationships
    user = relationship("User", back_populates="notifications")

class PaymentMethod(Base):
    __tablename__ = "payment_methods"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    type = Column(Enum('CRYPTO', 'CARD', 'CASH'), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, server_default=text('1'))
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    
    # Relationships
    bank_cards = relationship("BankCard", back_populates="payment_method", cascade="all, delete-orphan")

class BankCard(Base):
    __tablename__ = "bank_cards"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    payment_method_id = Column(Integer, ForeignKey('payment_methods.id', ondelete='CASCADE'), nullable=False)
    card_number = Column(String(16), nullable=False)
    card_holder = Column(String(255), nullable=False)
    bank_name = Column(String(100), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    
    # Relationships
    payment_method = relationship("PaymentMethod", back_populates="bank_cards")

class PreLocation(Base):
    __tablename__ = "pre_locations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    city_id = Column(Integer, ForeignKey('cities.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(255), nullable=False)
    address = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, server_default=text('1'))
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    
    # Relationships
    city = relationship("City", back_populates="pre_locations")

class MainLocation(Base):
    __tablename__ = "main_locations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)
    address = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum('PENDING', 'APPROVED', 'REJECTED'), nullable=False, server_default='PENDING')
    admin_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    
    # Relationships
    order = relationship("Order", back_populates="main_location")
