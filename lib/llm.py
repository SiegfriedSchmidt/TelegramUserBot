from openai import AsyncOpenAI
import asyncio
import aiohttp

from lib.asyncio_workers import AsyncioWorkers
from lib.stats import Stats
from lib.logger import llm_logger
from lib.utils.get_exception import get_exception


class Dialog:
    def __init__(self):
        self.messages = []

    def add_user_message(self, message):
        self.messages.append({
            "role": "user",
            "content": message
        })

    def add_assistant_message(self, message):
        self.messages.append({
            "role": "assistant",
            "content": message
        })

    def pop_message(self):
        self.messages.pop()

    def __str__(self):
        str_dialog = ''
        for message in self.messages:
            str_dialog += f'---{message["role"]}---: {message["content"]}\n'
        return str_dialog


class Openrouter:
    def __init__(self, api_key: str, workers: AsyncioWorkers, stats: Stats, model="deepseek/deepseek-r1:free"):
        self.api_key = api_key
        self.workers = workers
        self.stats = stats
        self.model = model
        self.client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
        )

    async def __chat_complete(self, dialog: Dialog) -> str:
        self.stats.add_total_requests(1)
        completion = await self.client.chat.completions.create(
            model="deepseek/deepseek-r1:free",
            messages=dialog.messages
        )

        return completion.choices[0].message.content

    async def __chat_complete_attempts(self, dialog: Dialog, attempts, timeout) -> str:
        rs = ''
        for attempt in range(attempts):
            try:
                rs = await self.__chat_complete(dialog)
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

    async def check_limits(self):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }

        async with aiohttp.ClientSession() as session:
            async with session.get('https://openrouter.ai/api/v1/auth/key', headers=headers) as resp:
                if resp.status == 200:
                    return await resp.text()
                else:
                    return "Error"

    async def chat_complete(self, dialog: Dialog, attempts=6, timeout=30):
        result = await self.workers.enqueue_task(self.__chat_complete_attempts, dialog, attempts, timeout)
        if result:
            self.stats.add_successful_requests(1)
        return result


if __name__ == '__main__':
    from config_reader import config
    from asyncio_workers import AsyncioWorkers
    from lib.post_assistant import PostAssistant, Post


    async def main():
        workers = AsyncioWorkers()
        stats = Stats()
        openrouter = Openrouter(config.openrouter_api_key.get_secret_value(), workers, stats)
        print(await openrouter.check_limits())
        post_assistant = PostAssistant(llm_api=openrouter)
        await openrouter.workers.start(1)


    #     post = Post('''Создаём любой логотип: вышел удобный БЕСПЛАТНЫЙ генератор лого AppyPie.
    #
    # • Пишем нужный промпт
    # • Выбираем стиль и качество (стандарт/высокое)
    # • Скачиваем ГОТОВОЕ лого в нужном формате
    #
    # Фрилансеры уже потирают ручки ''')
    #     await post_assistant.check_channel_message(post)

    #     print(llm_task_content)
    #
    #     await asyncio.gather(*[post_assistant.check_channel_message(
    #         '''Создаём любой логотип: вышел удобный БЕСПЛАТНЫЙ генератор лого AppyPie.
    #
    # • Пишем нужный промпт
    # • Выбираем стиль и качество (стандарт/высокое)
    # • Скачиваем ГОТОВОЕ лого в нужном формате
    #
    # Фрилансеры уже потирают ручки ''',
    #     ), post_assistant.check_channel_message(
    #         '''Создаём любой логотип: вышел удобный БЕСПЛАТНЫЙ генератор лого AppyPie.
    #
    # • Пишем нужный промпт
    # • Выбираем стиль и качество (стандарт/высокое)
    # • Скачиваем ГОТОВОЕ лого в нужном формате
    #
    # Фрилансеры уже потирают ручки ''',
    #     )])
    #     await asyncio_workers.shutdown()

    asyncio.run(main())
