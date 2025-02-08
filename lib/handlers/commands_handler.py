from lib.database import Database
from telethon import events

from lib.general.filters import Channel, Chat, Command, FilterType
from lib.general.events import Event
from lib.general.router import Router


def event_factory() -> Event:
    return events.NewMessage()


def filter_factory() -> FilterType:
    return Chat() & Command()


router = Router(event_factory, filter_factory)


# '/help, /show, /stop, /logs_file, /logs, /limits, /ask, /watch, /get_requests, /get_task_prompt'
# @router(filter=Channel())
# async def channel(event: Event, db: Database):
#     print(1)
#     # print(event.message.text)


@router()
async def help(event: Event, db: Database):
    await event.respond(', '.join(map(lambda r: '/' + r.name, router.handlers)))


@router()
async def lol(event: Event, db: Database):
    await event.respond('lol')


@router(filter=Command('/'), override_filter=True)
async def another(event: Event, db: Database):
    await event.respond('another')

# async def commands_handler(cmd: str):
#     if cmd == '/help':
#         await notify()
#     elif cmd == '/show':
#         await notify(f'''[{post_assistant.get_previous_posts_string()}]''')
#     elif cmd == '/stop':
#         await notify('Bot stopped.', log=True)
#         await client.disconnect()
#     elif cmd == '/logs_file':
#         await client.send_file(admin, log_stream.get_file())
#     elif cmd == '/logs':
#         await notify(str(log_stream))
#     elif cmd == '/limits':
#         await notify(await openrouter.check_limits())
#     elif cmd.split()[0] == '/ask':
#         messages = [
#             {
#                 "role": "user",
#                 "content": cmd[5:]
#             }
#         ]
#         result = await openrouter.chat_complete(messages, attempts=1)
#         await notify(result if result else "Nothing.")
#     elif cmd == '/watch':
#         is_watching = not is_watching
#         await notify("Watching enabled." if is_watching else "Watching disabled.")
#     elif cmd == '/get_requests':
#         await notify(
#             f"Number of requests {openrouter.successful_requests}/{openrouter.total_requests} (successful/total)."
#         )
#     elif cmd == '/get_task_prompt':
#         await notify(llm_task_content)
#     else:
#         await notify("Нифига не понимайт")
