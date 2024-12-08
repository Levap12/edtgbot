from aiogram import F, Router, types, Bot
from aiogram.types import Message, CallbackQuery, FSInputFile
from bot.keyboards import user_keyboards
from aiogram.filters import CommandStart
import os
from bot.utils import marzhapi
import asyncio
callback_router = Router()
from bot.utils.base64coding import encode
from dotenv import load_dotenv

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv('../.env')
SUB_URL = os.getenv("SUB_URL")
TOKEN = os.getenv("TOKEN_TG")
bot = Bot(token=TOKEN)

# @callback_router.callback_query(F.data == 'first_connect')
# async def first_connect(callback: CallbackQuery):
#     link = await marzhapi.crate_trial(callback.from_user.id)
#     text = '🪐 Подключение к Vless:' \
#            '\n' \
#            f'\n<code>{link}</code>' \
#            '\n👆 Нажмите чтобы скопировать!'
#
#     await callback.message.edit_text(text=text, reply_markup=user_keyboards.get_firstmsg_kb(), parse_mode='HTML')

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
               '\n\nМы гарантируем стабильность и высокую скорость!' \
               '\n\nА главное – наш VPN отлично работает как на телефоне, так и на ПК.' \
               '\n\nПогнали!' \
               '\n\n<b>Поддержка</b> @voxwork' \
               '\n<b>Новостной канал</b> @voxglobal' \
               '\nС уважением,' \
               '\nКоманда VOX VPN ⚡️'
        # Отправляем сообщение с картинкой и клавиатурой
        await message.answer_photo(photo=image_path, caption=text, reply_markup=user_keyboards.main_menu(), parse_mode="HTML")
    except Exception as e:
        logger.error(f"Ошибка в обработчике /start: {e}")
        await message.answer("Произошла ошибка при обработке команды /start.")


# Обработчик нажатий на кнопки
@callback_router.callback_query(F.data.in_(['buyvpn', 'chose_device','back_to_menu']))
async def handle_button_click(callback: types.CallbackQuery):
    try:
        action = callback.data
        logger.info(f"Пользователь выбрал действие: {action}")

        # Удаляем старое сообщение
        await callback.message.delete()

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
                   '\n\nМы гарантируем стабильность и высокую скорость!' \
                   '\n\nА главное – наш VPN отлично работает как на телефоне, так и на ПК.' \
                   '\n\nПогнали!' \
                   '\n\n<b>Поддержка</b> @voxwork' \
                   '\n<b>Новостной канал</b> @voxglobal' \
                   '\nС уважением,' \
                   '\nКоманда VOX VPN ⚡️'
            await callback.message.answer_photo(photo=image_path, caption=text, reply_markup=user_keyboards.main_menu(), parse_mode="HTML")

        # Отвечаем на callback
        # await callback.answer(f"Вы выбрали: {action}")

    except Exception as e:
        logger.error(f"Ошибка при обработке нажатия кнопки: {e}")
        await callback.answer("Произошла ошибка при обработке вашего запроса.")

# @callback_router.callback_query(F.data == 'profile')
# async def profile_cb(callback: CallbackQuery):
#     user_info = await marzhapi.get_user_info(callback.from_user.id)
#
#     if user_info["subscription_status"] == 'active':
#         sub_status = "✅ Активна"
#     elif user_info["subscription_status"] == 'disabled' or 'expired':
#         sub_status = "❌ Не активна"
#
#     else:
#         sub_status = "❓ Неизветсна ошибка"
#
#     text = f'<b>Подписка: {sub_status}</b>\n' \
#            f'├ ID: {callback.from_user.id}\n' \
#            f'├ Осталось дней: {user_info["remaining_days"]}\n' \
#            f'└ Активна до: {user_info["expire_date"]}'#├└
#
#     await handle_message_edit(callback, text, user_keyboards.get_profile_kb())


# @callback_router.callback_query(F.data == 'back_to_menu')
# async def back_to_main_cb(callback: CallbackQuery):
#     main_menu = 'Nock VPN — безопасная защита для вашей онлайн-жизни.\n' \
#                 '\n' \
#                 '🔥 Приобретайте подписку Nock VPN от 190₽\n' \
#                 '\n' \
#                 '⚡️ Подключайтесь к VPN, жмите на кнопку «Подключится»\n' \
#                 '\n' \
#                 'Вы можете управлять ботом следующими командами:'
#
#     await handle_message_edit(callback, main_menu, user_keyboards.get_main_kb())


# @callback_router.callback_query(F.data == 'buyvpn')
# async def buyvpn_cb(callback: CallbackQuery):
#     text = 'Для полного доступа выберите удобный для вас тариф:' \
#            '\n\n190₽ / 1 мес' \
#            '\n500₽ / 3 мес' \
#            '\n900₽ / 6 мес' \
#            '\n\n💳 К оплате принимаются карты РФ:' \
#            '\nVisa, MasterCard, МИР и криптовалюты.'
#
#
#     await handle_message_edit(callback, text, user_keyboards.get_buyvpn_kb())
#

async def handle_subscription(callback: CallbackQuery, months: int):
    user_id = callback.from_user.id
    await callback.message.delete()
    logger.info(f"Функция handle_subscription")
    if months == 1:
        month_text = "месяц"
    elif 2 <= months <= 4:
        month_text = "месяца"
    else:
        month_text = "месяцев"

    text = f'ℹ️ Доступ на {months} {month_text}.'
    payment_link = "https://t.me/nyrpeisov"
    await callback.message.answer(text=text, reply_markup=user_keyboards.get_payment_kb(payment_link, None))



    # await handle_message_edit(callback, text, user_keyboards.get_payment_kb(months, payment_link, None))
    # payment_link, error = await create_payment(user_id, months)
    # if payment_link:
    #     text = f'Доступ на {months} {month_text}'
    #     crypto_payment_url = f'https://crypto-payment.example.com/{months}_months'  # Замените на реальную ссылку
    #     await handle_message_edit(callback, text, user_keyboards.get_payment_kb(months, payment_link, crypto_payment_url))
    # else:
    #     await callback.message.answer(f"Ошибка создания ссылки: {error}")
    # await callback.message.answer(f'Для оплаты обратитесь в <a href="https://t.me/NockVPN_support">поддержку</a>', parse_mode='HTML')

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


@callback_router.callback_query(F.data == 'connect')
async def trial_shadowsocks_cb(callback: CallbackQuery):
    text = 'Выберите тип подключения 👇\n' \
           'Рекомендуем Vless'
    await handle_message_edit(callback, text, user_keyboards.get_connect_kb())

# @callback_router.callback_query(F.data == 'chose_device')
# async def chose_device(callback: CallbackQuery):
#     text = f'{callback.from_user.first_name}, выберите тип вашего устройства ниже 👇 чтобы увидеть инструкцию по подключению'
#     await handle_message_edit(callback, text, user_keyboards.get_chose_device_kb())

@callback_router.callback_query(F.data.startswith('device_'))
async def device_connect(callback: CallbackQuery):
    device = callback.data.split('_')[-1]
    user_id = callback.from_user.id

    DEVICE_URLS = {
        "iphone": {
            "device": "iPhone",
            "download_url": "https://app.hiddify.com/ios",
            "connect_url": f"https://apps.artydev.ru/?url=hiddify://import/{SUB_URL}/{encode(user_id)}#Vox%20VPN",
        },
        "android": {
            "device": "Android",
            "download_url": "https://app.hiddify.com/play",
            "connect_url": f"https://apps.artydev.ru/?url=hiddify://import/{SUB_URL}/{encode(user_id)}#Vox%20VPN",
        },
        "windows": {
            "device": "Windows",
            "download_url": "https://app.hiddify.com/windows",
            "connect_url": f"https://apps.artydev.ru/?url=hiddify://import/{SUB_URL}/{encode(user_id)}#Vox%20VPN",
        },
        "macos": {
            "device": "MacOS",
            "download_url": "https://app.hiddify.com/mac",
            "connect_url": f"https://apps.artydev.ru/?url=hiddify://import/{SUB_URL}/{encode(user_id)}#Vox%20VPN",
        },
        # Добавьте другие устройства здесь
    }
    urls = DEVICE_URLS[device]
    text = f"Подлючкение к VOX VPN для {urls['device']}" \
           "\nВам нужно сделать всего 2 шага:" \
           "\n\n1. Скачайте и установите приложение перейдя по кнопке" \
           "\n\n2. Нажимите на кнопку «ПОДКЛЮЧИТЬСЯ»" \
           "\n\n🚨 <b>Бесплатный период действует 3 дня!</b>" \
           "\n\nПосле истечения срока, вы можете оплатить на месяц и VPN в приложении автоматически продлится и продолжит работать."


    await handle_message_edit(callback, text, user_keyboards.get_device_kb(urls["download_url"], urls["connect_url"] ))



@callback_router.callback_query(F.data == 'vless')
async def trial_vless_cb(callback: CallbackQuery):
    text = '🪐 Подключение к VPN:' \
           '\n' \
           '\nВаша ссылка:' \
           f'\n└<code>{SUB_URL}/{encode(callback.from_user.id)}</code>' \
           '\nНажмите (тапните) чтобы скопировать и добавьте в приложение' \
           '\n' \
           '\nЕсли приложение уже установлено - воспользуйтесь <b>быстрым подключением</b>' \
           '\n- <a href="https://apps.apple.com/us/app/streisand/id6450534064">Streisand</a> - для iOS 🍏' \
           '\n- <a href="https://play.google.com/store/apps/details?id=com.v2ray.ang">v2rayNG</a> - для Android 🤖' \
           '\n' \
           '\nПодключить в <b>1 клик!</b>' \
           f'\n<a href="https://apps.artydev.ru/?url=streisand://import/{SUB_URL}/{encode(callback.from_user.id)}#Nock%20VPN">iOS</a>' \
           f'\n<a href="https://apps.artydev.ru/?url=v2rayng://install-config?url={SUB_URL}/{encode(callback.from_user.id)}">Android</a>' \
           '\n' \
           '\n⭐️ Если у вас Android(v2rayNG) - нажмите в приложении "..." - Обновить подписку' \
           '\n' \
           '\nПосмотреть подробную инструкцию 👇'
    await handle_message_edit(callback, text, user_keyboards.get_vless_con_kb())


@callback_router.message(F.content_type == 'video')
async def get_file_id(message: types.Message):
    # Получаем file_id отправленного видео
    file_id = message.video.file_id
    await message.reply(f"Ваш file_id: {file_id}")


# Обработчик callback-запросов для отправки видео
@callback_router.callback_query(lambda callback: callback.data in ['video_ios', 'video_mac', 'video_win', 'video_android'])
async def send_video(callback: types.CallbackQuery):
    try:
        # Словарь с параметрами для разных платформ
        video_data = {
            'video_ios': {
                'file_id': 'BAACAgQAAxkBAAIBOmcaHKmob-v6srPRPIM16-Il2YYmAAIkGAACmHxpUHQBCLbNDQn9NgQ',
                'caption': "Видео инструкция для IOS 🍏"
            },
            'video_mac': {
                'file_id': 'BAACAgQAAxkBAAIBPWcaHRElJOlM15LVME9Sa2w5X1MyAALbFQACmr6wUHidqln6cqO-NgQ',
                'caption': "Видео инструкция для mac OS"
            },
            'video_win': {
                'file_id': 'BAACAgIAAxkBAAMiZxj65u4ZxQldw3Sxg3H7KxL2-v0AAvJVAAJcmMlIyZHuytJiyn82BA',
                'caption': "Видео инструкция для Windows"
            },
            'video_android': {
                'file_id': 'BAACAgIAAxkBAAMiZxj65u4ZxQldw3Sxg3H7KxL2-v0AAvJVAAJcmMlIyZHuytJiyn82BA',
                'caption': "Видео инструкция для Android"
            }
        }

        # Получаем параметры в зависимости от платформы
        video_info = video_data.get(callback.data, {})
        file_id = video_info.get('file_id')
        caption = video_info.get('caption', "Видео инструкция")

        # Клавиатура для всех платформ одинакова
        keyboard = user_keyboards.get_support_kb()

        # Отправляем видео
        if file_id:
            await callback.message.answer_video(
                video=file_id,
                caption=caption
            )

            # Отправляем текст с клавиатурой после видео
            await callback.message.answer(
                text='🌐 Проблемы с подключением ???\n\n❗️Напишите оператору, мы работаем 24/7 👇',
                reply_markup=keyboard
            )
        else:
            await callback.message.answer("Не удалось найти видео для выбранной платформы.")

    except Exception as e:
        await callback.message.answer(f"Ошибка при отправке: {str(e)}")


# /sub/eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMTExMSIsImFjY2VzcyI6InN1YnNjcmlwdGlvbiIsImlhdCI6MTcxNjQwOTE0Nn0.0JnskQ2WHt_JEj6v5xUzD85-vjcHzi1eF92IyS4URug
# /sub/eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMTExMSIsImFjY2VzcyI6InN1YnNjcmlwdGlvbiIsImlhdCI6MTcxNjQxMDA5OX0.7MjY1IDfK1T97zSUrWH-e42ySV3mreD_lSL4qYnkJNc


# @callback_router.callback_query(F.data.startswith('outline'))
# async def trial_shadowsocks_cb(callback: CallbackQuery):
#     text = '🪐 Подключение к Outline VPN:' \
#            '\n\n<code>ssconf://users.outline.artydev.ru/conf/959fc2d1ec5e0x1af70d27#nRomania</code>' \
#             '\n👆 Нажмите чтобы скопировать!' \
#            '\n\nПосмотреть 👉 инструкцию (https://telegra.ph/Podklyuchenie-k-Outline-VPN-08-11)'
#
#     await callback.message.edit_text(text=text, reply_markup=user_keyboards.get_connected_kb(), parse_mode='HTML',disable_web_page_preview=True)




# @callback_router.callback_query(F.data.startswith('trial_shadowsocks_'))
# async def trial_shadowsocks_cb(callback: CallbackQuery):
#     country_id = callback.data.split('_')[-1]
#     print(f'{country_id}')
#     if country_id == "nl":
#         panel = Marzban(os.getenv("MARZH_LOGIN"), os.getenv("MARZH_PWD"), "https://vm13139.vpsone.xyz")
#         token = await panel.get_token()
#         expire_time = datetime.utcnow() + timedelta(days=1)  # Установка времени истечения срока действия на 1 день
#         expire_timestamp = int(expire_time.timestamp())
#         user = User(
#             username="new_user",  # Задайте уникальное имя пользователя
#             proxies={
#                 "shadowsocks": {}
#             },
#             inbounds={"shadowsocks": ["Shadowsocks TCP"]},  # Установка входящих соединений для Shadowsocks
#             expire=expire_timestamp,  # Установка времени истечения срока действия
#             data_limit=1024 * 1024 * 1024 * 15,  # Установка лимита данных, если необходимо
#             data_limit_reset_strategy="no_reset",  # Стратегия сброса лимита данных
#             status="active"  # Статус пользователя
#         )
#
#         result = await panel.add_user(user=user, token=token)
#
#         await callback.message.edit_text(text=result.links[0], reply_markup=await user_keyboards.get_trial_shadowsocks_countries_kb())

