"""
Menu handling module for the restaurant Telegram bot.
Handles menu viewing and management (adding/deleting items).
"""
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from models.menu import menu_manager
from handlers.common import get_main_keyboard

# Define states for menu management
class MenuStates(StatesGroup):
    """States for menu management flow"""
    main_menu = State()
    edit_menu = State()
    adding_item_main_category = State()
    adding_item_category = State()
    adding_item_name = State()
    deleting_main_category = State()
    deleting_category = State()
    deleting_item_select = State()
    confirm_delete = State()

router = Router()

# Keyboards
def get_menu_main_keyboard():
    """Create a keyboard with 'Edit Menu' and 'Back' options"""
    keyboard = [
        [KeyboardButton(text="⚙️ Изменить меню")],
        [KeyboardButton(text="🔙 Вернуться в главное меню")]
    ]
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Выберите действие"
    )

def get_edit_menu_keyboard():
    """Create a keyboard with menu editing options"""
    keyboard = [
        [KeyboardButton(text="➕ Добавить позицию")],
        [KeyboardButton(text="➖ Удалить позицию")],
        [KeyboardButton(text="🔙 Назад в меню")]
    ]
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Выберите действие"
    )

def get_main_categories_keyboard():
    """Create a keyboard with main categories (Кухня/Бар)"""
    main_categories = menu_manager.get_main_categories()
    keyboard = []
    
    for category in main_categories:
        keyboard.append([KeyboardButton(text=category)])
    
    keyboard.append([KeyboardButton(text="🔙 Назад")])
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Выберите категорию"
    )

def get_subcategories_keyboard(main_category):
    """Create a keyboard with subcategories for the selected main category"""
    subcategories = menu_manager.get_subcategories(main_category)
    keyboard = []
    
    # Add subcategories in rows of 2
    for i in range(0, len(subcategories), 2):
        row = []
        row.append(KeyboardButton(text=subcategories[i]))
        if i + 1 < len(subcategories):
            row.append(KeyboardButton(text=subcategories[i + 1]))
        keyboard.append(row)
    
    keyboard.append([KeyboardButton(text="🔙 Назад к категориям")])
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Выберите подкатегорию"
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

# Handlers
@router.message(F.text == "🍽️ Меню")
async def show_menu(message: Message, state: FSMContext):
    """Handler for the main menu button"""
    await state.set_state(MenuStates.main_menu)
    await message.answer(
        "🍽️ <b>Меню ресторана</b>\n\n"
        "Выберите действие:",
        parse_mode="HTML",
        reply_markup=get_menu_main_keyboard()
    )

# Main menu handlers
@router.message(MenuStates.main_menu)
async def handle_main_menu(message: Message, state: FSMContext):
    text = message.text
    
    if text == "⚙️ Изменить меню":
        await state.set_state(MenuStates.edit_menu)
        await message.answer(
            "⚙️ <b>Изменение меню</b>\n\n"
            "Выберите действие:",
            parse_mode="HTML",
            reply_markup=get_edit_menu_keyboard()
        )
        return
    
    if text == "🔙 Вернуться в главное меню":
        await state.clear()
        await message.answer(
            "Вы вернулись в главное меню.",
            reply_markup=get_main_keyboard()
        )
        return
    
    await message.answer(
        "❌ Пожалуйста, выберите действие из списка:",
        reply_markup=get_menu_main_keyboard()
    )

# Edit Menu Handlers
@router.message(MenuStates.edit_menu)
async def handle_edit_menu(message: Message, state: FSMContext):
    text = message.text
    
    if text == "➕ Добавить позицию":
        await add_item_start(message, state)
    elif text == "➖ Удалить позицию":
        await delete_item_start(message, state)
    elif text == "🔙 Назад в меню":
        await back_to_menu(message, state)
    else:
        await message.answer(
            "❌ Пожалуйста, выберите действие из списка:",
            reply_markup=get_edit_menu_keyboard()
        )

@router.message(F.text == "🔙 Назад в меню")
async def back_to_menu(message: Message, state: FSMContext):
    await state.set_state(MenuStates.main_menu)
    await message.answer(
        "🍽️ <b>Меню ресторана</b>\n\n"
        "Выберите действие:",
        parse_mode="HTML",
        reply_markup=get_menu_main_keyboard()
    )

# Add item handlers
async def add_item_start(message: Message, state: FSMContext):
    main_categories = menu_manager.get_main_categories()
    keyboard = []
    
    for category in main_categories:
        keyboard.append([KeyboardButton(text=category)])
    
    keyboard.append([KeyboardButton(text="🔙 Назад")])
    
    await state.set_state(MenuStates.adding_item_main_category)
    await message.answer(
        "➕ <b>Добавление новой позиции</b>\n\n"
        "Выберите основную категорию (Кухня/Бар):",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=keyboard,
            resize_keyboard=True,
            input_field_placeholder="Выберите категорию"
        )
    )

@router.message(MenuStates.adding_item_main_category)
async def select_add_main_category(message: Message, state: FSMContext):
    main_category = message.text
    
    if main_category == "🔙 Назад":
        await state.set_state(MenuStates.edit_menu)
        await message.answer(
            "⚙️ <b>Изменение меню</b>\n\n"
            "Выберите действие:",
            parse_mode="HTML",
            reply_markup=get_edit_menu_keyboard()
        )
        return
    
    main_categories = menu_manager.get_main_categories()
    if main_category not in main_categories:
        await message.answer(
            "❌ Пожалуйста, выберите категорию из списка.",
            parse_mode="HTML"
        )
        return
    
    await state.update_data(new_item_main_category=main_category)
    
    # Get subcategories for the selected main category
    subcategories = menu_manager.get_subcategories(main_category)
    keyboard = []
    
    for subcategory in subcategories:
        keyboard.append([KeyboardButton(text=subcategory)])
    
    keyboard.append([KeyboardButton(text="🔙 Назад")])
    
    await state.set_state(MenuStates.adding_item_category)
    await message.answer(
        f"➕ <b>Добавление позиции</b>\n\n"
        f"Выбрана основная категория: {main_category}\n"
        f"Выберите подкатегорию:",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=keyboard,
            resize_keyboard=True
        )
    )

@router.message(MenuStates.adding_item_category)
async def select_add_category(message: Message, state: FSMContext):
    category = message.text
    data = await state.get_data()
    main_category = data.get("new_item_main_category")
    
    if category == "🔙 Назад":
        await add_item_start(message, state)
        return
    
    subcategories = menu_manager.get_subcategories(main_category)
    if category not in subcategories:
        await message.answer(
            "❌ Пожалуйста, выберите подкатегорию из списка.",
            parse_mode="HTML"
        )
        return
    
    await state.update_data(new_item_category=category)
    await state.set_state(MenuStates.adding_item_name)
    
    await message.answer(
        f"➕ <b>Добавление позиции в категорию: {category}</b>\n\n"
        "Введите название блюда:",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="🔙 Назад")]],
            resize_keyboard=True
        )
    )

@router.message(MenuStates.adding_item_name)
async def process_item_name(message: Message, state: FSMContext):
    name = message.text
    
    if name == "🔙 Назад":
        data = await state.get_data()
        main_category = data.get("new_item_main_category")
        
        await state.set_state(MenuStates.adding_item_category)
        subcategories = menu_manager.get_subcategories(main_category)
        keyboard = []
        
        for subcat in subcategories:
            keyboard.append([KeyboardButton(text=subcat)])
        
        keyboard.append([KeyboardButton(text="🔙 Назад")])
        
        await message.answer(
            "Выберите подкатегорию для новой позиции:",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=keyboard,
                resize_keyboard=True,
                input_field_placeholder="Выберите подкатегорию"
            )
        )
        return
    
    await state.update_data(new_item_name=name)
    
    # Add the menu item directly without asking for price
    data = await state.get_data()
    category = data.get("new_item_category")
    main_category = data.get("new_item_main_category")
    
    # Add the item with category and main_category
    menu_manager.add_item(name=name, category=category, main_category=main_category)
    
    await state.set_state(MenuStates.edit_menu)
    await message.answer(
        f"✅ Позиция \"{name}\" успешно добавлена в категорию \"{category}\".",
        reply_markup=get_edit_menu_keyboard()
    )

# Delete item handlers
async def delete_item_start(message: Message, state: FSMContext):
    main_categories = menu_manager.get_main_categories()
    keyboard = []
    
    for category in main_categories:
        keyboard.append([KeyboardButton(text=category)])
    
    keyboard.append([KeyboardButton(text="🔙 Назад")])
    
    await state.set_state(MenuStates.deleting_main_category)
    await message.answer(
        "➖ <b>Удаление позиции</b>\n\n"
        "Выберите основную категорию (Кухня/Бар):",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=keyboard,
            resize_keyboard=True
        )
    )

@router.message(MenuStates.deleting_main_category)
async def select_delete_main_category(message: Message, state: FSMContext):
    main_category = message.text
    
    if main_category == "🔙 Назад":
        await state.set_state(MenuStates.edit_menu)
        await message.answer(
            "⚙️ <b>Изменение меню</b>\n\n"
            "Выберите действие:",
            parse_mode="HTML",
            reply_markup=get_edit_menu_keyboard()
        )
        return
    
    main_categories = menu_manager.get_main_categories()
    if main_category not in main_categories:
        await message.answer(
            "❌ Пожалуйста, выберите категорию из списка.",
            parse_mode="HTML"
        )
        return
    
    await state.update_data(delete_main_category=main_category)
    
    # Get subcategories for the selected main category
    subcategories = menu_manager.get_subcategories(main_category)
    keyboard = []
    
    for subcategory in subcategories:
        keyboard.append([KeyboardButton(text=subcategory)])
    
    keyboard.append([KeyboardButton(text="🔙 Назад")])
    
    await state.set_state(MenuStates.deleting_category)
    await message.answer(
        f"➖ <b>Удаление позиции</b>\n\n"
        f"Выбрана основная категория: {main_category}\n"
        f"Выберите подкатегорию:",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=keyboard,
            resize_keyboard=True
        )
    )

@router.message(MenuStates.deleting_category)
async def select_delete_category(message: Message, state: FSMContext):
    category = message.text
    data = await state.get_data()
    main_category = data.get("delete_main_category")
    
    if category == "🔙 Назад":
        await delete_item_start(message, state)
        return
    
    subcategories = menu_manager.get_subcategories(main_category)
    if category not in subcategories:
        await message.answer(
            "❌ Пожалуйста, выберите подкатегорию из списка.",
            parse_mode="HTML"
        )
        return
    
    items = menu_manager.get_menu_items_by_category(category)
    
    if not items:
        await state.set_state(MenuStates.edit_menu)
        await message.answer(
            f"❌ В категории \"{category}\" нет позиций.",
            reply_markup=get_edit_menu_keyboard()
        )
        return
    
    await state.update_data(delete_category=category)
    
    keyboard = []
    for item in items:
        keyboard.append([KeyboardButton(text=item.name)])
    
    keyboard.append([KeyboardButton(text="🔙 Назад")])
    
    await state.set_state(MenuStates.deleting_item_select)
    await message.answer(
        f"➖ <b>Удаление позиции из категории: {category}</b>\n\n"
        "Выберите позицию для удаления:",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=keyboard,
            resize_keyboard=True
        )
    )

@router.message(MenuStates.deleting_item_select)
async def confirm_delete_item(message: Message, state: FSMContext):
    item_name = message.text
    
    if item_name == "🔙 Назад":
        data = await state.get_data()
        main_category = data.get("delete_main_category")
        await state.set_state(MenuStates.deleting_category)
        
        # Get subcategories and show keyboard again
        subcategories = menu_manager.get_subcategories(main_category)
        keyboard = []
        for subcategory in subcategories:
            keyboard.append([KeyboardButton(text=subcategory)])
        keyboard.append([KeyboardButton(text="🔙 Назад")])
        
        await message.answer(
            f"➖ <b>Удаление позиции</b>\n\n"
            f"Выбрана основная категория: {main_category}\n"
            f"Выберите подкатегорию:",
            parse_mode="HTML",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=keyboard,
                resize_keyboard=True
            )
        )
        return
    
    data = await state.get_data()
    category = data.get("delete_category")
    
    # Find the item
    items = menu_manager.get_menu_items_by_category(category)
    item = next((item for item in items if item.name == item_name), None)
    
    if not item:
        await message.answer(
            "❌ Позиция не найдена.",
            reply_markup=get_edit_menu_keyboard()
        )
        return
    
    await state.update_data(delete_item_id=item.id, delete_item_name=item.name)
    
    keyboard = [
        [KeyboardButton(text="✅ Да"), KeyboardButton(text="❌ Нет")]
    ]
    
    await state.set_state(MenuStates.confirm_delete)
    await message.answer(
        f"⚠️ <b>Подтверждение удаления</b>\n\n"
        f"Вы действительно хотите удалить \"{item.name}\" из меню?",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=keyboard,
            resize_keyboard=True
        )
    )

@router.message(MenuStates.confirm_delete)
async def final_delete_item(message: Message, state: FSMContext):
    response = message.text
    
    if response == "❌ Нет":
        data = await state.get_data()
        category = data.get("delete_category")
        main_category = data.get("delete_main_category")
        
        # Go back to item selection
        items = menu_manager.get_menu_items_by_category(category)
        keyboard = []
        for item in items:
            keyboard.append([KeyboardButton(text=item.name)])
        keyboard.append([KeyboardButton(text="🔙 Назад")])
        
        await state.set_state(MenuStates.deleting_item_select)
        await message.answer(
            f"➖ <b>Удаление позиции из категории: {category}</b>\n\n"
            "Выберите позицию для удаления:",
            parse_mode="HTML",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=keyboard,
                resize_keyboard=True
            )
        )
        return
    
    if response == "✅ Да":
        data = await state.get_data()
        item_id = data.get("delete_item_id")
        item_name = data.get("delete_item_name")
        category = data.get("delete_category")
        
        success = menu_manager.delete_item(item_id)
        
        await state.set_state(MenuStates.edit_menu)
        if success:
            await message.answer(
                f"✅ Позиция \"{item_name}\" успешно удалена из категории \"{category}\".",
                reply_markup=get_edit_menu_keyboard()
            )
        else:
            await message.answer(
                "❌ Ошибка при удалении позиции.",
                reply_markup=get_edit_menu_keyboard()
            )
    else:
        await message.answer(
            "❌ Пожалуйста, выберите Да или Нет.",
            parse_mode="HTML"
        ) 