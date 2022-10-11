import asyncio
import logging

import aiohttp
import yaml
from json import loads, dumps
from telethon import TelegramClient, Button
from telethon.events import NewMessage, CallbackQuery, InlineQuery
from telethon.tl.types import InputWebDocument

from utils import headers, extract_url, get_videos
from database import get_value, create, exist


async def main(config):
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=config['log_level'])
    logger = logging.getLogger(__name__)
    if config['w2g_api_key']:
        api_key = config['w2g_api_key']
    else:
        raise Exception('There is no Watch2Gather API key in config file')

    max_results = config['max_results']
    yt_api_key = config['yt_api_key']

    # session = aiohttp.ClientSession()
    client = TelegramClient(**config['telethon_settings'])
    print("Starting")
    await client.start(bot_token=config['bot_token'])
    print("Started")

    @client.on(NewMessage(pattern='/start'))
    async def start(event):
        await event.reply('Witam', buttons=[Button.inline('Test')])

    @client.on(NewMessage(pattern='/new', incoming=True))
    async def new_room(event):
        async with aiohttp.ClientSession() as session:
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
                    f'Room assigned to your Telegram ID exists:'
                    f'\n\nhttps://w2g.tv/rooms/{get_value(event=event, key="streamkey")}')

    @client.on(NewMessage(pattern='/add', incoming=True))
    async def update(event):
        async with aiohttp.ClientSession() as session:
            url = await extract_url(event=event)

            body = {"w2g_api_key": api_key,
                    "add_items": [{"url": "https://www.youtube.com/watch?v=zfL1I7WpEdk", "title": "HGW"}]}

            streamkey = get_value(event=event, key='streamkey')

            async with session.post(
                    f'https://api.w2g.tv/rooms/{streamkey}/playlists/current/playlist_items/sync_update',
                    headers=headers, data=dumps(body)) as resp:
                if resp.status == 200:
                    await event.reply('Updated your current playlist with shared video!')
                else:
                    logger.debug(f'Status: {resp.status} Data: {await resp.read()}')
                    await event.reply('Something went wrong, try again :<')

    @client.on(InlineQuery(pattern="/update"))
    async def update_inline(event):
        videos = await get_videos(type='video', search_query=event.text[7:], api_key=yt_api_key, session=aiohttp.ClientSession(),
                                  max_result=max_results)
        await event.answer([event.builder.article(title=video['snippet']['title'],
                                                  description=f"Published by: {video['snippet']['channelTitle']}",
                                                  thumb=InputWebDocument(
                                                      url=video['snippet']['thumbnails']['default']['url'],
                                                      size=0,
                                                      mime_type='image/jpg',
                                                      attributes=[]),
                                                  text=f"/add https://www.youtube.com/watch?v={video['id']['videoId']}")
                            for video in videos])

    @client.on(NewMessage(pattern='/play'))
    async def play(event):
        ...

    async with client:
        print("Good morning!")
        await client.run_until_disconnected()


if __name__ == '__main__':
    with open("config.yml", 'r') as f:
        config = yaml.safe_load(f)
        asyncio.get_event_loop().run_until_complete(main(config))
