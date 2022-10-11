import aiohttp
from telethon.events import NewMessage

headers = {'Accept': 'application/json',
           'Content-Type': 'application/json'}


async def extract_url(event: NewMessage) -> str:
    if len(event.raw_text) > 4 and 'youtube.com/watch?v=' in event.raw_text:
        url = event.raw_text.split(' ', 1)[1]
    else:
        url = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'

    return url


async def check_streamkey(event: NewMessage) -> bool:
    ...


async def get_videos(type: str, search_query: str, api_key: str, session: aiohttp.ClientSession, max_result: int = 10):
    async with session.get('https://www.googleapis.com/youtube/v3/search', params={'part': 'snippet',
                                                                                   'q': search_query,
                                                                                   'maxResult': max_result,
                                                                                   'type': type,
                                                                                   'key': api_key}) as response:
        resp = await response.json()
        return resp['items']
