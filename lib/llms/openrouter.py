from openai import AsyncOpenAI
import asyncio
import aiohttp
from pydantic import SecretStr

from lib.asyncio_workers import AsyncioWorkers
from lib.llms.abstract import LLM
from lib.llms.dialog import Dialog
from lib.stats import Stats


# deepseek/deepseek-r1:free
# openrouter/cypher-alpha:free
# deepseek/deepseek-r1-0528:free
class Openrouter(LLM):
    def __init__(self, api_key: SecretStr, workers: AsyncioWorkers, stats: Stats,
                 model="deepseek/deepseek-r1-0528:free"):
        super().__init__(api_key, workers, stats, model)
        self.client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
        )

    async def _chat_complete(self, dialog: Dialog) -> str:
        self.stats.add_total_requests(1)
        completion = await self.client.chat.completions.create(
            model=self.model,
            messages=dialog.messages
        )

        return completion.choices[0].message.content

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


if __name__ == '__main__':
    from lib.config_reader import config
    from lib.asyncio_workers import AsyncioWorkers
    from lib.post_assistant import PostAssistant, Post


    async def main():
        workers = AsyncioWorkers()
        stats = Stats()
        openrouter = Openrouter(config.openrouter_api_keys[0], workers, stats)
        print(await openrouter.check_limits())
        post_assistant = PostAssistant(llm_api=openrouter, stats=stats)
        await openrouter.workers.start(1)

        class StubMessage:
            def __init__(self, text):
                self.text = text

        message = StubMessage('''Создаём любой логотип: вышел удобный БЕСПЛАТНЫЙ генератор лого AppyPie.

    • Пишем нужный промпт
    • Выбираем стиль и качество (стандарт/высокое)
    • Скачиваем ГОТОВОЕ лого в нужном формате

    Фрилансеры уже потирают ручки ''')
        post = Post(message)
        await post_assistant.check_channel_message(post)
        print('-----')
        print(post.successfully_checked)
        print('-----')
        print(post.checked_by_assistant)
        print('-----')
        print(post.meet_requirements)
        print('-----')
        print(post.brief_information)
        print('-----')


    asyncio.run(main())

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

    # asyncio.run(main())
    ...
