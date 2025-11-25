import asyncio
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.enums.parse_mode import ParseMode
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton
)
from aiogram.client.default import DefaultBotProperties

# ==============================
# НАСТРОЙКИ
# ==============================
TOKEN = "8593802121:AAFRwoVPBwNgtllkPykl9QMlWbppHesNUeQ"

ADMINS = [
    1226120583,  # ← твой ID
    2146799061   # ← второй админ
]

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# ==============================
# ХРАНЕНИЕ ДАННЫХ
# ==============================
user_proposals = {}
all_proposals = []
waiting_for_text = {}


# ==============================
# КЛАВИАТУРА
# ==============================
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="✍ Написать предложение"),
            KeyboardButton(text="📜 Мои предложения")
        ],
        [
            KeyboardButton(text="👑 Все предложения"),
            KeyboardButton(text="📚 Помощь")
        ]
    ],
    resize_keyboard=True
)


# ==============================
# /start
# ==============================
@dp.message(Command("start"))
async def start_cmd(message: Message):
    await message.answer(
        "Привет! Я бот для анонимных предложений.\n"
        "Выбирай действие на клавиатуре ниже 👇",
        reply_markup=main_kb
    )


# ==============================
# /helpme
# ==============================
@dp.message(Command("helpme"))
async def helpme_cmd(message: Message):
    await message.answer(
        "📌 Команды:\n"
        "/proposal — написать предложение\n"
        "/myproposal — ваши предложения\n"
        "/allproposal — все предложения (админы)\n"
        "/helpme — помощь",
        reply_markup=main_kb
    )


# ==============================
# REPLY КНОПКИ
# ==============================

@dp.message(F.text == "📚 Помощь")
async def btn_help(message: Message):
    await helpme_cmd(message)


@dp.message(F.text == "✍ Написать предложение")
async def btn_write_proposal(message: Message):
    user_id = message.from_user.id
    waiting_for_text[user_id] = True

    await message.answer(
        "Напиши своё предложение, и я передам его администраторам.",
        reply_markup=main_kb
    )


@dp.message(F.text == "📜 Мои предложения")
async def btn_my_proposals(message: Message):
    msgs = user_proposals.get(message.from_user.id)

    if not msgs:
        await message.answer("У вас пока нет предложений.")
    else:
        text = "\n\n— ".join([""] + msgs)
        await message.answer(f"Ваши предложения:\n— {text}")


@dp.message(F.text == "👑 Все предложения")
async def btn_all_proposals(message: Message):

    if message.from_user.id not in ADMINS:
        await message.answer("Эта функция доступна только администраторам 😎")
        return

    if not all_proposals:
        await message.answer("Пока нет предложений.")
        return

    text = "\n\n— ".join([""] + all_proposals)
    await message.answer(f"Все предложения:\n— {text}")


# ==============================
# ЛОВИМ ТЕКСТ — ПОЛЬЗОВАТЕЛЬ ПИШЕТ ПРЕДЛОЖЕНИЕ
# ==============================
@dp.message(F.text)
async def proposal_text_handler(message: Message):
    user_id = message.from_user.id

    # Если человек НЕ в режиме ввода — передаём дальше
    if not waiting_for_text.get(user_id):
        return

    text = message.text.strip()

    # сохраняем
    user_proposals.setdefault(user_id, []).append(text)
    all_proposals.append(text)

    # отправляем всем админам
    for admin_id in ADMINS:
        try:
            await bot.send_message(admin_id, f"📩 Новое анонимное предложение:\n{text}")
        except:
            pass

    await message.answer("Спасибо! Ваше предложение отправлено 😊")

    waiting_for_text[user_id] = False


# ==============================
# НЕИЗВЕСТНЫЕ СООБЩЕНИЯ
# ==============================
@dp.message()
async def unknown_message(message: Message):
    await message.answer("Я такого не знаю, упс 😅")


# ==============================
# ЗАПУСК
# ==============================
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())


