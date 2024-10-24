from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Dict
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_first_start_kb() -> InlineKeyboardMarkup:
    # Главгвное меню

    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🔌 Подключиться', callback_data='vless')]
    ])
    return ikb


def get_main_kb() -> InlineKeyboardMarkup:
    # Главгвное меню

    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🕹 Профиль', callback_data='profile'),InlineKeyboardButton(text='🛒 Купить VPN', callback_data='buyvpn')],
        [InlineKeyboardButton(text='🚀️ Подключится ', callback_data='vless')],
        [InlineKeyboardButton(text='⚙️ Поддержка', url='https://t.me/NockVPN_support')]
    ])
    return ikb

def get_mainmenu_kb() -> InlineKeyboardMarkup:
    # Главгвное меню

    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Главное меню', callback_data='back_to_menu')]
    ])
    return ikb

def get_profile_kb() -> InlineKeyboardMarkup:
    # Профиль меню

    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='⏳ Продлить подписку', callback_data='buyvpn')],
        [InlineKeyboardButton(text='Назад', callback_data='back_to_menu')]
    ])

    return ikb

def get_buyvpn_kb() -> InlineKeyboardMarkup:
    # Купить ВПН меню

    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='1 месяц', callback_data='buyvpn_1')],
         [InlineKeyboardButton(text='3 месяца', callback_data='buyvpn_3')],
         [InlineKeyboardButton(text='6 месяцев', callback_data='buyvpn_6')],
        [InlineKeyboardButton(text='Назад', callback_data='back_to_menu')]
    ])

    return ikb

def get_payment_kb(months: int, payment_url: str, crypto_payment_url: str) -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='✍ Написать', url=payment_url)],
        [InlineKeyboardButton(text='Назад', callback_data='back_to_menu')]
    ])
    return ikb


def get_support_kb() -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='✍ Написать', url='https://t.me/NockVPN_support')],
        [InlineKeyboardButton(text='Меню', callback_data='back_to_menu')]
    ])
    return ikb


def get_connect_kb() -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🧦 Outline', callback_data='outline'),InlineKeyboardButton(text='🛡 Vless', callback_data='vless')],
        [InlineKeyboardButton(text='Назад', callback_data='back_to_menu')]
    ])
    return ikb

def get_connected_kb() -> InlineKeyboardMarkup:

    ikb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Быстрое подключение', callback_data='connect_web')],
                                                [InlineKeyboardButton(text='Главное меню', callback_data='back_to_menu')]])

    return ikb


def get_vless_con_kb() -> InlineKeyboardMarkup:
    # Главгвное меню

    # ikb = InlineKeyboardMarkup(inline_keyboard=[
    #     [InlineKeyboardButton(text='для IOS(Iphone) 🍏', callback_data='video_ios'),InlineKeyboardButton(text='для Android 🤖', callback_data='video_android')],
    #     [InlineKeyboardButton(text='для mac OS 🍏', callback_data='video_mac'),
    #      InlineKeyboardButton(text='для Windows 💻', callback_data='video_win')],
    #     [InlineKeyboardButton(text='Главное меню', callback_data='back_to_menu')]
    # ])
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='для IOS(Iphone) 🍏', callback_data='video_ios'), InlineKeyboardButton(text='для Android 🤖', callback_data='video_android')],
        [InlineKeyboardButton(text='для mac OS 🍏', callback_data='video_mac')],
        [InlineKeyboardButton(text='Главное меню', callback_data='back_to_menu')]
    ])
    return ikb