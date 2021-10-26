import asyncio
import logging

import aiohttp
import yaml
from json import loads
from telethon import TelegramClient, Button
from telethon.events import NewMessage, CallbackQuery


async def main(config):
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=config['log_level'])
    # logger = logging.getLogger(__name__)

    api_key = 'abcdefghijklmnoprstuwxyzabcdefghijklmnoprstuwxyzabcdefghijklmnop'
    session = aiohttp.ClientSession()
    client = TelegramClient(**config['telethon_settings'])
    print("Starting")
    await client.start(bot_token=config['bot_token'])
    print("Started")

    @client.on(NewMessage(pattern='/start'))
    async def start(event):
        await event.reply('Witam', buttons=[Button.inline('Test')])

    @client.on(CallbackQuery(pattern='Test'))
    async def reply(event):
        async with session:
            headers = {'Accept': 'application/json',
                       'Content-Type': 'application/json'}
            body = {"w2g_api_key": api_key,
                    "share": "https://www.youtube.com/watch?v=8Wdp35Z-fRs",
                    "bg_color": "#00ff00",
                    "bg_opacity": "50"}

            data = {'headers': headers,
                    'body': body}

            async with session.post('https://w2g.tv/rooms/create.json', data=data) as resp:
                data = await resp.read()
                streamkey = loads(data.decode('utf-8'))['streamkey']
                await event.reply(f'https://w2g.tv/rooms/{streamkey}')

    async with client:
        print("Good morning!")
        await client.run_until_disconnected()


if __name__ == '__main__':
    with open("config.yml", 'r') as f:
        config = yaml.safe_load(f)
        asyncio.get_event_loop().run_until_complete(main(config))
