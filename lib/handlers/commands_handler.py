import asyncio

from lib.database import Database

from lib.general.filters import Channel, Chat, Command, FilterType
from lib.general.events import Event
from lib.general.middleware import CommandMiddleware, AccessMiddleware
from lib.general.router import Router
from lib.llm import Dialog
from lib.logger import log_stream, main_logger
from lib.init import llm_task_content
from lib.post_assistant import Post
from lib.utils.telethon_utils import send_post

router = Router(lambda: Chat() & Command(), [AccessMiddleware()])


@router()
async def help(event: Event, db: Database):
    await event.respond(', '.join(map(lambda r: '/' + r.name, router.handlers[:-2])))


@router()
async def previous_posts(event: Event, db: Database):
    await event.respond(f'[{db.post_assistant.get_previous_posts_string()}]')


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
    if not log_stream:
        await event.respond('Nothing.')

    for block in log_stream.get_divided_log():
        await event.respond(block)
        await asyncio.sleep(1)


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
async def night_posting(event: Event, db: Database):
    db.params.is_night_posting = not db.params.is_night_posting
    await event.respond("Night posting enabled." if db.params.is_night_posting else "Night posting disabled.")


@router()
async def info(event: Event, db: Database):
    await event.respond(f"Stats:\n{db.stats}\nParams:\n{db.params}")


@router()
async def send_pending_posts(event: Event, db: Database):
    if len(db.params.pending_posts) == 0:
        return await event.respond("No pending posts.")

    await event.respond(f"Run worker with '{len(db.params.pending_posts)}' tasks.")
    main_logger.info(f"Forward pending posts '{len(db.params.pending_posts)}'")

    async def send_post_with_waiting(db: Database, post: Post, waiting=10):
        await send_post(db, post)
        await asyncio.sleep(waiting)

    for post in db.params.pending_posts:
        await db.asyncio_workers.enqueue_task(send_post_with_waiting, db, post)

    db.params.pending_posts.clear()


@router()
async def reset_stats(event: Event, db: Database):
    db.stats.reset()
    await event.respond(f"Statistics reset.")


@router()
async def reset_previous_posts(event: Event, db: Database):
    db.post_assistant.previous_posts = []
    await event.respond(f"Previous posts reset.")


@router()
async def get_task_prompt(event: Event, db: Database):
    await event.respond(llm_task_content)


@router(filter=Command('/'), override_filter=True)
async def another(event: Event, db: Database):
    await event.respond('команда непонятна')


@router(filter=Chat(), override_filter=True)
async def another(event: Event, db: Database):
    await event.respond('не, сообщения это не мое, знаю только команды')
    await help(event, db)
