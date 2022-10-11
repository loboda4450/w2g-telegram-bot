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
