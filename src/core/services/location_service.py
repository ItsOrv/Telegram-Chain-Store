from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
from src.core.models.location import City, Province, PreLocation, MainLocation, LocationStatus
from src.core.services.base_service import BaseService
from src.utils.logger import log_error, setup_logger
import random

# Initialize logger
logger = setup_logger("location_service")

class LocationService:
    """
    Service for managing location-based delivery
    """
    
    def __init__(self, db_session: Session):
        """
        Initialize the location service
        
        Args:
            db_session: SQLAlchemy database session
        """
        self.db = db_session
        self.province_service = BaseService(db_session, Province)
        self.city_service = BaseService(db_session, City)
        self.pre_location_service = BaseService(db_session, PreLocation)
        self.main_location_service = BaseService(db_session, MainLocation)
    
    # Province operations
    
    def get_all_provinces(self) -> List[Province]:
        """
        Get all provinces
        
        Returns:
            List of provinces
        """
        return self.province_service.get_all(limit=100)
    
    def get_province_by_id(self, province_id: int) -> Optional[Province]:
        """
        Get a province by ID
        
        Args:
            province_id: Province ID
            
        Returns:
            Province if found, None otherwise
        """
        return self.province_service.get_by_id(province_id)
    
    def create_province(self, name: str, code: Optional[str] = None) -> Optional[Province]:
        """
        Create a new province
        
        Args:
            name: Province name
            code: Province code (optional)
            
        Returns:
            Created province if successful, None otherwise
        """
        try:
            # Check if province already exists
            existing = self.db.query(Province).filter(func.lower(Province.name) == func.lower(name)).first()
            if existing:
                logger.info(f"Province {name} already exists with ID {existing.id}")
                return existing
            
            # Create province
            province_data = {
                "name": name,
                "code": code
            }
            
            province = self.province_service.create(province_data)
            if province:
                logger.info(f"Created province {province.id}: {name}")
            return province
        except Exception as e:
            log_error(f"Error creating province {name}", e)
            return None
    
    # City operations
    
    def get_cities_by_province(self, province_id: int) -> List[City]:
        """
        Get all cities in a province
        
        Args:
            province_id: Province ID
            
        Returns:
            List of cities
        """
        try:
            return self.db.query(City).filter(City.province_id == province_id).all()
        except Exception as e:
            log_error(f"Error getting cities for province {province_id}", e)
            return []
    
    def get_city_by_id(self, city_id: int) -> Optional[City]:
        """
        Get a city by ID
        
        Args:
            city_id: City ID
            
        Returns:
            City if found, None otherwise
        """
        return self.city_service.get_by_id(city_id)
    
    def create_city(self, name: str, province_id: int) -> Optional[City]:
        """
        Create a new city
        
        Args:
            name: City name
            province_id: Province ID
            
        Returns:
            Created city if successful, None otherwise
        """
        try:
            # Check if province exists
            province = self.province_service.get_by_id(province_id)
            if not province:
                logger.error(f"Cannot create city: Province {province_id} not found")
                return None
            
            # Check if city already exists in this province
            existing = self.db.query(City).filter(
                and_(
                    func.lower(City.name) == func.lower(name),
                    City.province_id == province_id
                )
            ).first()
            
            if existing:
                logger.info(f"City {name} already exists in province {province_id} with ID {existing.id}")
                return existing
            
            # Create city
            city_data = {
                "name": name,
                "province_id": province_id,
                "is_active": True
            }
            
            city = self.city_service.create(city_data)
            if city:
                logger.info(f"Created city {city.id}: {name} in province {province_id}")
            return city
        except Exception as e:
            log_error(f"Error creating city {name} in province {province_id}", e)
            return None
    
    # Pre-defined location operations
    
    def create_pre_location(self, city_id: int, name: str, address: str, 
                         area: str, description: Optional[str] = None,
                         safety_rating: Optional[int] = None,
                         instructions: Optional[str] = None,
                         created_by: Optional[int] = None) -> Optional[PreLocation]:
        """
        Create a pre-defined location
        
        Args:
            city_id: City ID
            name: Location name
            address: Location address
            area: Area/district/zone
            description: Location description (optional)
            safety_rating: Safety rating 1-5 (optional)
            instructions: Special instructions (optional)
            created_by: Creator user ID (optional)
            
        Returns:
            Created pre-location if successful, None otherwise
        """
        try:
            # Check if city exists
            city = self.city_service.get_by_id(city_id)
            if not city:
                logger.error(f"Cannot create pre-location: City {city_id} not found")
                return None
            
            # Create pre-location
            pre_location_data = {
                "city_id": city_id,
                "name": name,
                "address": address,
                "area": area,
                "description": description,
                "status": LocationStatus.ACTIVE,
                "safety_rating": safety_rating,
                "instructions": instructions,
                "created_by": created_by
            }
            
            pre_location = self.pre_location_service.create(pre_location_data)
            if pre_location:
                logger.info(f"Created pre-location {pre_location.id}: {name} in city {city_id}")
            return pre_location
        except Exception as e:
            log_error(f"Error creating pre-location in city {city_id}", e)
            return None
    
    def get_pre_locations_by_city(self, city_id: int) -> List[PreLocation]:
        """
        Get all pre-defined locations in a city
        
        Args:
            city_id: City ID
            
        Returns:
            List of pre-locations
        """
        try:
            return self.db.query(PreLocation).filter(
                PreLocation.city_id == city_id,
                PreLocation.status == LocationStatus.ACTIVE
            ).all()
        except Exception as e:
            log_error(f"Error getting pre-locations for city {city_id}", e)
            return []
    
    def get_pre_locations_by_area(self, city_id: int, area: str) -> List[PreLocation]:
        """
        Get all pre-defined locations in a specific area
        
        Args:
            city_id: City ID
            area: Area/district/zone
            
        Returns:
            List of pre-locations
        """
        try:
            return self.db.query(PreLocation).filter(
                PreLocation.city_id == city_id,
                func.lower(PreLocation.area) == func.lower(area),
                PreLocation.status == LocationStatus.ACTIVE
            ).all()
        except Exception as e:
            log_error(f"Error getting pre-locations for area {area} in city {city_id}", e)
            return []
    
    def get_random_pre_location(self, city_id: int, area: str) -> Optional[PreLocation]:
        """
        Get a random pre-defined location in a specific area
        
        Args:
            city_id: City ID
            area: Area/district/zone
            
        Returns:
            Random pre-location if available, None otherwise
        """
        try:
            locations = self.get_pre_locations_by_area(city_id, area)
            if not locations:
                # If no locations in specific area, try anywhere in the city
                locations = self.get_pre_locations_by_city(city_id)
            
            if not locations:
                logger.error(f"No pre-locations found in city {city_id}")
                return None
            
            # Return a random location
            return random.choice(locations)
        except Exception as e:
            log_error(f"Error getting random pre-location for area {area} in city {city_id}", e)
            return None
    
    # Main location operations
    
    def create_main_location(self, order_id: int, pre_location_id: int, 
                          photo_url: Optional[str] = None,
                          description: Optional[str] = None,
                          specific_instructions: Optional[str] = None) -> Optional[MainLocation]:
        """
        Create a main location for an order
        
        Args:
            order_id: Order ID
            pre_location_id: Pre-location ID
            photo_url: Photo URL (optional)
            description: Description (optional)
            specific_instructions: Specific instructions (optional)
            
        Returns:
            Created main location if successful, None otherwise
        """
        try:
            # Check if pre-location exists
            pre_location = self.pre_location_service.get_by_id(pre_location_id)
            if not pre_location:
                logger.error(f"Cannot create main location: Pre-location {pre_location_id} not found")
                return None
            
            # Check if order already has a main location
            existing = self.db.query(MainLocation).filter(MainLocation.order_id == order_id).first()
            if existing:
                logger.info(f"Order {order_id} already has a main location {existing.id}")
                return existing
            
            # Create main location
            main_location_data = {
                "order_id": order_id,
                "pre_location_id": pre_location_id,
                "photo_url": photo_url,
                "description": description or pre_location.description,
                "specific_instructions": specific_instructions or pre_location.instructions,
                "status": "PENDING"
            }
            
            main_location = self.main_location_service.create(main_location_data)
            if main_location:
                logger.info(f"Created main location {main_location.id} for order {order_id}")
            return main_location
        except Exception as e:
            log_error(f"Error creating main location for order {order_id}", e)
            return None
    
    def update_main_location_photo(self, main_location_id: int, photo_url: str) -> bool:
        """
        Update a main location with a photo
        
        Args:
            main_location_id: Main location ID
            photo_url: Photo URL
            
        Returns:
            True if successful, False otherwise
        """
        try:
            main_location = self.main_location_service.get_by_id(main_location_id)
            if not main_location:
                return False
            
            main_location.photo_url = photo_url
            main_location.status = "READY"
            
            self.db.commit()
            logger.info(f"Updated main location {main_location_id} with photo")
            return True
        except Exception as e:
            self.db.rollback()
            log_error(f"Error updating main location {main_location_id} with photo", e)
            return False
    
    def mark_as_delivered(self, main_location_id: int) -> bool:
        """
        Mark a main location as delivered
        
        Args:
            main_location_id: Main location ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            main_location = self.main_location_service.get_by_id(main_location_id)
            if not main_location:
                return False
            
            main_location.status = "DELIVERED"
            
            self.db.commit()
            logger.info(f"Marked main location {main_location_id} as delivered")
            return True
        except Exception as e:
            self.db.rollback()
            log_error(f"Error marking main location {main_location_id} as delivered", e)
            return False
    
    def mark_as_picked_up(self, main_location_id: int) -> bool:
        """
        Mark a main location as picked up
        
        Args:
            main_location_id: Main location ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            main_location = self.main_location_service.get_by_id(main_location_id)
            if not main_location:
                return False
            
            main_location.status = "PICKED_UP"
            
            self.db.commit()
            logger.info(f"Marked main location {main_location_id} as picked up")
            return True
        except Exception as e:
            self.db.rollback()
            log_error(f"Error marking main location {main_location_id} as picked up", e)
            return False
    
    def get_locations(self, limit: int = 5) -> List[PreLocation]:
        """
        Get a list of recent predefined locations
        
        Args:
            limit: Maximum number of locations to return
            
        Returns:
            List of PreLocation objects
        """
        try:
            locations = self.db.query(PreLocation).order_by(
                desc(PreLocation.created_at)
            ).limit(limit).all()
            return locations
        except Exception as e:
            log_error("Error getting locations list", e)
            return []
    
    def count_locations(self) -> int:
        """
        Count total number of predefined locations
        
        Returns:
            Total count of PreLocation objects
        """
        try:
            return self.db.query(PreLocation).count()
        except Exception as e:
            log_error("Error counting locations", e)
            return 0 