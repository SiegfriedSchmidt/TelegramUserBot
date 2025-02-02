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

neural_networks_channel = 2276376102
admin = "GormCHEV"
openrouter = Openrouter()


@client.on(events.NewMessage)
async def my_event_handler(event: NewMessage.Event):
    try:
        chat = await event.get_chat()
        print(f"New message in channel '{chat.title}':\n{event.text}")
        await client.forward_messages("GormCHEV", event.message)
    except Exception as e:
        print("Error reading message")

    print('-' * 40)


async def join_channel(channel_id: str):
    channel = await client.get_entity(channel_id)
    await client(JoinChannelRequest(channel))
    print(f'Joined channel {channel_id}')


async def main():
    me = await client.get_me()
    print(me.phone)

    message = await client.send_message(2276376102, 'Working')
    # print(message.raw_text)


if __name__ == '__main__':
    with client:
        client.loop.run_until_complete(main())
        client.run_until_disconnected()
