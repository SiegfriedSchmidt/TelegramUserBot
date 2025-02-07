from telethon import TelegramClient
from lib.asyncio_workers import AsyncioWorkers
from lib.config_reader import config
from lib.llm import Openrouter, PostAssistant
from lib.init import telegram_session_path


class Database:
    def __init__(self):
        self.admins = [config.telegram_admin.get_secret_value()]
        self.neural_networks_channel = int(config.telegram_channel.get_secret_value())
        self.is_posting = False

        self.asyncio_workers = AsyncioWorkers()
        self.openrouter = Openrouter(config.openrouter_api_key.get_secret_value(), self.asyncio_workers)
        self.post_assistant = PostAssistant(llm_api=self.openrouter)
        self.client = TelegramClient(
            telegram_session_path,
            int(config.telegram_api_id.get_secret_value()),
            config.telegram_api_hash.get_secret_value()
        )

    async def shutdown(self):
        await self.asyncio_workers.shutdown()
        await self.client.disconnect()
