"""
Menu data models for the restaurant bot.
Includes MenuItem class for individual dishes and MenuManager for managing the menu.
"""
import json
import os
import logging
from typing import Dict, List, Optional
from config import MENU_DATA_PATH, MENU_CATEGORIES, MAIN_CATEGORIES, ALL_CATEGORIES

logger = logging.getLogger(__name__)

class MenuItem:
    """
    Represents a menu item with its properties.
    """
    def __init__(self, id: int, name: str, category: str, main_category: str = None):
        self.id = id
        self.name = name
        self.category = category
        # If main_category is not provided, determine it from the category
        if main_category is None:
            self.main_category = self._determine_main_category()
        else:
            self.main_category = main_category
    
    def _determine_main_category(self) -> str:
        """Determine main category based on category"""
        for main_cat, subcats in MENU_CATEGORIES.items():
            if self.category in subcats:
                return main_cat
        return "Кухня"  # Default to Kitchen if not found
    
    def to_dict(self) -> Dict:
        """Convert the menu item to a dictionary for serialization"""
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "main_category": self.main_category
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'MenuItem':
        """Create a MenuItem instance from a dictionary"""
        main_category = data.get("main_category")
        return cls(
            id=data["id"],
            name=data["name"],
            category=data["category"],
            main_category=main_category
        )

class MenuManager:
    """
    Manages the menu items, provides methods for loading, saving, and accessing menu data.
    """
    def __init__(self):
        self.menu_items: List[MenuItem] = []
        self.load_menu()
    
    def load_menu(self) -> None:
        """Load menu from JSON file"""
        if os.path.exists(MENU_DATA_PATH):
            try:
                with open(MENU_DATA_PATH, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Check if the data is in the expected format (list of dictionaries)
                if isinstance(data, list):
                    self.menu_items = [MenuItem.from_dict(item) for item in data]
                    
                    # Check and add main_category if missing
                    needs_update = False
                    for item in self.menu_items:
                        if not hasattr(item, 'main_category') or item.main_category is None:
                            item.main_category = item._determine_main_category()
                            needs_update = True
                    
                    if needs_update:
                        self.save_menu()
                else:
                    logger.warning("Menu data format is not as expected. Initializing empty menu.")
                    self.menu_items = []
                    self.save_menu()
            except Exception as e:
                logger.error(f"Error loading menu: {e}")
                self.menu_items = []
        else:
            # Create directory if not exists
            os.makedirs(os.path.dirname(MENU_DATA_PATH), exist_ok=True)
            # Initialize with empty list
            self.menu_items = []
            self.save_menu()
    
    def save_menu(self) -> None:
        """Save menu to JSON file"""
        try:
            items_data = [item.to_dict() for item in self.menu_items]
            os.makedirs(os.path.dirname(MENU_DATA_PATH), exist_ok=True)
            with open(MENU_DATA_PATH, 'w', encoding='utf-8') as f:
                json.dump(items_data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logger.error(f"Error saving menu: {e}")
    
    def get_menu_items_by_category(self, category: str) -> List[MenuItem]:
        """Get menu items filtered by category"""
        return [item for item in self.menu_items if item.category.lower() == category.lower()]
    
    def get_menu_items_by_main_category(self, main_category: str) -> List[MenuItem]:
        """Get menu items filtered by main category"""
        return [item for item in self.menu_items if item.main_category == main_category]
    
    def get_all_categories(self) -> List[str]:
        """Get all available categories as a flat list"""
        return ALL_CATEGORIES
    
    def get_main_categories(self) -> List[str]:
        """Get main categories"""
        return MAIN_CATEGORIES
    
    def get_subcategories(self, main_category: str) -> List[str]:
        """Get subcategories for a given main category"""
        return MENU_CATEGORIES.get(main_category, [])
    
    def add_item(self, name: str, category: str, main_category: str = None) -> MenuItem:
        """Add a new menu item"""
        # Generate a new ID (max ID + 1 or 1 if no items exist)
        new_id = max([item.id for item in self.menu_items], default=0) + 1
        item = MenuItem(id=new_id, name=name, category=category, main_category=main_category)
        self.menu_items.append(item)
        self.save_menu()
        return item
    
    def delete_item(self, item_id: int) -> bool:
        """Delete a menu item by ID"""
        for i, item in enumerate(self.menu_items):
            if item.id == item_id:
                del self.menu_items[i]
                self.save_menu()
                return True
        return False
    
    def get_item_by_id(self, item_id: int) -> Optional[MenuItem]:
        """Get a menu item by ID"""
        for item in self.menu_items:
            if item.id == item_id:
                return item
        return None

# Singleton instance
menu_manager = MenuManager() 