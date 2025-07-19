# handlers.py
from aiogram import Router, F
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, Contact, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from utils import save_to_google_sheets, notify_admin

form_router = Router()

class LeadForm(StatesGroup):
    language = State()
    name = State()
    phone = State()
    country = State()
    services = State()

texts = {
    "ru": {
        "start": "Привет! 👋\n\nЯ помогу собрать ваши пожелания и передать их напрямую разработчику.\nПожалуйста, выберите язык, на котором вам будет удобно продолжить:",
        "name": "Как вас зовут?",
        "phone": "Отправьте номер телефона кнопкой ниже:",
        "phone_button": "📱 Отправить номер",
        "country": "Из какой вы страны?",
        "services": "Что вас интересует? Выберите всё, что нужно:",
        "done": "✅ Завершить",
        "options": [
            ("🤖 Бот", "srv_bot"),
            ("🌐 Лендинг", "srv_landing"),
            ("📊 Автоматизация (Google/Notion/CRM)", "srv_auto"),
            ("🔔 Уведомление о заявке", "srv_notify"),
            ("🗂 Внутренняя база", "srv_internal")
        ]
    },
    "en": {
        "start": "Hello! 👋\n\nI'll help collect your request and forward it directly to the developer.\nPlease select the language you prefer:",
        "name": "What's your name?",
        "phone": "Send your phone number via the button below:",
        "phone_button": "📱 Send phone number",
        "country": "Which country are you from?",
        "services": "What do you need? Choose all that apply:",
        "done": "✅ Done",
        "options": [
            ("🤖 Bot", "srv_bot"),
            ("🌐 Landing page", "srv_landing"),
            ("📊 Automation (Google/Notion/CRM)", "srv_auto"),
            ("🔔 Lead notifications", "srv_notify"),
            ("🗂 Internal database", "srv_internal")
        ]
    }
}

@form_router.message(F.text == "/start")
async def start(message: Message, state: FSMContext):
    await state.clear()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")]
    ])
    await message.answer(texts["ru"]["start"], reply_markup=kb)

@form_router.callback_query(F.data.startswith("lang_"))
async def set_language(callback: CallbackQuery, state: FSMContext):
    lang = callback.data.split("_")[1]
    await state.update_data(language=lang)
    await callback.message.delete()
    await callback.message.answer(texts[lang]["name"])
    await state.set_state(LeadForm.name)

@form_router.message(LeadForm.name)
async def get_name(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.update_data(name=message.text)
    lang = data["language"]
    button = KeyboardButton(text=texts[lang]["phone_button"], request_contact=True)
    kb = ReplyKeyboardMarkup(keyboard=[[button]], resize_keyboard=True)
    await message.answer(texts[lang]["phone"], reply_markup=kb)
    await state.set_state(LeadForm.phone)

@form_router.message(LeadForm.phone, F.contact)
async def get_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.contact.phone_number)
    data = await state.get_data()
    await message.answer(texts[data["language"]]["country"], reply_markup=ReplyKeyboardRemove())
    await state.set_state(LeadForm.country)

@form_router.message(LeadForm.country)
async def get_country(message: Message, state: FSMContext):
    await state.update_data(country=message.text)
    data = await state.get_data()
    lang = data["language"]

    buttons = [[InlineKeyboardButton(text=label, callback_data=value)] for label, value in texts[lang]["options"]]
    buttons.append([InlineKeyboardButton(text=texts[lang]["done"], callback_data="done")])

    await state.update_data(services=[])
    await message.answer(texts[lang]["services"], reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await state.set_state(LeadForm.services)

@form_router.callback_query(LeadForm.services)
async def select_services(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    service_map = {
        "srv_bot": "Бот",
        "srv_landing": "Лендинг",
        "srv_auto": "Автоматизация",
        "srv_notify": "Уведомление",
        "srv_internal": "Внутренняя база"
    }

    if callback.data == "done":
        await callback.message.delete()
        await finalize(callback.message, state)
        return

    service = service_map.get(callback.data)
    if not service:
        return

    services = data.get("services", [])
    if service not in services:
        services.append(service)
        await state.update_data(services=services)

    await callback.answer(f"Добавлено: {service}")

async def finalize(message: Message, state: FSMContext):
    data = await state.get_data()
    await save_to_google_sheets(data)
    await notify_admin(data)

    lang = data.get("language", "ru")
    done_text = "✅ Спасибо! Ваша заявка отправлена." if lang == "ru" else "✅ Thank you! Your request has been sent."
    await message.answer(done_text)
    await state.clear()
