"""
Configuration file for the Telegram bot.
Contains all constants and settings needed for the application.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Telegram Bot Token (get from environment variable or use default)
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# Path to store json data
MENU_DATA_PATH = "data/menu.json"
ORDERS_DATA_PATH = "data/orders.json"

# Number of tables in the restaurant
TABLE_COUNT = 11

# Main menu categories
MAIN_CATEGORIES = ["Кухня", "Бар"]

# Menu categories by main category
MENU_CATEGORIES = {
    "Кухня": ["Закуски", "Гарниры", "Горячее", "Десерты", "Салаты"],
    "Бар": ["Коктейли", "Алкоголь", "Пиво", "Лимонады", "Чай"]
}

# Generate a flat list of all categories for convenience
ALL_CATEGORIES = []
for categories in MENU_CATEGORIES.values():
    ALL_CATEGORIES.extend(categories) 