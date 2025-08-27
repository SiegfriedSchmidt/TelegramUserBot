from telethon import TelegramClient
from lib.asyncio_workers import AsyncioWorkers
from lib.config_reader import config
from lib.llms.mistral import Mistral
from lib.llms.openrouter import Openrouter
from lib.params import Params
from lib.post_assistant import PostAssistant
from lib.init import telegram_session_path
from lib.stats import Stats
from apscheduler.schedulers.asyncio import AsyncIOScheduler


class Database:
    def __init__(self):
        self.admins = config.telegram_admins
        self.neural_networks_channel = int(config.telegram_channel.get_secret_value())

        self.asyncio_workers = AsyncioWorkers()
        self.scheduler = AsyncIOScheduler()
        self.params = Params(config.openrouter_api_keys)
        self.stats = Stats()
        self.openrouter = Openrouter(self.params.keys.get_key(), self.asyncio_workers, self.stats)
        self.mistral = Mistral(config.mistral_api_key, self.asyncio_workers, self.stats)
        self.post_assistant = PostAssistant(llm_api=self.mistral, stats=self.stats)
        self.client = TelegramClient(
            telegram_session_path,
            int(config.telegram_api_id.get_secret_value()),
            config.telegram_api_hash.get_secret_value()
        )

    async def shutdown(self):
        await self.asyncio_workers.shutdown()
        await self.client.disconnect()
