import asyncio
import datetime
from datetime import time

from lib.database import Database

from lib.general.filters import Chat, Command
from lib.general.events import Event
from lib.general.middleware import CommandMiddleware, AccessMiddleware
from lib.general.router import Router
from lib.llms.dialog import Dialog
from lib.logger import log_stream, main_logger
from lib.init import llm_post_task_content, llm_summary_task
from lib.utils.check_time_interval import next_datetime_from_time
from lib.utils.telethon_utils import large_respond, get_messages

router = Router(lambda: Chat() & Command(), [AccessMiddleware()])


@router()
async def help(event: Event, db: Database):
    await event.respond(', '.join(map(lambda r: '/' + r.name, router.handlers[:-2])))


@router()
async def test(event: Event, db: Database):
    await event.respond('scheduled', schedule=datetime.datetime(2025, 8, 29, 19, 0) + datetime.timedelta(hours=-3))


@router()
async def previous_posts(event: Event, db: Database):
    await large_respond(event, f'{db.post_assistant}')


@router()
async def stop(event: Event, db: Database):
    await event.respond(f'Bot stopped.')
    await db.client.disconnect()


@router()
async def logs_file(event: Event, db: Database):
    if log_stream:
        await event.respond(file=log_stream.get_file())
    else:
        await event.respond('Nothing.')


@router()
async def logs(event: Event, db: Database):
    await large_respond(event, log_stream.logs)


@router()
async def limits(event: Event, db: Database):
    await event.respond(await db.openrouter.check_limits())


@router(middlewares=[CommandMiddleware()])
async def ask(event: Event, db: Database, arg):
    dialog = Dialog()
    dialog.add_user_message(arg)
    await event.respond("Question received.")
    main_logger.info(f'/ask {arg}')

    result = await db.post_assistant.llm_api.chat_complete(dialog, attempts=1)
    if not result:
        return await event.respond("Nothing.")

    dialog.add_assistant_message(result)
    main_logger.info(f'Answered question:\n{str(dialog)}')
    await event.respond(result)


@router(middlewares=[CommandMiddleware()])
async def set_model(event: Event, db: Database, arg):
    main_logger.info(f'Set model: {arg}')
    db.post_assistant.llm_api.model = arg
    await event.respond(f'Set model: {arg}')


@router()
async def change_api(event: Event, db: Database):
    if db.post_assistant.llm_api == db.openrouter:
        db.post_assistant.llm_api = db.mistral
        main_logger.info(f'Set api mistral')
        await event.respond(f'Set api mistral')
    else:
        db.post_assistant.llm_api = db.openrouter
        main_logger.info(f'Set model openrouter')
        await event.respond(f'Set api openrouter')


@router()
async def posting(event: Event, db: Database):
    db.params.is_posting = not db.params.is_posting
    await event.respond("Posting enabled." if db.params.is_posting else "Posting disabled.")


@router()
async def night_posting(event: Event, db: Database):
    db.params.is_night_posting = not db.params.is_night_posting
    await event.respond("Night posting enabled." if db.params.is_night_posting else "Night posting disabled.")


@router()
async def info(event: Event, db: Database):
    await event.respond(f"Stats:\n{db.stats}\nParams:\n{db.params}\nApi:\n{db.openrouter}")


@router()
async def reset_stats(event: Event, db: Database):
    db.stats.reset()
    await event.respond(f"Statistics reset.")


@router()
async def get_task_prompt(event: Event, db: Database):
    await event.respond(llm_post_task_content)
    await asyncio.sleep(2)
    await event.respond(llm_summary_task)


@router()
async def rotate_keys(event: Event, db: Database):
    db.params.keys.rotate_keys()
    db.openrouter.api_key = db.params.keys.get_key().get_secret_value()
    await event.respond(f"Current key {db.params.keys.get_key_number()}")


@router(middlewares=[CommandMiddleware(), AccessMiddleware(["olgagorla"])], override_middleware=True)
async def messages(event: Event, db: Database, arg):
    count = int(arg) if arg and arg.isdigit() else 3
    main_logger.info(f'/messages {count} started.')
    for message in await get_messages(db, "@petrovchanka_lera", count):
        if not message:
            continue

        await event.respond(message)
        await asyncio.sleep(5)
    main_logger.info(f'/messages {count} finished.')


@router(filter=Command('/'), override_filter=True)
async def another(event: Event, db: Database):
    await event.respond('команда непонятна')


@router(filter=Chat(), override_filter=True)
async def another(event: Event, db: Database):
    await event.respond('не, сообщения это не мое, знаю только команды')
    await help(event, db)
