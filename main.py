import asyncio
import signal
import nest_asyncio

from apscheduler.triggers.cron import CronTrigger
from telethon import events

from lib.init import llm_summary_task
from lib.llm import Dialog
from lib.logger import main_logger
from lib.database import Database
from lib.utils.telethon_utils import notify

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


async def on_day_start(db: Database):
    main_logger.info("Day start function triggered.")
    db.post_assistant.previous_posts.clear()


async def on_day_end(db: Database):
    main_logger.info("Day end function triggered.")
    dialog = Dialog()
    dialog.add_user_message(llm_summary_task)
    dialog.add_user_message(f'Previous Posts Information: [{db.post_assistant.get_previous_posts_for_llm()}]')
    result = await db.post_assistant.llm_api.chat_complete(dialog)
    await db.client.send_message(db.neural_networks_channel, result + '[сообщение сгенерировано автоматически]')


async def main():
    db = Database()
    await db.asyncio_workers.start(1)
    setup_signal_handlers(db)

    try:
        await db.client.connect()
        await on_start(db)

        # Scheduler
        trigger = CronTrigger(hour=db.params.night_interval[0].hour, minute=db.params.night_interval[0].minute)
        db.scheduler.add_job(on_day_end, trigger, args=(db,))

        trigger = CronTrigger(hour=db.params.night_interval[1].hour, minute=db.params.night_interval[1].minute)
        db.scheduler.add_job(on_day_start, trigger, args=(db,))

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
