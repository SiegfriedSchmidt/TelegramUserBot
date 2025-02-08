from telethon.tl.functions.channels import JoinChannelRequest
from lib.database import Database
from lib.logger import logger


async def notify(db: Database, message: str, log=False):
    for admin in db.admins:
        await db.client.send_message(admin, message)
    if log:
        logger.info(f'Notification: {message}')


async def join_channel(db: Database, channel_id: str):
    channel = await db.client.get_entity(channel_id)
    await db.client(JoinChannelRequest(channel))
    logger.info(f'Joined channel {channel_id}')
