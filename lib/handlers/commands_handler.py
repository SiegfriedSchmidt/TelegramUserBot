from lib.config_reader import config
from lib.database import Database

from lib.general.filters import Channel, Chat, Command, FilterType
from lib.general.events import Event
from lib.general.middleware import CommandMiddleware, AccessMiddleware
from lib.general.router import Router
from lib.llm import Dialog
from lib.logger import log_stream
from lib.init import llm_task_content

router = Router(lambda: Chat() & Command(), AccessMiddleware([config.telegram_admin.get_secret_value()]))


@router()
async def help(event: Event, db: Database):
    await event.respond(', '.join(map(lambda r: '/' + r.name, router.handlers[:-2])))


@router()
async def show(event: Event, db: Database):
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
    await event.respond(str(log_stream) if log_stream else 'Nothing.')


@router()
async def limits(event: Event, db: Database):
    await event.respond(await db.openrouter.check_limits())


@router(middleware=CommandMiddleware())
async def ask(event: Event, db: Database, arg):
    dialog = Dialog()
    dialog.add_user_message(arg)
    result = await db.openrouter.chat_complete(dialog, attempts=1)
    await event.respond(result if result else "Nothing.")


@router()
async def watch(event: Event, db: Database):
    db.is_posting = not db.is_posting
    await event.respond("Posting enabled." if db.is_posting else "Posting disabled.")


@router()
async def get_requests(event: Event, db: Database):
    await event.respond(
        f"Number of requests {db.openrouter.successful_requests}/{db.openrouter.total_requests} (successful/total)."
    )


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
