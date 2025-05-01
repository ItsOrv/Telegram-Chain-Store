from telethon import Button
from typing import List, Any

def get_location_management_keyboard() -> List[List[Button]]:
    """
    Get the keyboard for location management
    
    Returns:
        List of button rows
    """
    return [
        [
            Button.inline("➕ افزودن مکان", "location:add"),
            Button.inline("📋 لیست مکان‌ها", "location:list")
        ],
        [
            Button.inline("🔍 جستجوی مکان", "location:find"),
            Button.inline("🗑️ حذف مکان", "location:remove")
        ],
        [
            Button.inline("« بازگشت به پنل مدیریت", "admin:back")
        ]
    ]

def get_cities_keyboard(cities: List[Any]) -> List[List[Button]]:
    """
    Get the keyboard for city selection
    
    Args:
        cities: List of city objects
        
    Returns:
        List of button rows
    """
    keyboard = []
    
    # Create buttons for cities, 2 per row
    row = []
    for i, city in enumerate(cities, 1):
        row.append(Button.inline(city.name, f"location:list:{city.id}"))
        
        if i % 2 == 0 or i == len(cities):
            keyboard.append(row)
            row = []
    
    # Add navigation buttons
    keyboard.append([
        Button.inline("« بازگشت به منوی اصلی", "navigation:main_menu")
    ])
    
    return keyboard

def get_locations_keyboard(city_id: int) -> List[List[Button]]:
    """
    Get the keyboard for location selection in a city
    
    Args:
        city_id: City ID
        
    Returns:
        List of button rows
    """
    return [
        [
            Button.inline("✅ انتخاب مکان", f"location:select:{city_id}"),
            Button.inline("🗺️ مشاهده نقشه", f"location:map:{city_id}")
        ],
        [
            Button.inline("« بازگشت به لیست شهرها", "location:list"),
            Button.inline("« منوی اصلی", "navigation:main_menu")
        ]
    ] 