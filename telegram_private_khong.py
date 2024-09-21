import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import ContentType

# Initialize bot and dispatcher
API_TOKEN = '7852289575:AAGPlh2IxbFJTpEoDnDuABslA4x-MoftiBY'  # Replace with your Bot API token
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Create a directory to store the videos
download_path = './videos/'
if not os.path.exists(download_path):
    os.makedirs(download_path)

logging.basicConfig(level=logging.INFO)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Hi! Send me a video and I'll download it.")

@dp.message_handler(content_types=[ContentType.VIDEO])
async def download_video(message: types.Message):
    try:
        video = message.video
        file_id = video.file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path
        file_name = f"{file_id}.mp4"
        video_file_path = os.path.join(download_path, file_name)

        # Download video
        await bot.download_file(file_path, video_file_path)
        await message.reply(f"Video downloaded successfully: {file_name}")
    except Exception as e:
        await message.reply(f"An error occurred: {str(e)}")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
