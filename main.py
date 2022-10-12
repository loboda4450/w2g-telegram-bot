import asyncio
import logging

import aiohttp
import yaml
from json import loads, dumps
from telethon import TelegramClient, Button
from telethon.events import NewMessage, InlineQuery

from utils import headers, extract_url, get_videos, parse_answer
from database import get_value, create, exist


async def main(config):
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=config['log_level'])
    logger = logging.getLogger(__name__)
    if config['w2g_api_key']:
        api_key = config['w2g_api_key']
    else:
        raise Exception('There is no Watch2Gather API key in config file')

    if config['max_results']:
        max_results = config['max_results']

    if config['yt_api_key']:
        yt_api_key = config['yt_api_key']
    else:
        raise Exception('There is no YouTube API key in config file')

    session = aiohttp.ClientSession()
    client = TelegramClient(**config['telethon_settings'])
    print("Starting")
    await client.start(bot_token=config['bot_token'])
    print("Started")

    @client.on(NewMessage(pattern='/start'))
    async def start(event):
        await event.reply('Witam', buttons=[Button.inline('Test')])

    @client.on(NewMessage(pattern='/new', incoming=True))
    async def new_room(event):
        if not session.closed:
            url = await extract_url(event=event)
            if not exist(event=event):
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
                body = {"w2g_api_key": api_key,
                        "add_items": [{"url": url, "title": "TBD"}]}

                async with session.post(
                        f'https://api.w2g.tv/rooms/{get_value(event=event, key="streamkey")}/playlists/current/playlist_items/sync_update',
                        headers=headers, data=dumps(body)) as resp:
                    if resp.status == 200:
                        await event.reply(
                            f'Room assigned to your Telegram ID exists:'
                            f'\n\nhttps://w2g.tv/rooms/{get_value(event=event, key="streamkey")}\n\n'
                            f'Updated with shared video!')
                    else:
                        logger.debug(f'Status: {resp.status} Data: {await resp.read()}')
                        await event.reply('Something went wrong, try again :<')

    @client.on(InlineQuery(pattern='/new'))
    async def new_inline(event):
        if not session.closed:
            await parse_answer(event=event, operation='/new', yt_api_key=yt_api_key, max_results=max_results)

    @client.on(NewMessage(pattern='/update', incoming=True))
    async def update(event):
        if not session.closed:
            url = await extract_url(event=event)

            body = {"w2g_api_key": api_key,
                    "add_items": [{"url": url, "title": " "}]}

            async with session.post(
                    f'https://api.w2g.tv/rooms/{get_value(event=event, key="streamkey")}/playlists/current/playlist_items/sync_update',
                    headers=headers, data=dumps(body)) as resp:
                if resp.status == 200:
                    await event.reply('Updated your current playlist with shared video!')
                else:
                    logger.debug(f'Status: {resp.status} Data: {await resp.read()}')
                    await event.reply('Something went wrong, try again :<')

    @client.on(InlineQuery(pattern="/update"))
    async def update_inline(event):
        if not session.closed:
            await parse_answer(event=event, operation='/update', yt_api_key=yt_api_key, max_results=max_results)

    @client.on(NewMessage(pattern='/play'))
    async def play(event):
        if not session.closed:
            url = await extract_url(event=event)

            body = {"w2g_api_key": api_key,
                    "item_url": url}

            async with session.post(
                    f'https://api.w2g.tv/rooms/{get_value(event=event, key="streamkey")}/sync_update',
                    headers=headers, data=dumps(body)) as resp:
                if resp.status == 200:
                    await event.reply('Playing immediately shared video!')
                else:
                    logger.debug(f'Status: {resp.status} Data: {await resp.read()}')
                    await event.reply('Something went wrong, try again :<')

    @client.on(InlineQuery(pattern='/play'))
    async def play_inline(event):
        if not session.closed:
            await parse_answer(event=event, operation='/play', yt_api_key=yt_api_key, max_results=max_results)

    async with client:
        print("Good morning!")
        await client.run_until_disconnected()


if __name__ == '__main__':
    with open("config.yml", 'r') as f:
        config = yaml.safe_load(f)
        asyncio.get_event_loop().run_until_complete(main(config))
