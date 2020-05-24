#!/usr/bin/env python
# -- coding: utf-8 --

from telethon import TelegramClient, sync
from telethon.tl.functions.photos import UploadProfilePhotoRequest, DeletePhotosRequest
import requests
import socks
from PIL import ImageDraw, Image, ImageFont
import time
import os

celsius = '°'
TEMP_PATH = 'temperature_images'
READY_PATH = 'ready_images'
WEATHER_PATH = 'weather_images'

location = 498817  # Saint-Petersburg
openweather_api_key = 'abcdefghi'

telegram_api_id = 1234567
telegram_api_hash = 'abcdefghi'

FONT_SIZE = 80
TEXT_Y_POSITION = 80

#proxy options
#w = input('Which: ')

host = '127.0.0.1'  # a valid host
port = 9050  # a valid port
proxy = (socks.SOCKS5, host, port)

icons = ["01d", "02d", "03d", "04d", "09d", "10d", "11d", "13d", "50d", "01n", "02n", "03n", "04n", "09n", "10n", "11n", "13n", "50n"]

# create all avatars
print('Start of  temperature images generation')
for temperature in range(-99, 99, 1):
    raw = Image.new('RGBA', (200, 200), "gray")
    parsed = ImageDraw.Draw(raw)
    length = len(str(temperature))
    if length == 1:
        x_start = 70
    if length == 2:
        x_start = 40
    if length == 3:
        x_start = 30

    font = ImageFont.truetype("arial.ttf", FONT_SIZE)
    parsed.text((x_start, TEXT_Y_POSITION), f'{temperature}{celsius}', align="center", font=font)
    raw.save(f'{TEMP_PATH}/{temperature}.png', "PNG")
print('Generating finished')

print('Beginning icons download')
for ic in icons:
    url = f'http://openweathermap.org/img/wn/{ic}@2x.png'
    r = requests.get(url)
    with open(f'{WEATHER_PATH}/{ic}.png', 'wb') as f:
        f.write(r.content)
    r.raise_for_status()
print('Download successfull')

print('Generate_final_images')
for temperature_file in os.listdir(f'{TEMP_PATH}'):
    if temperature_file.endswith(".png"):
        new_im = Image.open(f'{TEMP_PATH}/{temperature_file}')
        for weather_file in os.listdir(f'{WEATHER_PATH}'):
            if weather_file.endswith(".png"):
                im = Image.open(f'{WEATHER_PATH}/{weather_file}')
                test_img = Image.composite(im, new_im, im)
                temperature_file = temperature_file.strip('.png')
                weather_file = weather_file.replace('.png','')
                test_img.save(f'{READY_PATH}/{temperature_file}_{weather_file}.png')
print('done')

def get_temperature(weather_data):
    return round(weather_data['main']['temp'])
def get_conditions(weather_data):
    weath_array = weather_data['weather']
    weath_dict = weath_array[0]
    return weath_dict['icon']


def get_weather(location, api_key):
    url = f'https://api.openweathermap.org/data/2.5/weather?id={location}&units=metric&appid={api_key}'
    r = requests.get(url)
    return r.json()


client = TelegramClient('1', telegram_api_id, telegram_api_hash)
#client = TelegramClient('anon', telegram_api_id, telegram_api_hash, proxy=(socks.SOCKS5, '127.0.0.1', 9050))
client.connect()


client.start()

last_temperature = -274

while True:
    weather_data = get_weather(location, openweather_api_key)
    temperature = get_temperature(weather_data)
    conditions = get_conditions(weather_data)
    print(last_temperature, temperature)
    if temperature == last_temperature:
        time.sleep(15 * 60)
        continue

    client(DeletePhotosRequest(client.get_profile_photos('me')))
    file = client.upload_file(f'{READY_PATH}/{temperature}_{conditions}.png')
    client(UploadProfilePhotoRequest(file))
    last_temperature = temperature
    time.sleep(15 * 60)