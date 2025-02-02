from telethon import TelegramClient, events
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.events import NewMessage

from lib.config_reader import config
from lib.init import telegram_session_path
from lib.logger import logger
from lib.llm import Openrouter

client = TelegramClient(
    telegram_session_path,
    config.telegram_api_id.get_secret_value(),
    config.telegram_api_hash.get_secret_value()
)

neural_networks_channel = int(config.telegram_channel.get_secret_value())
admin = config.telegram_admin.get_secret_value()
openrouter = Openrouter()


async def notify(message: str):
    await client.send_message(admin, message)
    logger.info(f'Notification: {message}')


@client.on(events.NewMessage)
async def my_event_handler(event: NewMessage.Event):
    chat = await event.get_chat()

    try:
        if chat.username == admin:
            if event.message.text == '/help':
                await notify("/help, /show, /stop")
            elif event.message.text == '/show':
                await notify(f'''[{", ".join(map(lambda x: f'"{x}"', openrouter.previous_posts))}]''')
            elif event.message.text == '/stop':
                await notify('Bot stopped.')
                await client.disconnect()
            else:
                await notify("Нифига не понимайт")

            return
    except Exception as e:
        ...

    try:
        logger.info(f"New message in channel '{chat.title}'")
        success, meet_requirements, brief_information = await openrouter.check_channel_message(event.text)
        if not success:
            await notify('Ошибочка вышла, и по ходу дела не очень хорошая. Проблема в этом посте')
            await client.forward_messages(admin, event.message)
            return
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
    print(f'Joined channel {channel_id}')


async def main():
    me = await client.get_me()
    await notify('Bot started.')


if __name__ == '__main__':
    with client:
        client.loop.run_until_complete(main())
        client.run_until_disconnected()
