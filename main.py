import os
import asyncio
import re
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from pytube import YouTube

# Укажите ваш токен Telegram бота
BOT_TOKEN = ""

# Регулярное выражение для проверки ссылок на видео YouTube
YOUTUBE_REGEX = r'^(https?\:\/\/)?(www\.youtube\.com|youtu\.?be)\/.+$'

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

async def download_youtube_video(url):
    try:
        yt = YouTube(url)
        video = yt.streams.filter(only_audio=True).first()
        if video:
            filename = f"{yt.title}.mp3"
            video.download(filename=filename)
            return filename, yt.title
        else:
            return None, None
    except Exception as e:
        print(e)
        return None, None

@dp.message_handler(content_types=types.ContentType.TEXT)
async def handle_text(message: types.Message):
    for entity in message.entities:
        if entity.type == types.MessageEntityType.URL:
            url = message.text[entity.offset:entity.offset + entity.length]
            if re.match(YOUTUBE_REGEX, url):
                await handle_youtube_link(message, url)
                return
    await message.reply("Пожалуйста, отправьте ссылку на видео с YouTube.")

async def handle_youtube_link(message: types.Message, url: str):
    await message.reply("Начинаю скачивание и конвертацию...")
    filename, title = await download_youtube_video(url)
    if filename:
        await bot.send_audio(message.chat.id, audio=open(filename, 'rb'), title=title, caption="Ваш файл готов!")
        os.remove(filename)
    else:
        await message.reply("Что-то пошло не так. Пожалуйста, убедитесь, что ссылка ведет на видео с YouTube.")

if __name__ == '__main__':
    asyncio.run(dp.start_polling())
