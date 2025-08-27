import asyncio
from telethon.tl.functions.channels import JoinChannelRequest
from lib.database import Database
from lib.general.events import Event
from lib.logger import main_logger
from lib.post_assistant import Post
from typing import Iterable


async def notify(db: Database, message: str, log=False):
    for admin in db.admins:
        await db.client.send_message(admin, message)
    if log:
        main_logger.info(f'Notification: {message}')


async def join_channel(db: Database, channel_id: str):
    channel = await db.client.get_entity(channel_id)
    await db.client(JoinChannelRequest(channel))
    main_logger.info(f'Joined channel {channel_id}')


async def send_post(db: Database, post: Post, schedule=None):
    await db.client.forward_messages(db.neural_networks_channel, post.message, schedule=schedule)


async def get_messages(db: Database, channel_name: str, count: int):
    channel = await db.client.get_entity(channel_name)
    idx = 0
    messages = []
    async for message in db.client.iter_messages(channel):
        messages.append(message.text)
        idx += 1
        if idx == count:
            break

    return messages


async def large_respond(event: Event, obj: str | Iterable[str], timeout=3, characters=2000, maximum=4):
    if not obj:
        await event.respond("Nothing.")
    elif isinstance(obj, str):
        if len(obj) >= characters * 4:
            return await event.respond("Too large.")
        for i in range(0, len(obj), characters):
            await event.respond(obj[i:i + characters])
            await asyncio.sleep(timeout)
    elif isinstance(obj, Iterable):
        divided_message = []
        log = ''
        cnt = 0
        for item in obj:
            cnt += len(item)
            if cnt >= characters:
                divided_message.append(log)
                log = ''
                cnt = len(item)

            log += item

        if log:
            divided_message.append(log)

        if len(divided_message) >= maximum:
            return await event.respond("Too large.")

        for message in divided_message:
            await event.respond(message)
            await asyncio.sleep(timeout)
    else:
        await event.respond("I've get smth else than a str or Iterable.")

    return None
