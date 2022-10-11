import asyncio
import logging

import aiohttp
import yaml
from json import loads, dumps
from telethon import TelegramClient, Button
from telethon.events import NewMessage, CallbackQuery
from utils import headers, extract_url
from database import get_value, create, exist


async def main(config):
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=config['log_level'])
    logger = logging.getLogger(__name__)
    if config['w2g_api_key']:
        api_key = config['w2g_api_key']
    else:
        raise Exception('There is no Watch2Gather API key in config file')

    session = aiohttp.ClientSession()
    client = TelegramClient(**config['telethon_settings'])
    print("Starting")
    await client.start(bot_token=config['bot_token'])
    print("Started")

    @client.on(NewMessage(pattern='/start'))
    async def start(event):
        await event.reply('Witam', buttons=[Button.inline('Test')])

    @client.on(NewMessage(pattern='/new'))
    async def new_room(event):
        async with session:
            if not exist(event=event):
                url = await extract_url(event=event)

                body = {"w2g_api_key": api_key,
                        "share": url,
                        "bg_color": "#00ff00",
                        "bg_opacity": "50"}

                async with session.post('https://api.w2g.tv/rooms/create.json', headers=headers,
                                        data=dumps(body)) as resp:
                    if resp.status == 200:
                        data = await resp.read()
                        streamkey = loads(data.decode('utf-8'))['streamkey']
                        if create(event=event, streamkey=streamkey):
                            await event.reply(f'Created room with your link! :)\n\n'
                                              f'https://w2g.tv/rooms/{streamkey}')
                    else:
                        logger.debug(f'Status: {resp.status} Data: {await resp.read()}')
                        await event.reply('Something went wrong, try again :<')

            else:
                await event.reply(
                    f'Room assigned to your Telegram ID exists:\n\nhttps://w2g.tv/rooms/{get_value(event=event, key="streamkey")}')

    # @client.on(NewMessage(incoming=True))
    # async def play(event):
    #     async with session:
    #         url = extract_url(event=event)
    #
    #         body = {"w2g_api_key": api_key,
    #                 "share": url}
    #
    #         streamkey = ...
    #
    #         async with session.post(
    #                 f'https://api.w2g.tv/rooms/{streamkey}/playlists/current/playlist_items/sync_update',
    #                 headers=headers, data=dumps(body)) as resp:
    #             if resp.status == 200:
    #                 ...
    #             else:
    #                 logger.debug(f'Status: {resp.status} Data: {await resp.read()}')
    #                 await event.reply('Something went wrong, try again :<')

    @client.on(NewMessage(pattern='/add'))
    async def add(event):
        ...

    @client.on(CallbackQuery(pattern='Test'))
    async def reply(event):
        ...

    async with client:
        print("Good morning!")
        await client.run_until_disconnected()


if __name__ == '__main__':
    with open("config.yml", 'r') as f:
        config = yaml.safe_load(f)
        asyncio.get_event_loop().run_until_complete(main(config))
