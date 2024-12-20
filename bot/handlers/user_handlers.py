from aiogram import Router,Dispatcher,F,Bot, types
from bot.keyboards.user_keyboards import main_menu
from aiogram.types import Message, FSInputFile
from bot.utils import marzhapi
from dotenv import load_dotenv
import os
import logging
command_router = Router()
load_dotenv('../.env')

token = os.getenv("TOKEN_TG")
bot = Bot(token=token)#'7464437998:AAHovjFWytYVAwi8_qk2RnfyIXh2HxhM0pM')

@command_router.message(F.content_type == 'photo')
async def get_file_id(message: types.Message):
    # Получаем file_id самого большого фото
    if message.photo:
        file_id = message.photo[-1].file_id  # Последний элемент обычно самый большой
        await message.reply(f"Ваш file_id: {file_id}")
    else:
        await message.reply("Фото не было отправлено.")
