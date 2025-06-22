"""
Common handlers and utilities for the restaurant Telegram bot.
Contains command handlers and basic navigation functions.
"""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext

router = Router()

# Main keyboard
def get_main_keyboard():
    """
    Create the main keyboard with primary bot functions.
    Returns a ReplyKeyboardMarkup with New Order, Active Orders, and Menu buttons.
    """
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🆕 Новый заказ")],
            [KeyboardButton(text="📋 Активные заказы")],
            [KeyboardButton(text="🍽️ Меню")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите действие"
    )
    return kb

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """
    Handler for the /start command.
    Shows welcome message and main keyboard.
    """
    await state.clear()
    await message.answer(
        "👋 Добро пожаловать в систему заказов для официантов!\n\n"
        "С помощью этого бота вы можете:\n"
        "• Создавать новые заказы\n"
        "• Просматривать активные заказы\n"
        "• Управлять меню заведения\n\n"
        "Используйте кнопки внизу для навигации.",
        reply_markup=get_main_keyboard()
    )

@router.message(Command("help"))
async def cmd_help(message: Message):
    """
    Handler for the /help command.
    Shows detailed help information about bot functions.
    """
    await message.answer(
        "📖 <b>Справка по использованию бота:</b>\n\n"
        "<b>🆕 Новый заказ</b> - создание нового заказа. Выберите стол и добавьте позиции из меню.\n\n"
        "<b>📋 Активные заказы</b> - просмотр и управление текущими заказами. Вы можете "
        "добавить позиции или закрыть заказ.\n\n"
        "<b>🍽️ Меню</b> - просмотр и редактирование меню заведения. Здесь можно добавлять "
        "и удалять позиции в разных категориях.\n\n"
        "<i>Для начала работы нажмите на одну из кнопок внизу.</i>",
        parse_mode="HTML",
        reply_markup=get_main_keyboard()
    )

@router.message(F.text == "🔙 Вернуться в главное меню")
async def return_to_main_menu(message: Message, state: FSMContext):
    """
    Handler for returning to the main menu.
    Clears state and shows main keyboard.
    """
    await state.clear()
    await message.answer(
        "Вы вернулись в главное меню.",
        reply_markup=get_main_keyboard()
    ) 