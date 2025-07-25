import asyncio
from typing import Tuple

from lib.database import Database

from lib.general.filters import Channel, Chat, Command
from lib.general.events import Event
from lib.general.middleware import CommandMiddleware, AccessMiddleware
from lib.general.router import Router
from lib.llm import Dialog
from lib.logger import log_stream, main_logger
from lib.init import llm_task_content
from lib.post_assistant import Post
from lib.utils.telethon_utils import large_respond, send_pending_posts, get_messages

router = Router(lambda: Chat() & Command(), [AccessMiddleware()])


@router()
async def help(event: Event, db: Database):
    await event.respond(', '.join(map(lambda r: '/' + r.name, router.handlers[:-2])))


@router()
async def previous_posts(event: Event, db: Database):
    await large_respond(event, f'[{db.post_assistant.get_previous_posts_string()}]')


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

    result = await db.openrouter.chat_complete(dialog, attempts=1)
    if not result:
        return await event.respond("Nothing.")

    dialog.add_assistant_message(result)
    main_logger.info(f'Answered question:\n{str(dialog)}')
    await event.respond(result)


@router()
async def posting(event: Event, db: Database):
    db.params.is_posting = not db.params.is_posting
    await event.respond("Posting enabled." if db.params.is_posting else "Posting disabled.")


@router()
async def pending_posting(event: Event, db: Database):
    db.params.is_pending_posting = not db.params.is_pending_posting
    await event.respond("Pending posting enabled." if db.params.is_pending_posting else "Pending posting disabled.")


@router()
async def stub_posting_check(event: Event, db: Database):
    db.params.stub_posting_check = not db.params.stub_posting_check
    await event.respond(
        "Stub posting check enabled." if db.params.stub_posting_check else "Stub posting check disabled."
    )


@router()
async def night_posting(event: Event, db: Database):
    db.params.is_night_posting = not db.params.is_night_posting
    await event.respond("Night posting enabled." if db.params.is_night_posting else "Night posting disabled.")


@router()
async def info(event: Event, db: Database):
    await event.respond(f"Stats:\n{db.stats}\nParams:\n{db.params}\nApi:\n{db.openrouter}")


@router()
async def send_pending(event: Event, db: Database):
    if len(db.params.pending_posts) == 0:
        return await event.respond("No pending posts.")

    await event.respond(f"Run worker with '{len(db.params.pending_posts)}' tasks.")
    await send_pending_posts(db)
    await event.respond(f"Pending posts successfully sent.")


@router()
async def reset_stats(event: Event, db: Database):
    db.stats.reset()
    await event.respond(f"Statistics reset.")


@router()
async def reset_previous_posts(event: Event, db: Database):
    db.post_assistant.previous_posts.clear()
    await event.respond(f"Previous posts reset.")


@router()
async def get_task_prompt(event: Event, db: Database):
    await event.respond(llm_task_content)


@router()
async def rotate_keys(event: Event, db: Database):
    db.params.keys.rotate_keys()
    db.openrouter.api_key = db.params.keys.get_key()
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
