import asyncio
from telethon.tl.functions.channels import JoinChannelRequest
from lib.database import Database
from lib.general.events import Event
from lib.logger import main_logger
from lib.post_assistant import Post
from typing import List


async def notify(db: Database, message: str, log=False):
    for admin in db.admins:
        await db.client.send_message(admin, message)
    if log:
        main_logger.info(f'Notification: {message}')


async def join_channel(db: Database, channel_id: str):
    channel = await db.client.get_entity(channel_id)
    await db.client(JoinChannelRequest(channel))
    main_logger.info(f'Joined channel {channel_id}')


async def send_post(db: Database, post: Post):
    await db.client.forward_messages(db.neural_networks_channel, post.message)
    await db.client.send_message(
        db.neural_networks_channel,
        f'Summary of the previous post: {post.brief_information}'
    )


async def send_pending_posts(db: Database):
    count = len(db.params.pending_posts)
    if count == 0:
        return main_logger.info(f"No pending posts.")

    main_logger.info(f"Forward pending posts '{count}'")

    async def send_post_with_waiting(db: Database, post: Post, last: bool, waiting=10):
        await send_post(db, post)
        if not last:
            await asyncio.sleep(waiting)

    for idx, post in enumerate(db.params.pending_posts):
        await db.asyncio_workers.enqueue_task(send_post_with_waiting, db, post, idx == count - 1)

    db.params.pending_posts.clear()


async def large_respond(event: Event, obj: str | List[str], characters=2000, timeout=3):
    if not obj:
        await event.respond("Nothing.")
    elif isinstance(obj, str):
        for i in range(0, len(obj), characters):
            await event.respond(obj[i:i + characters])
            await asyncio.sleep(timeout)
    elif isinstance(obj, list):
        divided_message = []
        log = ''
        cnt = 0
        for item in obj:
            cnt += len(item)
            if cnt >= characters:
                divided_message.append(log)
                log = item
                cnt = len(item)

            log += item

        if log:
            divided_message.append(log)

        for message in divided_message:
            await event.respond(message)
            await asyncio.sleep(timeout)
