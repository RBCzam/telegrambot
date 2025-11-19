import asyncio
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.enums.parse_mode import ParseMode
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.client.default import DefaultBotProperties

# ==============================
# НАСТРОЙКИ
# ==============================
TOKEN = "8593802121:AAFRwoVPBwNgtllkPykl9QMlWbppHesNUeQ"
OWNER_ID = 1226120583  # ← твой Telegram ID

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# ==============================
# ХРАНЕНИЕ ПРЕДЛОЖЕНИЙ
# ==============================
user_proposals = {}      # {user_id: [messages]}
all_proposals = []       # [messages]
waiting_for_text = {}    # {user_id: True/False}

# ==============================
# /start — приветствие
# ==============================
@dp.message(Command("start"))
async def start_cmd(message: Message):
    await message.answer(
        "Привет! Я бот для анонимных предложений.\n"
        "Используй /helpme, чтобы посмотреть команды.\n"
        "Используй /proposal, чтобы анонимно написать своё предложение."
    )

# ==============================
# /helpme — список команд
# ==============================
@dp.message(Command("helpme"))
async def helpme_cmd(message: Message):
    await message.answer(
        "📌 Доступные команды:\n"
        "/proposal — меню с предложениями.\n"
        "/allproposal — все предложения (только владелец).\n"
        "/helpme — помощь."
    )

# ==============================
# /proposal — главное меню
# ==============================
@dp.message(Command("proposal"))
async def proposal_cmd(message: Message):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✍️ Написать предложение", callback_data="write_proposal")],
            [InlineKeyboardButton(text="📜 Мои предложения", callback_data="my_proposals_btn")]
        ]
    )
    await message.answer("Выберите действие:", reply_markup=kb)

# ==============================
# Кнопка "Написать предложение"
# ==============================
@dp.callback_query(F.data == "write_proposal")
async def callback_write_proposal(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    waiting_for_text[user_id] = True
    await callback.message.answer(
        "Напиши своё предложение, и я анонимно передам его администратору."
    )
    await callback.answer()

# ==============================
# Кнопка "Мои предложения"
# ==============================
@dp.callback_query(F.data == "my_proposals_btn")
async def callback_my_proposals(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    msgs = user_proposals.get(user_id)
    if not msgs:
        await callback.message.answer("У вас пока нет предложений.")
    else:
        text = "\n\n— ".join([""] + msgs)
        await callback.message.answer(f"Ваши предложения:\n— {text}")
    await callback.answer()

# ==============================
# Ловим текст пользователя
# ==============================
@dp.message()
async def handle_messages(message: Message):
    user_id = message.from_user.id

    # Если пользователь в режиме ввода — сохраняем предложение
    if waiting_for_text.get(user_id):
        text = message.text.strip()
        user_proposals.setdefault(user_id, []).append(text)
        all_proposals.append(text)
        try:
            await bot.send_message(OWNER_ID, f"📩 Новое анонимное предложение:\n{text}")
        except:
            pass
        await message.answer("Спасибо! Ваше предложение отправлено администраторам.")
        waiting_for_text[user_id] = False
        return

    # Любое сообщение, кроме команд — неизвестное
    if message.text and not message.text.startswith("/"):
        await message.answer("Я такого не знаю, упс 😅")

# ==============================
# /myproposal — показать мои предложения
# ==============================
@dp.message(Command("myproposal"))
async def myproposal_cmd(message: Message):
    user_id = message.from_user.id
    msgs = user_proposals.get(user_id)
    if not msgs:
        await message.answer("У вас пока нет предложений.")
        return
    text = "\n\n— ".join([""] + msgs)
    await message.answer(f"Ваши предложения:\n— {text}")

# ==============================
# /allproposal — для владельца
# ==============================
@dp.message(Command("allproposal"))
async def allproposal_cmd(message: Message):
    if message.from_user.id != OWNER_ID:
        await message.answer("Эта команда только для владельца бота 😎")
        return

    if not all_proposals:
        await message.answer("Пока нет ни одного предложения.")
        return

    text = "\n\n— ".join([""] + all_proposals)
    await message.answer(f"Все предложения:\n— {text}")

# ==============================
# Запуск бота
# ==============================
async def main():
    print("Удаляю вебхук...")
    await bot.delete_webhook(drop_pending_updates=True)
    print("Вебхук удалён, запускаем polling...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
