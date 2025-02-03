from telethon import TelegramClient, events
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.events import NewMessage
import asyncio
import signal

from lib.config_reader import config
from lib.init import telegram_session_path
from lib.logger import logger, log_stream
from lib.llm import Openrouter, PostAssistant
from lib.asyncio_workers import asyncio_workers

client = TelegramClient(
    telegram_session_path,
    config.telegram_api_id.get_secret_value(),
    config.telegram_api_hash.get_secret_value()
)

neural_networks_channel = int(config.telegram_channel.get_secret_value())
admin = config.telegram_admin.get_secret_value()
openrouter = Openrouter()
post_assistant = PostAssistant(llm_api=openrouter)


async def notify(message: str, log=False):
    await client.send_message(admin, message)
    if log:
        logger.info(f'Notification: {message}')


async def commands_handler(cmd: str):
    if cmd == '/help':
        await notify("/help, /show, /stop, /logs, /limits, /ask")
    elif cmd == '/show':
        await notify(f'''[{post_assistant.get_previous_posts_string()}]''')
    elif cmd == '/stop':
        await notify('Bot stopped.', log=True)
        await client.disconnect()
    elif cmd == '/logs':
        await client.send_file(admin, log_stream.get_file())
    elif cmd == '/limits':
        await notify(await openrouter.check_limits())
    elif cmd.split()[0] == '/ask':
        messages = [
            {
                "role": "user",
                "content": cmd[5:]
            }
        ]
        result = await openrouter.chat_complete(messages, attempts=1)
        await notify(result if result else "Nothing.")
    else:
        await notify("Нифига не понимайт")


@client.on(events.NewMessage)
async def my_event_handler(event: NewMessage.Event):
    chat = await event.get_chat()

    try:
        if chat.username == admin:
            await commands_handler(event.message.text)

        return
    except Exception as e:
        ...

    try:
        logger.info(f"New message in channel '{chat.title}'")
        text = event.text.strip()
        if not text:
            logger.info(f"Post message is empty")
            return

        success, meet_requirements, brief_information = await post_assistant.check_channel_message(text)
        if not success:
            ...
            # await notify('Ошибочка вышла, и по ходу дела не очень хорошая. Проблема в этом посте')
            # await client.forward_messages(admin, event.message)
        else:
            logger.info(f"Brief info: {brief_information}, meet_requirements: {meet_requirements}")
            if meet_requirements:
                await client.forward_messages(neural_networks_channel, event.message)
                await client.send_message(
                    neural_networks_channel,
                    f'Summary of the previous post: {brief_information}'
                )
    except Exception as e:
        logger.warning("Error reading message")


async def join_channel(channel_id: str):
    channel = await client.get_entity(channel_id)
    await client(JoinChannelRequest(channel))
    logger.info(f'Joined channel {channel_id}')


async def main():
    setup_signal_handlers()
    await asyncio_workers.start(num_workers=1)
    me = await client.get_me()
    await notify('Bot started.', log=True)

    await client.run_until_disconnected()


def terminate_by_signal():
    logger.info("Program interrupted and terminated by signal.")
    asyncio.create_task(asyncio_workers.shutdown())
    exit(0)


def setup_signal_handlers():
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, terminate_by_signal)


if __name__ == '__main__':
    try:
        with client:
            client.loop.run_until_complete(main())
    except KeyboardInterrupt:
        logger.info("Program interrupted and terminated.")
    finally:
        client.loop.run_until_complete(asyncio_workers.shutdown())
