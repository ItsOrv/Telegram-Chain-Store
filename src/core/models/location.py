from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import text
import enum
from datetime import datetime
from src.core.models.base import Base

class LocationStatus(str, enum.Enum):
    """Location status for delivery points"""
    ACTIVE = "ACTIVE"  # Available for use
    INACTIVE = "INACTIVE"  # Temporarily not available
    CLOSED = "CLOSED"  # Permanently closed
    
    def __str__(self) -> str:
        return self.value

class Province(Base):
    """Province/State/Region model"""
    __tablename__ = "provinces"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    code = Column(String(10), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime, nullable=False, 
                      server_default=text('CURRENT_TIMESTAMP'),
                      onupdate=text('CURRENT_TIMESTAMP'))
    
    # Relationships
    cities = relationship("City", back_populates="province", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Province(id={self.id}, name={self.name})>"

class City(Base):
    """City model"""
    __tablename__ = "cities"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    province_id = Column(Integer, ForeignKey('provinces.id', ondelete='CASCADE'), nullable=False)
    is_active = Column(Boolean, nullable=False, server_default=text('1'))
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime, nullable=False, 
                      server_default=text('CURRENT_TIMESTAMP'),
                      onupdate=text('CURRENT_TIMESTAMP'))
    
    # Relationships
    province = relationship("Province", back_populates="cities")
    users = relationship("User", secondary="user_cities", back_populates="cities")
    products = relationship("Product", back_populates="city")
    pre_locations = relationship("PreLocation", back_populates="city", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<City(id={self.id}, name={self.name}, province_id={self.province_id})>"

class PreLocation(Base):
    """Pre-defined delivery locations by admin"""
    __tablename__ = "pre_locations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    city_id = Column(Integer, ForeignKey('cities.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(255), nullable=False)
    address = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    area = Column(String(100), nullable=False, comment="Area/district/zone within the city")
    status = Column(Enum(LocationStatus), nullable=False, server_default=LocationStatus.ACTIVE.value)
    
    # Additional information
    safety_rating = Column(Integer, nullable=True, comment="Admin-assigned safety rating 1-5")
    instructions = Column(Text, nullable=True, comment="Special instructions for this location")
    
    created_by = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime, nullable=False, 
                      server_default=text('CURRENT_TIMESTAMP'),
                      onupdate=text('CURRENT_TIMESTAMP'))
    
    # Relationships
    city = relationship("City", back_populates="pre_locations")
    orders = relationship("Order", back_populates="location")
    creator = relationship("User", foreign_keys=[created_by])
    
    def __repr__(self) -> str:
        return f"<PreLocation(id={self.id}, name={self.name}, city_id={self.city_id})>"
    
    @property
    def is_active(self) -> bool:
        """Check if location is active"""
        return self.status == LocationStatus.ACTIVE
    
    @property
    def full_address(self) -> str:
        """Get full address with city"""
        return f"{self.address}, {self.area}, {self.city.name}"

class MainLocation(Base):
    """Specific delivery location information for an order"""
    __tablename__ = "main_locations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.id', ondelete='CASCADE'), nullable=False, unique=True)
    pre_location_id = Column(Integer, ForeignKey('pre_locations.id', ondelete='SET NULL'), nullable=True)
    
    # Location details
    photo_url = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    specific_instructions = Column(Text, nullable=True)
    
    # Status tracking
    status = Column(Enum('PENDING', 'READY', 'DELIVERED', 'PICKED_UP'), 
                   nullable=False, server_default='PENDING')
    
    # Audit fields
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime, nullable=False, 
                      server_default=text('CURRENT_TIMESTAMP'),
                      onupdate=text('CURRENT_TIMESTAMP'))
    
    # Relationships
    order = relationship("Order", foreign_keys=[order_id])
    pre_location = relationship("PreLocation", foreign_keys=[pre_location_id])
    
    def __repr__(self) -> str:
        return f"<MainLocation(id={self.id}, order_id={self.order_id}, status={self.status})>" 