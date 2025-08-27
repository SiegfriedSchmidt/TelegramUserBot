from abc import ABC, abstractmethod

from openai import RateLimitError
import asyncio
from pydantic import SecretStr

from lib.asyncio_workers import AsyncioWorkers
from lib.llms.dialog import Dialog
from lib.stats import Stats
from lib.logger import llm_logger
from lib.utils.get_exception import get_exception


class LLM(ABC):
    def __init__(self, api_key: SecretStr, workers: AsyncioWorkers, stats: Stats, model: str):
        self.api_key = api_key.get_secret_value()
        self.workers = workers
        self.stats = stats
        self.model = model

    @abstractmethod
    async def _chat_complete(self, dialog: Dialog) -> str:
        ...

    @abstractmethod
    async def check_limits(self) -> str:
        ...

    async def _chat_complete_attempts(self, dialog: Dialog, attempts, timeout) -> str:
        rs = ''
        for attempt in range(attempts):
            try:
                rs = await self._chat_complete(dialog)
            except RateLimitError as e:
                llm_logger.error(f'RATE LIMIT EXCEEDED: {e.message}.')
            except Exception as e:
                llm_logger.warning(f'Attempt get answer {attempt + 1}/{attempts} failed: {get_exception(e)}')
                if attempt != attempts - 1:
                    await asyncio.sleep(timeout)
                continue

            if rs:
                break
            else:
                llm_logger.warning(f'Attempt get answer {attempt + 1}/{attempts} failed: Get empty response.')

        if not rs:
            self.stats.add_failed_row_requests(1)
            llm_logger.error(f'All attempts ({attempts}) have failed!')

        return rs

    async def chat_complete(self, dialog: Dialog, attempts=6, timeout=30):
        result = await self.workers.enqueue_task(self._chat_complete_attempts, dialog, attempts, timeout)
        if result:
            self.stats.add_successful_requests(1)
        return result

    def __str__(self):
        return f'model: {self.model}\napi_key: {self.api_key[0:15]}.....{self.api_key[-5:]}\n'
