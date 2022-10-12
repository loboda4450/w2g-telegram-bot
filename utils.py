import aiohttp
from telethon.events import NewMessage, InlineQuery
from telethon.tl.types import InputWebDocument

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


async def get_videos(type: str, search_query: str, api_key: str, session: aiohttp.ClientSession, max_results: int = 10):
    async with session.get('https://www.googleapis.com/youtube/v3/search', params={'part': 'snippet',
                                                                                   'q': search_query,
                                                                                   'maxResult': max_results,
                                                                                   'type': type,
                                                                                   'key': api_key}) as response:
        resp = await response.json()
        return resp['items']


async def parse_answer(event: InlineQuery, operation: str, yt_api_key: str, max_results: int = 10):
    videos = await get_videos(type='video',
                              search_query=event.text[7:],
                              api_key=yt_api_key,
                              session=aiohttp.ClientSession(),
                              max_results=max_results)

    await event.answer([event.builder.article(title=video['snippet']['title'],
                                              description=f"Published by: {video['snippet']['channelTitle']}",
                                              thumb=InputWebDocument(
                                                  url=video['snippet']['thumbnails']['default']['url'],
                                                  size=0,
                                                  mime_type='image/jpg',
                                                  attributes=[]),
                                              text=f"{operation} https://www.youtube.com/watch?v={video['id']['videoId']}")
                        for video in videos])
