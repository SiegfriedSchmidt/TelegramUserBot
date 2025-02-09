from telethon.tl.functions.channels import JoinChannelRequest
from lib.database import Database
from lib.logger import main_logger
from lib.post_assistant import Post


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
