import asyncio
import signal
import time
import nest_asyncio

from apscheduler.triggers.cron import CronTrigger
from telethon import events

from lib.logger import main_logger
from lib.database import Database
from lib.utils.telethon_utils import notify, send_pending_posts

from lib.handlers import commands_handler, channel_messages_handler
from lib.utils.get_exception import get_exception

nest_asyncio.apply()


def on_shutdown(db: Database, sig=0):
    if sig != 0:
        signal_name = "SIGINT" if sig == signal.SIGINT else "SIGTERM"
        main_logger.info(f"Program interrupted and terminated by signal {signal_name}.")
    asyncio.run(db.shutdown())
    exit(0)


async def on_start(db: Database):
    me = await db.client.get_me()
    await notify(db, 'Bot started.', log=True)


def setup_signal_handlers(db: Database):
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, on_shutdown, db, sig)


async def every_day_function(db: Database):
    main_logger.info("Every day function triggered.")
    db.post_assistant.previous_posts.clear()
    await send_pending_posts(db)


async def main():
    db = Database()
    await db.asyncio_workers.start(1)
    setup_signal_handlers(db)

    try:
        await db.client.connect()
        await on_start(db)

        # Scheduler
        trigger = CronTrigger(hour=db.params.night_interval[1].hour, minute=db.params.night_interval[1].minute)
        db.scheduler.add_job(every_day_function, trigger, args=(db,))
        db.scheduler.start()

        # Events
        db.client.add_event_handler(commands_handler.router.get_dispatcher(db), events.NewMessage())
        db.client.add_event_handler(channel_messages_handler.router.get_dispatcher(db), events.NewMessage())

        await db.client.run_until_disconnected()
        main_logger.info("Bot stopped.")
    except KeyboardInterrupt:
        main_logger.info("Program terminated by KeyboardInterrupt.")
    except Exception as e:
        main_logger.error(f"Program terminated by Error: {get_exception(e)}")
    finally:
        on_shutdown(db)


if __name__ == '__main__':
    asyncio.run(main())
