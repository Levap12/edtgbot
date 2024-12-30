from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Dict
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu() -> InlineKeyboardMarkup:
    # Главгвное меню

    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='КУПИТЬ VPN', callback_data='buyvpn')],
        [InlineKeyboardButton(text='БЕСПЛАТНЫЙ VPN', callback_data='chose_device')],
        [InlineKeyboardButton(text='ПОМОЩЬ', url='https://t.me/voxwork')]
    ])
    return ikb


def get_chose_device_kb() -> InlineKeyboardMarkup:
    # Главгвное меню

    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='📲 iPhone', callback_data='device_iphone')],
        [InlineKeyboardButton(text='🤖 Android', callback_data='device_android')],
        [InlineKeyboardButton(text='💻 Windows', callback_data='device_windows')],
        [InlineKeyboardButton(text='🍏 MacOS', callback_data='device_macos')],
        [InlineKeyboardButton(text='Назад', callback_data='back_to_menu')],
    ])
    return ikb


def get_device_kb(download_url:str ,connect_url:str) -> InlineKeyboardMarkup:
    # Главгвное

    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🌐 Скачать приложение ', url=download_url)],
        [InlineKeyboardButton(text='🚀 Подключиться ', url=connect_url)],
        [InlineKeyboardButton(text='ℹ️ Инструкция ', callback_data='instruction')],
        [InlineKeyboardButton(text='💠 Меню', callback_data='back_to_menu')]
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
        # [InlineKeyboardButton(text='Меню', callback_data='back_to_menu')]
    ])

    return ikb


def get_instruction_kb() -> InlineKeyboardMarkup:
    # Профиль меню

    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🚀 Подключиться', callback_data='chose_device')],
        # [InlineKeyboardButton(text='Меню', callback_data='back_to_menu')]
    ])

    return ikb


def get_buyvpn_kb() -> InlineKeyboardMarkup:
    # Купить ВПН меню

    ikb = InlineKeyboardMarkup(inline_keyboard=[
        # [InlineKeyboardButton(text='TEST', callback_data='buyvpn_7')],
        [InlineKeyboardButton(text='1 МЕСЯЦ - 200 РУБЛЕЙ', callback_data='buyvpn_1')],
         [InlineKeyboardButton(text='3 МЕСЯЦА - 600 РУБЛЕЙ', callback_data='buyvpn_3')],
         [InlineKeyboardButton(text='6 МЕСЯЦЕВ - 900 РУБЛЕЙ', callback_data='buyvpn_6')],
        [InlineKeyboardButton(text='Назад', callback_data='back_to_menu')]
    ])

    return ikb


def get_payment_kb(payment_url: str, transfer_url: str) -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Оплатить', url=payment_url)],
        [InlineKeyboardButton(text='Оплата переводом', url=transfer_url)],
        [InlineKeyboardButton(text='Назад', callback_data='buyvpn')]
    ])
    return ikb
