import os
import time
import requests
import logging
from urllib.parse import urlparse

# Initialize bot details
API_TOKEN = '7852289575:AAGPlh2IxbFJTpEoDnDuABslA4x-MoftiBY'  # Replace with your Bot API token
BASE_URL = f'https://api.telegram.org/bot{API_TOKEN}/'

# Create a directory to store the videos
download_path = './videos/'
if not os.path.exists(download_path):
    os.makedirs(download_path)

# Logging setup
logging.basicConfig(level=logging.INFO)

# Function to download file from a direct link
def download_from_url(url, file_name):
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(os.path.join(download_path, file_name), 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            logging.info(f"Video downloaded from link: {file_name}")
            return True
        return False
    except Exception as e:
        logging.error(f"Error downloading video: {str(e)}")
        return False

# Function to validate if the message contains a valid URL
def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

# Function to download Telegram-hosted video via file path
def download_file(file_path, file_name):
    file_url = f'{BASE_URL}file/bot{API_TOKEN}/{file_path}'
    return download_from_url(file_url, file_name)

# Function to get file information from Telegram
def get_file(file_id):
    response = requests.get(f'{BASE_URL}getFile?file_id={file_id}')
    if response.status_code == 200:
        result = response.json().get('result', {})
        return result.get('file_path')
    return None

# Function to send a message to the user
def send_message(chat_id, text):
    payload = {
        'chat_id': chat_id,
        'text': text
    }
    requests.post(f'{BASE_URL}sendMessage', data=payload)

# Function to handle incoming messages
def handle_message(message):
    chat_id = message['chat']['id']

    # Handle /start command
    if 'text' in message and message['text'] == '/start':
        send_message(chat_id, "Hi! Send me a video link, and I'll download it for you.")

    # Handle video file sent directly
    elif 'video' in message:
        video = message['video']
        file_id = video['file_id']
        file_name = f'{file_id}.mp4'

        # Get file path and download video
        file_path = get_file(file_id)
        if file_path:
            success = download_file(file_path, file_name)
            if success:
                send_message(chat_id, f"Video downloaded successfully: {file_name}")
            else:
                send_message(chat_id, "Failed to download video.")
        else:
            send_message(chat_id, "Could not retrieve file information.")

    # Handle link (URL) sent by the user
    elif 'text' in message and is_valid_url(message['text']):
        video_url = message['text']
        file_name = video_url.split("/")[-1]  # Use last part of the URL as file name

        # Download video from the link
        success = download_from_url(video_url, file_name)
        if success:
            send_message(chat_id, f"Video downloaded successfully: {file_name}")
        else:
            send_message(chat_id, "Failed to download video from the provided link.")
    else:
        send_message(chat_id, "Please send a valid video link or video file.")

# Function to fetch updates from Telegram
def get_updates(offset=None):
    url = f'{BASE_URL}getUpdates'
    params = {'timeout': 100, 'offset': offset}  # Long polling with a timeout
    response = requests.get(url, params=params)
    return response.json()

# Main function to continuously check for new updates
def main():
    logging.info("Bot started...")
    last_update_id = None

    while True:
        updates = get_updates(offset=last_update_id)
        if 'result' in updates and len(updates['result']) > 0:
            for update in updates['result']:
                last_update_id = update['update_id'] + 1  # Increment to the next update
                if 'message' in update:
                    handle_message(update['message'])

        time.sleep(1)  # Avoid hitting Telegram's API limit

if __name__ == '__main__':
    main()
