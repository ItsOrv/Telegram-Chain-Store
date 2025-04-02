import pytest
from datetime import datetime
from src.core.models.product import (
    Product, ProductCategory, ProductVariant, ProductImage,
    ProductAttribute, ProductReview, ProductPrice, ProductInventory,
    ProductTag, ProductDiscount
)

def test_product_creation():
    product = Product(
        id=1,
        name="Test Product",
        description="Test product description",
        price=100.0,
        store_id=1,
        sku="TEST-001",
        barcode="123456789",
        weight=1.0,
        dimensions={"length": 10, "width": 5, "height": 2},
        is_active=True,
        is_featured=True
    )
    
    assert product.id == 1
    assert product.name == "Test Product"
    assert product.description == "Test product description"
    assert product.price == 100.0
    assert product.store_id == 1
    assert product.sku == "TEST-001"
    assert product.barcode == "123456789"
    assert product.weight == 1.0
    assert isinstance(product.dimensions, dict)
    assert product.is_active is True
    assert product.is_featured is True

def test_product_category_creation():
    category = ProductCategory(
        id=1,
        name="Electronics",
        description="Electronic products",
        parent_id=None,
        store_id=1,
        is_active=True
    )
    
    assert category.id == 1
    assert category.name == "Electronics"
    assert category.description == "Electronic products"
    assert category.parent_id is None
    assert category.store_id == 1
    assert category.is_active is True

def test_product_variant_creation():
    variant = ProductVariant(
        id=1,
        product_id=1,
        name="Red",
        sku="TEST-001-RED",
        price=110.0,
        attributes={"color": "red", "size": "M"},
        is_active=True
    )
    
    assert variant.id == 1
    assert variant.product_id == 1
    assert variant.name == "Red"
    assert variant.sku == "TEST-001-RED"
    assert variant.price == 110.0
    assert isinstance(variant.attributes, dict)
    assert variant.is_active is True

def test_product_image_creation():
    image = ProductImage(
        id=1,
        product_id=1,
        url="https://example.com/image.jpg",
        alt_text="Product image",
        is_primary=True,
        sort_order=1
    )
    
    assert image.id == 1
    assert image.product_id == 1
    assert image.url == "https://example.com/image.jpg"
    assert image.alt_text == "Product image"
    assert image.is_primary is True
    assert image.sort_order == 1

def test_product_attribute_creation():
    attribute = ProductAttribute(
        id=1,
        product_id=1,
        name="Color",
        value="Red",
        is_filterable=True,
        sort_order=1
    )
    
    assert attribute.id == 1
    assert attribute.product_id == 1
    assert attribute.name == "Color"
    assert attribute.value == "Red"
    assert attribute.is_filterable is True
    assert attribute.sort_order == 1

def test_product_review_creation():
    review = ProductReview(
        id=1,
        product_id=1,
        user_id=100,
        rating=5,
        comment="Great product!",
        is_approved=True
    )
    
    assert review.id == 1
    assert review.product_id == 1
    assert review.user_id == 100
    assert review.rating == 5
    assert review.comment == "Great product!"
    assert review.is_approved is True

def test_product_price_creation():
    price = ProductPrice(
        id=1,
        product_id=1,
        price=100.0,
        currency="USD",
        start_date=datetime.now(),
        end_date=datetime.now()
    )
    
    assert price.id == 1
    assert price.product_id == 1
    assert price.price == 100.0
    assert price.currency == "USD"
    assert isinstance(price.start_date, datetime)
    assert isinstance(price.end_date, datetime)

def test_product_inventory_creation():
    inventory = ProductInventory(
        id=1,
        product_id=1,
        variant_id=1,
        quantity=100,
        low_stock_threshold=10,
        is_tracked=True
    )
    
    assert inventory.id == 1
    assert inventory.product_id == 1
    assert inventory.variant_id == 1
    assert inventory.quantity == 100
    assert inventory.low_stock_threshold == 10
    assert inventory.is_tracked is True

def test_product_tag_creation():
    tag = ProductTag(
        id=1,
        name="New Arrival",
        store_id=1,
        is_active=True
    )
    
    assert tag.id == 1
    assert tag.name == "New Arrival"
    assert tag.store_id == 1
    assert tag.is_active is True

def test_product_discount_creation():
    discount = ProductDiscount(
        id=1,
        product_id=1,
        discount_type="percentage",
        value=10.0,
        start_date=datetime.now(),
        end_date=datetime.now()
    )
    
    assert discount.id == 1
    assert discount.product_id == 1
    assert discount.discount_type == "percentage"
    assert discount.value == 10.0
    assert isinstance(discount.start_date, datetime)
    assert isinstance(discount.end_date, datetime) 