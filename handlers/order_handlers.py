"""
Order handling module for the restaurant Telegram bot.
Handles order creation, viewing active orders, and order management.
"""
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from models.menu import menu_manager
from models.orders import order_manager
from config import TABLE_COUNT, MENU_CATEGORIES, MAIN_CATEGORIES, ALL_CATEGORIES
from handlers.common import get_main_keyboard
from datetime import datetime

# Define states for order management
class OrderStates(StatesGroup):
    """States for order creation and management flow"""
    selecting_table = State()
    selecting_main_category = State()  # Кухня/Бар
    selecting_category = State()       # Subcategories
    selecting_menu_item = State()
    entering_quantity = State()
    viewing_order = State()
    managing_order = State()
    confirm_close = State()

router = Router()

# Keyboards
def get_tables_keyboard():
    """Create a keyboard with table selection buttons"""
    keyboard = []
    
    # Create buttons for tables in rows of 3
    for i in range(1, TABLE_COUNT + 1, 3):
        row = []
        for j in range(i, min(i + 3, TABLE_COUNT + 1)):
            row.append(KeyboardButton(text=f"Стол {j}"))
        keyboard.append(row)
    
    keyboard.append([KeyboardButton(text="🔙 Вернуться в главное меню")])
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Выберите стол"
    )

def get_main_categories_keyboard():
    """Create a keyboard with main categories (Кухня/Бар)"""
    keyboard = []
    
    for category in MAIN_CATEGORIES:
        keyboard.append([KeyboardButton(text=category)])
    
    keyboard.append([KeyboardButton(text="✅ Завершить заказ")])
    keyboard.append([KeyboardButton(text="🔙 Назад к столам")])
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Выберите категорию"
    )

def get_subcategories_keyboard(main_category):
    """Create a keyboard with subcategories for the selected main category"""
    subcategories = MENU_CATEGORIES.get(main_category, [])
    keyboard = []
    
    # Add subcategories in rows of 2
    for i in range(0, len(subcategories), 2):
        row = []
        row.append(KeyboardButton(text=subcategories[i]))
        if i + 1 < len(subcategories):
            row.append(KeyboardButton(text=subcategories[i + 1]))
        keyboard.append(row)
    
    keyboard.append([KeyboardButton(text="🔙 Назад к основным категориям")])
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Выберите подкатегорию"
    )

def get_active_orders_keyboard():
    """Create a keyboard with active orders"""
    active_orders = order_manager.get_active_orders()
    keyboard = []
    
    # Group orders by tables
    for order in active_orders:
        keyboard.append([
            KeyboardButton(text=f"Стол {order.table_number} - {len(order.items)} поз.")
        ])
    
    keyboard.append([KeyboardButton(text="🔙 Вернуться в главное меню")])
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Выберите заказ"
    )

def get_order_actions_keyboard(order):
    """Create a keyboard with order management actions"""
    keyboard = [
        [KeyboardButton(text=f"➕ Добавить позиции (Стол {order.table_number})")],
        [KeyboardButton(text=f"✅ Закрыть заказ (Стол {order.table_number})")],
        [KeyboardButton(text="🔙 Назад к заказам")]
    ]
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )

def get_category_items_keyboard(category):
    """Create a keyboard with menu items for a specific category"""
    items = menu_manager.get_menu_items_by_category(category)
    keyboard = []
    
    # Add items in rows of 1
    for item in items:
        keyboard.append([KeyboardButton(text=f"{item.name}")])
    
    keyboard.append([KeyboardButton(text="🔙 Назад к подкатегориям")])
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Выберите блюдо"
    )

def get_quantity_keyboard():
    """Create a keyboard for quantity selection"""
    keyboard = [
        [
            KeyboardButton(text="1"),
            KeyboardButton(text="2"),
            KeyboardButton(text="3"),
        ],
        [
            KeyboardButton(text="4"),
            KeyboardButton(text="5"),
            KeyboardButton(text="Другое количество"),
        ],
        [KeyboardButton(text="🔙 Назад")]
    ]
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Выберите количество"
    )

def get_confirmation_keyboard():
    """Create a keyboard for order close confirmation"""
    keyboard = [
        [KeyboardButton(text="✅ Да, закрыть заказ"), KeyboardButton(text="❌ Нет, отмена")]
    ]
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )

# Handlers
@router.message(F.text == "🆕 Новый заказ")
async def new_order(message: Message, state: FSMContext):
    """Handle new order creation"""
    await state.set_state(OrderStates.selecting_table)
    await message.answer(
        "🆕 <b>Новый заказ</b>\n\n"
        "Выберите номер стола:",
        parse_mode="HTML",
        reply_markup=get_tables_keyboard()
    )

@router.message(F.text == "📋 Активные заказы")
async def show_active_orders(message: Message, state: FSMContext):
    active_orders = order_manager.get_active_orders()
    
    if not active_orders:
        await message.answer(
            "📋 <b>Активные заказы</b>\n\n"
            "На данный момент нет активных заказов.",
            parse_mode="HTML",
            reply_markup=get_main_keyboard()
        )
        return
    
    # Save active order IDs to state for quick lookup
    order_map = {}
    for order in active_orders:
        key = f"Стол {order.table_number} - {len(order.items)} поз."
        order_map[key] = order.id
    
    await state.update_data(active_orders=order_map)
    await state.set_state(OrderStates.viewing_order)
    
    await message.answer(
        "📋 <b>Активные заказы</b>\n\n"
        "Выберите заказ для просмотра:",
        parse_mode="HTML",
        reply_markup=get_active_orders_keyboard()
    )

@router.message(OrderStates.selecting_table)
async def select_table(message: Message, state: FSMContext):
    text = message.text
    
    if text == "🔙 Вернуться в главное меню":
        await state.clear()
        await message.answer(
            "Вы вернулись в главное меню.",
            reply_markup=get_main_keyboard()
        )
        return
    
    # Parse table number from text ("Стол X")
    if not text.startswith("Стол "):
        await message.answer(
            "❌ Пожалуйста, выберите стол из списка:",
            reply_markup=get_tables_keyboard()
        )
        return
    
    try:
        table_number = int(text.split(" ")[1])
        if not 1 <= table_number <= TABLE_COUNT:
            raise ValueError("Invalid table number")
    except (ValueError, IndexError):
        await message.answer(
            "❌ Пожалуйста, выберите стол из списка:",
            reply_markup=get_tables_keyboard()
        )
        return
    
    # Check if table has an active order
    existing_order = order_manager.get_table_active_order(table_number)
    
    if existing_order:
        # If order exists, show it
        await state.update_data(current_order_id=existing_order.id)
        await state.set_state(OrderStates.managing_order)
        order_text = format_order_text(existing_order)
        
        await message.answer(
            f"📋 <b>Существующий заказ для стола {table_number}</b>\n\n"
            f"{order_text}",
            parse_mode="HTML",
            reply_markup=get_order_actions_keyboard(existing_order)
        )
    else:
        # Create new order and show main categories (Кухня/Бар)
        order = order_manager.create_order(table_number)
        await state.update_data(current_order_id=order.id)
        await state.set_state(OrderStates.selecting_main_category)
        
        await message.answer(
            f"🆕 <b>Новый заказ для стола {table_number}</b>\n\n"
            "Выберите раздел меню:",
            parse_mode="HTML",
            reply_markup=get_main_categories_keyboard()
        )

@router.message(F.text == "🔙 Вернуться в главное меню")
async def back_to_main_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Вы вернулись в главное меню.",
        reply_markup=get_main_keyboard()
    )

@router.message(F.text == "🔙 Назад к столам")
async def back_to_tables(message: Message, state: FSMContext):
    await state.set_state(OrderStates.selecting_table)
    await message.answer(
        "🆕 <b>Новый заказ</b>\n\n"
        "Выберите номер стола:",
        parse_mode="HTML",
        reply_markup=get_tables_keyboard()
    )

@router.message(F.text == "🔙 Назад к заказам")
async def back_to_active_orders(message: Message, state: FSMContext):
    active_orders = order_manager.get_active_orders()
    
    if not active_orders:
        await message.answer(
            "📋 <b>Активные заказы</b>\n\n"
            "На данный момент нет активных заказов.",
            parse_mode="HTML",
            reply_markup=get_main_keyboard()
        )
        return
    
    # Save active order IDs to state for quick lookup
    order_map = {}
    for order in active_orders:
        key = f"Стол {order.table_number} - {len(order.items)} поз."
        order_map[key] = order.id
    
    await state.update_data(active_orders=order_map)
    await state.set_state(OrderStates.viewing_order)
    
    await message.answer(
        "📋 <b>Активные заказы</b>\n\n"
        "Выберите заказ для просмотра:",
        parse_mode="HTML",
        reply_markup=get_active_orders_keyboard()
    )

@router.message(OrderStates.selecting_main_category)
async def select_main_category(message: Message, state: FSMContext):
    text = message.text
    data = await state.get_data()
    order_id = data.get("current_order_id")
    
    if text == "🔙 Назад к столам":
        await back_to_tables(message, state)
        return
    
    if text == "✅ Завершить заказ":
        order = order_manager.get_order_by_id(order_id)
        if not order:
            await message.answer(
                "❌ Заказ не найден.",
                reply_markup=get_main_keyboard()
            )
            return
        
        if not order.items:
            # If no items in order, delete it
            order_manager.close_order(order_id)
            await message.answer(
                "❌ Заказ отменен, так как не было добавлено ни одной позиции.",
                reply_markup=get_main_keyboard()
            )
            await state.clear()
            return
        
        # Show order summary
        order_text = format_order_text(order)
        
        await message.answer(
            f"✅ <b>Заказ для стола {order.table_number} создан</b>\n\n"
            f"{order_text}",
            parse_mode="HTML",
            reply_markup=get_main_keyboard()
        )
        
        await state.clear()
        return
    
    # Check if the text is a valid main category
    if text not in MAIN_CATEGORIES:
        await message.answer(
            "❌ Пожалуйста, выберите раздел меню из списка:",
            reply_markup=get_main_categories_keyboard()
        )
        return
    
    main_category = text
    await state.update_data(current_main_category=main_category)
    
    # Show subcategories for the selected main category
    await state.set_state(OrderStates.selecting_category)
    await message.answer(
        f"<b>{main_category}</b>\n\n"
        "Выберите категорию блюд:",
        parse_mode="HTML",
        reply_markup=get_subcategories_keyboard(main_category)
    )

@router.message(OrderStates.selecting_category)
async def select_subcategory(message: Message, state: FSMContext):
    text = message.text
    data = await state.get_data()
    main_category = data.get("current_main_category")
    order_id = data.get("current_order_id")
    
    if text == "🔙 Назад к основным категориям":
        await state.set_state(OrderStates.selecting_main_category)
        await message.answer(
            "Выберите раздел меню:",
            parse_mode="HTML",
            reply_markup=get_main_categories_keyboard()
        )
        return
    
    # Get subcategories for current main category
    subcategories = MENU_CATEGORIES.get(main_category, [])
    
    # Check if selected text is a valid subcategory
    if text not in subcategories:
        await message.answer(
            "❌ Пожалуйста, выберите категорию из списка:",
            reply_markup=get_subcategories_keyboard(main_category)
        )
        return
    
    category = text
    await state.update_data(current_category=category)
    
    items = menu_manager.get_menu_items_by_category(category)
    
    if not items:
        await message.answer(
            f"❌ В категории \"{category}\" нет позиций.",
            reply_markup=get_subcategories_keyboard(main_category)
        )
        return
    
    # Create keyboard with menu items
    keyboard = []
    for item in items:
        keyboard.append([KeyboardButton(text=f"{item.name}")])
    
    keyboard.append([KeyboardButton(text="🔙 Назад к подкатегориям")])
    
    await state.set_state(OrderStates.selecting_menu_item)
    await message.answer(
        f"🍽️ <b>Выберите позицию из категории \"{category}\"</b>",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=keyboard,
            resize_keyboard=True
        )
    )

@router.message(OrderStates.selecting_menu_item, F.text == "🔙 Назад к подкатегориям")
async def back_to_subcategories(message: Message, state: FSMContext):
    data = await state.get_data()
    main_category = data.get("current_main_category")
    
    await state.set_state(OrderStates.selecting_category)
    await message.answer(
        f"<b>{main_category}</b>\n\n"
        "Выберите категорию блюд:",
        parse_mode="HTML",
        reply_markup=get_subcategories_keyboard(main_category)
    )

@router.message(OrderStates.selecting_menu_item)
async def select_menu_item(message: Message, state: FSMContext):
    text = message.text
    data = await state.get_data()
    category = data.get("current_category")
    
    # Parse menu item from text
    items = menu_manager.get_menu_items_by_category(category)
    selected_item = None
    
    for item in items:
        if text.startswith(f"{item.name}"):
            selected_item = item
            break
    
    if not selected_item:
        await message.answer(
            "❌ Пожалуйста, выберите блюдо из списка:",
            reply_markup=get_category_items_keyboard(category)
        )
        return
    
    await state.update_data(current_item_id=selected_item.id)
    
    await state.set_state(OrderStates.entering_quantity)
    await message.answer(
        f"🔢 <b>Выберите количество</b>\n\n"
        f"Блюдо: {selected_item.name}",
        parse_mode="HTML",
        reply_markup=get_quantity_keyboard()
    )

@router.message(OrderStates.entering_quantity, F.text == "🔙 Назад")
async def back_to_items(message: Message, state: FSMContext):
    data = await state.get_data()
    category = data.get("current_category")
    
    items = menu_manager.get_menu_items_by_category(category)
    
    # Create keyboard with menu items
    keyboard = []
    for item in items:
        keyboard.append([KeyboardButton(text=f"{item.name}")])
    
    keyboard.append([KeyboardButton(text="🔙 Назад к подкатегориям")])
    
    await state.set_state(OrderStates.selecting_menu_item)
    await message.answer(
        f"🍽️ <b>Выберите позицию из категории \"{category}\"</b>",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=keyboard,
            resize_keyboard=True
        )
    )

@router.message(OrderStates.entering_quantity)
async def process_quantity(message: Message, state: FSMContext):
    text = message.text
    
    if text == "Другое количество":
        await message.answer(
            "Введите количество (число):",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="🔙 Назад")]],
                resize_keyboard=True
            )
        )
        return
    
    if text == "🔙 Назад" or text == "🔙 Отмена":
        await back_to_items(message, state)
        return
    
    try:
        quantity = int(text)
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        await add_item_with_quantity(message, state, quantity)
    except ValueError:
        await message.answer(
            "❌ Пожалуйста, введите корректное положительное число.",
            reply_markup=get_quantity_keyboard()
        )

async def add_item_with_quantity(message, state, quantity):
    data = await state.get_data()
    order_id = data.get("current_order_id")
    item_id = data.get("current_item_id")
    main_category = data.get("current_main_category")
    
    order = order_manager.get_order_by_id(order_id)
    item = menu_manager.get_item_by_id(item_id)
    
    if not order or not item:
        await message.answer(
            "❌ Ошибка при добавлении позиции. Попробуйте снова.",
            reply_markup=get_main_keyboard()
        )
        return
    
    order.add_item(item, quantity)
    order_manager.save_orders()
    
    # Return to main category selection
    await state.set_state(OrderStates.selecting_main_category)
    await message.answer(
        f"✅ В заказ добавлено: {item.name} x{quantity}\n\n"
        "Выберите раздел меню или завершите заказ:",
        parse_mode="HTML",
        reply_markup=get_main_categories_keyboard()
    )

@router.message(OrderStates.viewing_order)
async def view_order(message: Message, state: FSMContext):
    text = message.text
    
    if text == "🔙 Вернуться в главное меню":
        await state.clear()
        await message.answer(
            "Вы вернулись в главное меню.",
            reply_markup=get_main_keyboard()
        )
        return
    
    # Get the order ID from state data
    data = await state.get_data()
    order_map = data.get("active_orders", {})
    order_id = order_map.get(text)
    
    if not order_id:
        await message.answer(
            "❌ Пожалуйста, выберите заказ из списка:",
            reply_markup=get_active_orders_keyboard()
        )
        return
    
    order = order_manager.get_order_by_id(order_id)
    if not order:
        await message.answer(
            "❌ Заказ не найден.",
            reply_markup=get_active_orders_keyboard()
        )
        return
    
    await state.update_data(current_order_id=order_id)
    await state.set_state(OrderStates.managing_order)
    
    order_text = format_order_text(order)
    
    await message.answer(
        f"📋 <b>Заказ для стола {order.table_number}</b>\n\n"
        f"{order_text}",
        parse_mode="HTML",
        reply_markup=get_order_actions_keyboard(order)
    )

@router.message(OrderStates.managing_order)
async def manage_order(message: Message, state: FSMContext):
    text = message.text
    data = await state.get_data()
    order_id = data.get("current_order_id")
    
    if text == "🔙 Назад к заказам":
        await back_to_active_orders(message, state)
        return
    
    order = order_manager.get_order_by_id(order_id)
    if not order:
        await message.answer(
            "❌ Заказ не найден.",
            reply_markup=get_main_keyboard()
        )
        return
    
    if text.startswith("➕ Добавить позиции"):
        # Set to main category selection first
        await state.set_state(OrderStates.selecting_main_category)
        await message.answer(
            f"🆕 <b>Добавление позиций в заказ стола {order.table_number}</b>\n\n"
            "Выберите раздел меню:",
            parse_mode="HTML",
            reply_markup=get_main_categories_keyboard()
        )
        return
    
    if text.startswith("✅ Закрыть заказ"):
        # Show order summary and confirm closing
        order_text = format_order_text(order)
        
        await state.set_state(OrderStates.confirm_close)
        
        await message.answer(
            f"⚠️ <b>Подтверждение закрытия заказа</b>\n\n"
            f"{order_text}\n\n"
            f"Вы действительно хотите закрыть заказ для стола {order.table_number}?",
            parse_mode="HTML",
            reply_markup=get_confirmation_keyboard()
        )
        return
    
    await message.answer(
        "❌ Пожалуйста, выберите действие из списка:",
        reply_markup=get_order_actions_keyboard(order)
    )

@router.message(OrderStates.confirm_close, F.text == "✅ Да, закрыть заказ")
async def confirm_close_order(message: Message, state: FSMContext):
    data = await state.get_data()
    order_id = data.get("current_order_id")
    
    if not order_id:
        await message.answer(
            "❌ Ошибка! Информация о заказе не найдена.",
            reply_markup=get_main_keyboard()
        )
        return
    
    # Get order before closing for summary
    order = order_manager.get_order_by_id(order_id)
    if not order:
        await message.answer(
            "❌ Заказ не найден! Возможно, он был уже закрыт.",
            reply_markup=get_main_keyboard()
        )
        return
    
    # Close the order
    if order_manager.close_order(order_id):
        # Format a nice receipt
        timestamp = datetime.fromisoformat(order.timestamp).strftime("%d.%m.%Y %H:%M")
        
        receipt = (
            f"✅ <b>ЗАКАЗ #{order.id} ЗАКРЫТ</b>\n\n"
            f"<b>Дата:</b> {timestamp}\n"
            f"<b>Стол:</b> {order.table_number}\n\n"
            f"<b>СОСТАВ ЗАКАЗА:</b>\n"
        )
        
        # List all ordered items
        items_by_category = {}
        for item in order.items:
            category = item.menu_item.category
            if category not in items_by_category:
                items_by_category[category] = []
            items_by_category[category].append(item)
        
        # Format items by category
        for category, items in items_by_category.items():
            receipt += f"<b>{category}:</b>\n"
            for i, item in enumerate(items, 1):
                menu_item = item.menu_item
                receipt += f"  {i}. {menu_item.name} x{item.quantity}\n"
        
        await message.answer(
            receipt,
            parse_mode="HTML",
            reply_markup=get_main_keyboard()
        )
    else:
        await message.answer(
            "❌ Ошибка при закрытии заказа!",
            reply_markup=get_main_keyboard()
        )

@router.message(OrderStates.confirm_close, F.text == "❌ Нет, отмена")
async def cancel_close_order(message: Message, state: FSMContext):
    data = await state.get_data()
    order_id = data.get("current_order_id")
    
    if not order_id:
        await message.answer(
            "❌ Ошибка! Информация о заказе не найдена.",
            reply_markup=get_main_keyboard()
        )
        return
        
    order = order_manager.get_order_by_id(order_id)
    if order:
        await state.set_state(OrderStates.managing_order)
        await message.answer(
            "Отмена закрытия заказа. Вы вернулись к управлению заказом.",
            reply_markup=get_order_actions_keyboard(order)
        )
    else:
        await message.answer(
            "❌ Заказ не найден.",
            reply_markup=get_main_keyboard()
        )

def format_order_text(order):
    """Format order details as text"""
    text = f"<b>Заказ #{order.id} (Стол {order.table_number})</b>\n\n"
    
    if not order.items:
        text += "Заказ пуст. Добавьте позиции из меню.\n"
        return text
    
    # Group items by category
    items_by_category = {}
    for item in order.items:
        category = item.menu_item.category
        if category not in items_by_category:
            items_by_category[category] = []
        items_by_category[category].append(item)
    
    # Format items by category
    for category, items in items_by_category.items():
        text += f"<b>{category}:</b>\n"
        for i, item in enumerate(items, 1):
            menu_item = item.menu_item
            text += f"    {i}. {menu_item.name} x{item.quantity}\n"
    
    text += "\n"
    
    return text 