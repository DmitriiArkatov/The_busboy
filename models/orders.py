"""
Order data models for the restaurant bot.
Includes OrderItem, Order classes and OrderManager for managing orders.
"""
import json
import os
import logging
from typing import Dict, List, Optional
from datetime import datetime
from config import ORDERS_DATA_PATH, TABLE_COUNT
from models.menu import MenuItem

logger = logging.getLogger(__name__)

class OrderItem:
    """
    Represents an item in an order, with a menu item and quantity.
    """
    def __init__(self, menu_item: MenuItem, quantity: int):
        self.menu_item = menu_item
        self.quantity = quantity
    
    def to_dict(self) -> Dict:
        """Convert the order item to a dictionary for serialization"""
        return {
            "menu_item": self.menu_item.to_dict(),
            "quantity": self.quantity
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'OrderItem':
        """Create an OrderItem instance from a dictionary"""
        menu_item = MenuItem.from_dict(data["menu_item"])
        return cls(menu_item=menu_item, quantity=data["quantity"])

class Order:
    """
    Represents an order with table number, items and status.
    """
    def __init__(self, id: int, table_number: int, items: List[OrderItem] = None, 
                 timestamp: Optional[str] = None, is_active: bool = True):
        self.id = id
        self.table_number = table_number
        self.items = items or []
        self.timestamp = timestamp or datetime.now().isoformat()
        self.is_active = is_active
    
    def to_dict(self) -> Dict:
        """Convert the order to a dictionary for serialization"""
        return {
            "id": self.id,
            "table_number": self.table_number,
            "items": [item.to_dict() for item in self.items],
            "timestamp": self.timestamp,
            "is_active": self.is_active
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Order':
        """Create an Order instance from a dictionary"""
        items = [OrderItem.from_dict(item) for item in data["items"]]
        return cls(
            id=data["id"],
            table_number=data["table_number"],
            items=items,
            timestamp=data["timestamp"],
            is_active=data["is_active"]
        )
    
    def add_item(self, menu_item: MenuItem, quantity: int = 1) -> None:
        """Add an item to the order or update quantity if it already exists"""
        # Check if item already exists in order, update quantity if so
        for order_item in self.items:
            if order_item.menu_item.id == menu_item.id:
                order_item.quantity += quantity
                return
        
        # Otherwise add new order item
        self.items.append(OrderItem(menu_item, quantity))
    
    def remove_item(self, menu_item_id: int) -> bool:
        """Remove an item from the order by menu item ID"""
        for i, order_item in enumerate(self.items):
            if order_item.menu_item.id == menu_item_id:
                del self.items[i]
                return True
        return False

class OrderManager:
    """
    Manages the orders, provides methods for loading, saving, and accessing order data.
    """
    def __init__(self):
        self.orders: List[Order] = []
        self.load_orders()
    
    def load_orders(self) -> None:
        """Load orders from JSON file"""
        if os.path.exists(ORDERS_DATA_PATH):
            try:
                with open(ORDERS_DATA_PATH, 'r', encoding='utf-8') as f:
                    orders_data = json.load(f)
                
                if isinstance(orders_data, list):
                    self.orders = [Order.from_dict(order) for order in orders_data]
                    # Filter out inactive orders during load
                    self.orders = [order for order in self.orders if order.is_active]
                else:
                    logger.warning("Orders data format is not as expected. Initializing empty orders.")
                    self.orders = []
                    self.save_orders()
            except Exception as e:
                logger.error(f"Error loading orders: {e}")
                self.orders = []
        else:
            # Create directory if not exists
            os.makedirs(os.path.dirname(ORDERS_DATA_PATH), exist_ok=True)
            # Initialize with empty list
            self.orders = []
            self.save_orders()
    
    def save_orders(self) -> None:
        """Save orders to JSON file"""
        try:
            orders_data = [order.to_dict() for order in self.orders]
            os.makedirs(os.path.dirname(ORDERS_DATA_PATH), exist_ok=True)
            with open(ORDERS_DATA_PATH, 'w', encoding='utf-8') as f:
                json.dump(orders_data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logger.error(f"Error saving orders: {e}")
    
    def create_order(self, table_number: int) -> Order:
        """Create a new order for a table"""
        if not 1 <= table_number <= TABLE_COUNT:
            raise ValueError(f"Table number must be between 1 and {TABLE_COUNT}")
        
        # Check if table already has an active order
        for order in self.orders:
            if order.table_number == table_number and order.is_active:
                return order
        
        # Generate a new ID (max ID + 1 or 1 if no orders exist)
        new_id = max([order.id for order in self.orders], default=0) + 1
        order = Order(id=new_id, table_number=table_number)
        self.orders.append(order)
        self.save_orders()
        return order
    
    def get_order_by_id(self, order_id: int) -> Optional[Order]:
        """Get an order by ID"""
        for order in self.orders:
            if order.id == order_id:
                return order
        return None
    
    def get_active_orders(self) -> List[Order]:
        """Get all active orders"""
        return [order for order in self.orders if order.is_active]
    
    def get_table_active_order(self, table_number: int) -> Optional[Order]:
        """Get active order for a specific table"""
        for order in self.orders:
            if order.table_number == table_number and order.is_active:
                return order
        return None
    
    def close_order(self, order_id: int) -> bool:
        """Close (deactivate) an order"""
        order = self.get_order_by_id(order_id)
        if order:
            order.is_active = False
            self.save_orders()
            # Remove inactive orders from memory
            self.orders = [o for o in self.orders if o.is_active]
            return True
        return False

# Singleton instance
order_manager = OrderManager() 