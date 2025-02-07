from lib.database import Database
from telethon import events

from lib.general.filters import Channel, Chat, Command, Event
from lib.general.router import Router

router = Router()


# '/help, /show, /stop, /logs_file, /logs, /limits, /ask, /watch, /get_requests, /get_task_prompt'
@router(events.NewMessage(), Channel())
async def channel(event: Event, db: Database):
    print(1)
    # print(event.message.text)


@router(events.NewMessage(), Chat() & Command('help'))
async def help(event: Event, db: Database):
    print(2)
    # await event.respond(', '.join(map(lambda r: '/' + r.name, router.handlers)))

@router(events.NewMessage(), Chat() & Command('lol'))
async def lol(event: Event, db: Database):
    print(3)
    # await event.respond(', '.join(map(lambda r: '/' + r.name, router.handlers)))

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
