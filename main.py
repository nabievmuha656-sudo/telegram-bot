import logging
import asyncio
from aiogram import Bot, Dispatcher, F, html
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
    InputMediaPhoto,
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

BOT_TOKEN = "8725238341:AAHh9V_rkSxdmlCH4zGl90VTke5Qbb798ew"

ADMIN_ID = 7464983977

PRICE = 250
KASPI_NUMBER = "+7 775 893 51 58"
KASPI_NAME = "Мухамед Н."

logging.basicConfig(level=logging.INFO)

bot = Bot(BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


class AdForm(StatesGroup):
    receipt = State()
    photos = State()
    description = State()
    price = State()
    phone = State()


def main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📢 Подать объявление")]
        ],
        resize_keyboard=True,
    )


def done_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Готово")]
        ],
        resize_keyboard=True,
    )


@dp.message(F.text == "/start")
async def start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Добро пожаловать!\n\nНажмите кнопку ниже, чтобы подать объявление.",
        reply_markup=main_keyboard(),
    )


@dp.message(F.text == "📢 Подать объявление")
async def new_ad(message: Message, state: FSMContext):
    await message.answer(
        f"💰 Стоимость публикации — {PRICE} ₸.\n\n"
        f"Kaspi: {KASPI_NUMBER}\n"
        f"Получатель: {KASPI_NAME}\n\n"
        "После оплаты отправьте фотографию чека.",
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(AdForm.receipt)
@dp.message(AdForm.receipt, F.photo)
async def receipt(message: Message, state: FSMContext):
    await state.update_data(receipt=message.photo[-1].file_id)
    await state.update_data(photos=[])

    await message.answer(
        "Теперь отправьте до 6 фотографий объявления.\nКогда закончите, нажмите ✅ Готово",
        reply_markup=done_keyboard()
    )

    await state.set_state(AdForm.photos)


@dp.message(AdForm.photos, F.photo)
async def photos(message: Message, state: FSMContext):

    data = await state.get_data()

    photos = data["photos"]

    if len(photos) >= 6:
        await message.answer("Максимум 6 фотографий.")
        return

    photos.append(message.photo[-1].file_id)

    await state.update_data(photos=photos)

    await message.answer(f"Добавлено {len(photos)}/6")


@dp.message(AdForm.photos, F.text == "✅ Готово")
async def done(message: Message, state: FSMContext):

    data = await state.get_data()

    if len(data["photos"]) == 0:
        await message.answer("Отправьте хотя бы одну фотографию.")
        return

    await message.answer("Введите описание.")

    await state.set_state(AdForm.description)

@dp.message(AdForm.description, F.text)
async def description(message: Message, state: FSMContext):

    await state.update_data(description=message.text)

    await message.answer("💰 Введите цену товара:")

    await state.set_state(AdForm.price)


@dp.message(AdForm.price, F.text)
async def price(message: Message, state: FSMContext):

    await state.update_data(price=message.text)

    await message.answer("📞 Введите номер телефона:")

    await state.set_state(AdForm.phone)


@dp.message(AdForm.phone, F.text)
async def phone(message: Message, state: FSMContext):

    await state.update_data(phone=message.text)

    data = await state.get_data()

    text = f"""
📢 НОВОЕ ОБЪЯВЛЕНИЕ

👤 Пользователь:
@{message.from_user.username}

📝 Описание:
{data['description']}

💰 Цена:
{data['price']}

📞 Телефон:
{data['phone']}
"""

    await bot.send_photo(
        ADMIN_ID,
        data["receipt"],
        caption="🧾 Чек об оплате"
    )

    media = []

    for i, photo in enumerate(data["photos"]):

        if i == 0:

            media.append(
                InputMediaPhoto(
                    media=photo,
                    caption=text
                )
            )

        else:

            media.append(
                InputMediaPhoto(
                    media=photo
                )
            )

    await bot.send_media_group(
        ADMIN_ID,
        media
    )

    await message.answer(
        "✅ Ваше объявление отправлено на проверку.\n\nПосле проверки администратор опубликует его."
    )

    await state.clear()
@dp.message(F.text == "🏠 Главное меню")
async def menu(message: Message, state: FSMContext):
    await state.clear()

    await message.answer(
        "Главное меню",
        reply_markup=main_keyboard()
    )


@dp.message()
async def unknown(message: Message):
    await message.answer(
        "Используйте кнопку «📢 Подать объявление»."
    )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
