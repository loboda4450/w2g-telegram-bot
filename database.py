from pony.orm import *
from logme import logme
import typing
from telethon.events import NewMessage, CallbackQuery, InlineQuery

db = Database("sqlite", "w2g.sqlite", create_db=True)


class Room(db.Entity):
    id = PrimaryKey(int, auto=True)
    ownerid = Required(int)
    streamkey = Required(str, unique=True)
    chatid = Optional(int)


db.generate_mapping(create_tables=True)


@db_session
@logme
def exist(event: typing.Union[NewMessage, InlineQuery], streamkey: typing.Optional[str] = None, chatid: typing.Optional[int] = None) -> bool:
    if chatid and streamkey:
        return Room.exists(ownerid=event.sender.id, streamkey=streamkey, chatid=chatid)
    elif chatid:
        return Room.exists(ownerid=event.sender.id, chatid=chatid)
    elif streamkey:
        return Room.exists(ownerid=event.sender.id, streamkey=streamkey)
    else:
        return Room.exists(ownerid=event.sender.id)


@db_session
@logme
def create(event: NewMessage, streamkey: str) -> bool:
    if isinstance(event, NewMessage.Event):
        Room(ownerid=event.sender.id, streamkey=streamkey)
        return True
    else:
        raise Exception('Wrong event type!')


@db_session
@logme
def get_value(event: NewMessage, key: typing.Optional[str] = None):
    if key == 'streamkey':
        return Room.get(ownerid=event.sender.id).streamkey
    elif key == 'chatid':
        return Room.get(ownerid=event.sender.id).chatid
    elif key == 'ownerid':
        return Room.get(ownerid=event.sender.id).ownerid
    else:
        return Room.get(ownerid=event.sender.id)

@db_session
@logme
def remove(event: typing.Union[NewMessage, CallbackQuery], streamkey: typing.Optional[str] = None) -> None:
    ...
