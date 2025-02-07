import asyncio
import signal
import nest_asyncio
from telethon import events

from lib.logger import logger
from lib.database import Database

from lib.handlers import commands_handler
from lib.utils.get_exception import get_exception

nest_asyncio.apply()


# async def join_channel(db: Database, channel_id: str):
#     channel = await db.client.get_entity(channel_id)
#     await db.client(JoinChannelRequest(channel))
#     logger.info(f'Joined channel {channel_id}')


async def notify(db: Database, message: str, log=False):
    for admin in db.admins:
        await db.client.send_message(admin, message)
    if log:
        logger.info(f'Notification: {message}')


def on_shutdown(db: Database, sig=0):
    if sig != 0:
        signal_name = "SIGINT" if sig == signal.SIGINT else "SIGTERM"
        logger.info(f"Program interrupted and terminated by signal {signal_name}.")
    # asyncio.run(notify(db, 'Bot stopped.', log=True))
    asyncio.run(db.shutdown())
    exit(0)


async def on_start(db: Database):
    me = await db.client.get_me()
    # await notify(db, 'Bot started.', log=True)


def setup_signal_handlers(db: Database):
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, on_shutdown, db, sig)


async def main():
    db = Database()
    await db.asyncio_workers.start(1)
    setup_signal_handlers(db)

    try:
        await db.client.connect()
        await on_start(db)

        # Events
        commands_handler.router.register_router(db.client, db)

        await db.client.run_until_disconnected()
    except KeyboardInterrupt:
        logger.info("Program terminated by KeyboardInterrupt.")
    except Exception as e:
        logger.error(f"Program terminated by Error: \n---\n{get_exception(e)}---")
    finally:
        on_shutdown(db)


if __name__ == '__main__':
    asyncio.run(main())
