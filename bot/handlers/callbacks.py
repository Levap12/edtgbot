from aiogram import F, Router, types, Bot
from aiogram.types import Message, CallbackQuery, FSInputFile
from bot.keyboards import user_keyboards
from aiogram.filters import CommandStart, Command
import os
from bot.utils import marzhapi
import asyncio
callback_router = Router()
from bot.utils.base64coding import encode
from dotenv import load_dotenv
from bot.utils.yoomonepay import create_payment
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv('../.env')
SUB_URL = os.getenv("SUB_URL")
TOKEN = os.getenv("TOKEN_TG")
bot = Bot(token=TOKEN)


user_last_interaction = {}
async def handle_message_edit(callback: CallbackQuery, new_text: str, new_reply_markup):
    user_id = callback.from_user.id
    current_time = asyncio.get_event_loop().time()

    # Проверка, что прошло достаточно времени с последнего взаимодействия
    if user_id in user_last_interaction:
        last_time = user_last_interaction[user_id]
        if current_time - last_time < .5:  # Например, 1 секунда
            await callback.answer("Подождите немного перед следующим нажатием.")
            return

    user_last_interaction[user_id] = current_time

    # Проверка, изменился ли текст сообщения или его разметка
    if callback.message.text != new_text or callback.message.reply_markup != new_reply_markup:
        await callback.message.edit_text(text=new_text, reply_markup=new_reply_markup, parse_mode='HTML', disable_web_page_preview=True)
    else:
        await callback.answer("Сообщение не изменено.")


# Обработчик команды /start
@callback_router.message(CommandStart())
async def cmd_start(message: types.Message):
    try:
        # Путь к изображению (file_id)
        image_path = "AgACAgQAAxkBAAIBamdU23ZiPgSLkqOIZrRXLYXBznSnAAJ-xjEb8PmgUo683NEpncO2AQADAgADeQADNgQ"

        # Логирование параметров
        logger.info(f"Команда /start: отправляем изображение {image_path} с клавиатурой.")

        create_user_result = await marzhapi.crate_user(message.from_user.id)  # создание пользователя в панеле VPN
        if create_user_result['status'] == 'ok':
            # Если пользователь успешно создан, отправляем уведомление в группу
            group_message = (
                f'🆕 Новый пользователь подключился!\n'
                f'Имя: {message.from_user.first_name}\n'
                f'ID пользователя: {message.from_user.id}\n'
                f'Username: @{message.from_user.username}'
            )
            await bot.send_message(chat_id=-1002286289168, text=group_message)
        text = '<b>Добро пожаловать в VOX VPN!</b>' \
               '\n\nМы гарантируем <b>стабильное соединение</b> и <b>высокую скорость</b> для комфортного использования.' \
               '\n\n<b>Один аккаунт — на всех устройствах:</b> VPN идеально работает как на <b>телефоне</b>, так и на <b>ПК.</b>' \
               '\n\n<b>Погнали!</b>' \
               '\n\n<b>🔹 Поддержка</b> @voxwork' \
               '\n🔹 <b>Отзывы</b> @voxglobal' \
               '\n🔸 <b>Профиль</b> /profile' \
               '\n\n<b>С уважением,</b>' \
               '\n<b>Команда VOX VPN</b> ⚡️'
        # Отправляем сообщение с картинкой и клавиатурой
        await message.answer_photo(photo=image_path, caption=text, reply_markup=user_keyboards.main_menu(), parse_mode="HTML")
    except Exception as e:
        logger.error(f"Ошибка в обработчике /start: {e}")
        await message.answer("Произошла ошибка при обработке команды /start.")


@callback_router.message(Command('profile'))
async def cmd_start(message: types.Message):
    user_info = await marzhapi.get_user_info(message.from_user.id)
    image_path = "AgACAgQAAxkBAAIBamdU23ZiPgSLkqOIZrRXLYXBznSnAAJ-xjEb8PmgUo683NEpncO2AQADAgADeQADNgQ"
    logger.info(f"Отправляем сообщение для получения профиля.")
    if user_info["subscription_status"] == 'active':
        sub_status = "✅ Активна"
    elif user_info["subscription_status"] == 'disabled' or 'expired':
        sub_status = "❌ Не активна"

    else:
        sub_status = "❓ Неизветсна ошибка"

    text = f'<b>Подписка: {sub_status}</b>\n' \
           f'├ ID: {message.from_user.id}\n' \
           f'├ Осталось дней: {user_info["remaining_days"]}\n' \
           f'└ Активна до: {user_info["expire_date"]}'  # ├└
    await message.answer_photo(photo=image_path, caption=text, reply_markup=user_keyboards.get_profile_kb(),
                                        parse_mode="HTML")

# Обработчик нажатий на кнопки
@callback_router.callback_query(F.data.in_(['buyvpn', 'chose_device','back_to_menu']))
async def handle_button_click(callback: types.CallbackQuery):
    try:
        action = callback.data
        logger.info(f"Пользователь выбрал действие: {action}")

        # Удаляем старое сообщение
        try:
            await callback.message.delete()
        except Exception as e:
            logger.error(f"Не удалось удалить сообщение: {e}")

        # Логируем, какое сообщение и клавиатуру мы отправляем
        if action == 'buyvpn':
            image_path = "AgACAgQAAxkBAAIBamdU23ZiPgSLkqOIZrRXLYXBznSnAAJ-xjEb8PmgUo683NEpncO2AQADAgADeQADNgQ"
            logger.info(f"Отправляем изображение {image_path} с клавиатурой для покупки VPN.")
            await callback.message.answer_photo(photo=image_path, reply_markup=user_keyboards.get_buyvpn_kb())
        elif action == 'chose_device':
            logger.info(f"Отправляем сообщение для получения бесплатного VPN.")

            text = f'{callback.from_user.first_name}, выберите тип вашего устройства ниже 👇 чтобы увидеть инструкцию по подключению'
            await callback.message.answer(text=text, reply_markup=user_keyboards.get_chose_device_kb())
        elif action == 'back_to_menu':
            image_path = "AgACAgQAAxkBAAIBamdU23ZiPgSLkqOIZrRXLYXBznSnAAJ-xjEb8PmgUo683NEpncO2AQADAgADeQADNgQ"
            logger.info(f"Отправляем сообщение для получения меню.")
            text = '<b>Добро пожаловать в VOX VPN!</b>' \
               '\n\nМы гарантируем <b>стабильное соединение</b> и <b>высокую скорость</b> для комфортного использования.' \
               '\n\n<b>Один аккаунт — на всех устройствах:</b> VPN идеально работает как на <b>телефоне</b>, так и на <b>ПК.</b>' \
               '\n\n<b>Погнали!</b>' \
               '\n\n<b>🔹 Поддержка</b> @voxwork' \
               '\n🔹 <b>Отзывы</b> @voxglobal' \
               '\n🔸 <b>Профиль</b> /profile' \
               '\n\n<b>С уважением,</b>' \
               '\n<b>Команда VOX VPN</b> ⚡️'
            await callback.message.answer_photo(photo=image_path, caption=text, reply_markup=user_keyboards.main_menu(),
                                                parse_mode="HTML")
        elif action == 'profile':
            user_info = await marzhapi.get_user_info(callback.from_user.id)
            image_path = "AgACAgQAAxkBAAIBamdU23ZiPgSLkqOIZrRXLYXBznSnAAJ-xjEb8PmgUo683NEpncO2AQADAgADeQADNgQ"
            logger.info(f"Отправляем сообщение для получения профиля.")
            if user_info["subscription_status"] == 'active':
                sub_status = "✅ Активна"
            elif user_info["subscription_status"] == 'disabled' or 'expired':
                sub_status = "❌ Не активна"

            else:
                sub_status = "❓ Неизветсна ошибка"

            text = f'<b>Подписка: {sub_status}</b>\n' \
                   f'├ ID: {callback.from_user.id}\n' \
                   f'├ Осталось дней: {user_info["remaining_days"]}\n' \
                   f'└ Активна до: {user_info["expire_date"]}'  # ├└
            await callback.message.answer_photo(photo=image_path, caption=text, reply_markup=user_keyboards.get_profile_kb(),
                                                parse_mode="HTML")
        # Отвечаем на callback
        # await callback.answer(f"Вы выбрали: {action}")

    except Exception as e:
        logger.error(f"Ошибка при обработке нажатия кнопки: {e}")
        await callback.answer("Произошла ошибка при обработке вашего запроса.")


async def handle_subscription(callback: CallbackQuery, months: int):
    user_id = callback.from_user.id
    try:
        await callback.message.delete()
    except Exception as e:
        logger.error(f"Не удалось удалить сообщение: {e}")

    logger.info(f"Функция handle_subscription")
    if months == 1:
        month_text = "месяц"
    elif 2 <= months <= 4:
        month_text = "месяца"
    elif months == 7:
        month_text = "месяца"
    else:
        month_text = "месяцев"

    text = f'ℹ️ Доступ на {months} {month_text}.'
    transfer_url = "https://t.me/voxwork"
    payment_link = await create_payment(user_id,months)
    await callback.message.answer(text=text, reply_markup=user_keyboards.get_payment_kb(payment_link, transfer_url))


@callback_router.callback_query(F.data.startswith('test_payment_'))
async def test_payment_cb(callback: CallbackQuery):
    months = int(callback.data.split('_')[-1])
    if months == 1:
        month_text = "месяц"
    elif months == 3:
        month_text = "месяца"
    elif months == 6:
        month_text = "месяцев"
    else:
        month_text = "месяцев"

    await marzhapi.extend_expire(callback.from_user.id,months)

    text = f'Оплата за {months} {month_text} успешно выполнена! Спасибо за покупку.'
    await handle_message_edit(callback, text, user_keyboards.get_mainmenu_kb())


# Обработчики для каждого периода подписки
@callback_router.callback_query(F.data == 'buyvpn_1')
async def buyvpn_1_cb(callback: CallbackQuery):
    await handle_subscription(callback, 1)


@callback_router.callback_query(F.data == 'buyvpn_3')
async def buyvpn_3_cb(callback: CallbackQuery):
    await handle_subscription(callback, 3)


@callback_router.callback_query(F.data == 'buyvpn_6')
async def buyvpn_6_cb(callback: CallbackQuery):
    await handle_subscription(callback, 6)


@callback_router.callback_query(F.data == 'buyvpn_7')
async def buyvpn_6_cb(callback: CallbackQuery):
    await handle_subscription(callback, 7)


@callback_router.callback_query(F.data.startswith('device_'))
async def device_connect(callback: CallbackQuery):
    device = callback.data.split('_')[-1]
    user_id = callback.from_user.id

    DEVICE_URLS = {
        "iphone": {
            "device": "iPhone",
            "download_url": "https://app.hiddify.com/ios",
            "connect_url": f"https://app.nockserv.cloud/?url=hiddify://import/{SUB_URL}/{encode(user_id)}#Vox%20VPN",
        },
        "android": {
            "device": "Android",
            "download_url": "https://app.hiddify.com/play",
            "connect_url": f"https://app.nockserv.cloud/?url=hiddify://import/{SUB_URL}/{encode(user_id)}#Vox%20VPN",
        },
        "windows": {
            "device": "Windows",
            "download_url": "https://app.hiddify.com/windows",
            "connect_url": f"https://app.nockserv.cloud/?url=hiddify://import/{SUB_URL}/{encode(user_id)}#Vox%20VPN",
        },
        "macos": {
            "device": "MacOS",
            "download_url": "https://app.hiddify.com/mac",
            "connect_url": f"https://app.nockserv.cloud/?url=hiddify://import/{SUB_URL}/{encode(user_id)}#Vox%20VPN",
        },
        # Добавьте другие устройства здесь
    }
    urls = DEVICE_URLS[device]
    text = f"<b>Подключение к VOX VPN для {urls['device']} за 2 шага:</b>" \
           "\n\n1. <b>Скачайте приложение.</b> " \
           "\nПосле установки обязательно откройте приложение и подтвердите разрешение на установку VPN-профилей." \
           "\n\n2. <b>Нажмите на кнопку «ПОДКЛЮЧИТЬСЯ».</b>" \
           "\n\n🚨 <b>Первые 7 дней – абсолютно бесплатно!</b>" \
           "\n\n💬 Круглосуточная поддержка: @voxwork"

    await handle_message_edit(callback, text, user_keyboards.get_device_kb(urls["download_url"], urls["connect_url"] ))


@callback_router.message(F.content_type == 'video')
async def get_file_id(message: types.Message):
    # Получаем file_id отправленного видео
    file_id = message.video.file_id
    await message.reply(f"Ваш file_id: {file_id}")


@callback_router.callback_query(F.data == 'instruction')
async def handle_connect(callback: CallbackQuery):
    logging.debug(f"instruction")
    try:
        await callback.message.delete()
    except Exception as e:
        logger.error(f"Не удалось удалить сообщение: {e}")
    try:
        file_id = 'BAACAgQAAxkBAAIHNmdz0HhbelJBxB-wkP__aL8D_mEoAAJbFgACQUCYUxGufhvsFKLcNgQ'
        await callback.message.answer_video(video=file_id,
                                            reply_markup=user_keyboards.get_instruction_kb())
    except:
        await callback.message.answer(
            text=f'Видео не найдено',
            parse_mode='HTML'
        )

