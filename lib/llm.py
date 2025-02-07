from openai import AsyncOpenAI
import asyncio
import re
import aiohttp

from lib.asyncio_workers import AsyncioWorkers
from lib.logger import logger
from lib.init import llm_task_content


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


class Openrouter:
    def __init__(self, api_key: str, workers: AsyncioWorkers, model="deepseek/deepseek-r1:free"):
        self.api_key = api_key
        self.workers = workers
        self.model = model
        self.client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
        )
        self.total_requests = 0
        self.successful_requests = 0

    async def __chat_complete(self, dialog: Dialog) -> str:
        completion = await self.client.chat.completions.create(
            model="deepseek/deepseek-r1:free",
            messages=dialog.messages
        )

        return completion.choices[0].message.content

    async def __chat_complete_attempts(self, dialog: Dialog, attempts, timeout) -> str:
        rs = ''
        for attempt in range(attempts):
            self.total_requests += 1
            try:
                rs = await self.__chat_complete(dialog)
            except Exception as e:
                logger.warning(f'Attempt get answer {attempt + 1}/{attempts} failed: {e}')
                if attempt != attempts - 1:
                    await asyncio.sleep(timeout)

            if rs:
                break

        if not rs:
            logger.error(f'All attempts ({attempts}) have failed!')
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
            self.successful_requests += 1
        return result


class PostAssistant:
    def __init__(self, llm_api: Openrouter):
        self.llm_api = llm_api
        self.previous_posts = []

    @staticmethod
    def parse_result(result: str) -> (bool, bool, str):
        bool_match = re.search(r'Meet\s+the\s+requirements:\s*"?\s*(True|False)\s*"?', result, re.IGNORECASE)
        brief_match = re.search(r'Brief\s+information:\s*"(.*?)"', result, re.IGNORECASE | re.DOTALL)
        if bool_match and brief_match:
            meet_requirements = bool_match.group(1).strip().lower() == "true"
            brief_information = brief_match.group(1).strip()

            return True, meet_requirements, brief_information
        else:
            return False, False, result

    def get_previous_posts_string(self):
        return ", ".join(map(lambda x: f'"{x}"', self.previous_posts))

    async def check_channel_message(self, post_message: str, attempts=3) -> (bool, bool, str):
        logger.info("Start checking new post message...")
        dialog = Dialog()
        dialog.add_user_message(llm_task_content)
        dialog.add_user_message(
            f'''New Post Content: "{post_message}"\nPrevious Posts Information: [{self.get_previous_posts_string()}]'''
        )

        print(dialog.messages)

        for attempt in range(attempts):
            result = await self.llm_api.chat_complete(dialog)

            if not result:
                return False, False, ''

            success, meet_requirements, brief_information = self.parse_result(result)
            if success:
                if meet_requirements:
                    self.previous_posts.append(brief_information)
                return True, meet_requirements, brief_information
            else:
                logger.warning(f"Attempt parse the result string {attempt + 1}/{attempts} failed: {result}")

        logger.error(f"All attempts ({attempts}) to parse the result string ave failed!")
        return False, False, ''


if __name__ == '__main__':
    from config_reader import config
    from asyncio_workers import AsyncioWorkers


    async def main():
        workers = AsyncioWorkers()
        openrouter = Openrouter(config.openrouter_api_key.get_secret_value(), workers)
        print(await openrouter.check_limits())
        post_assistant = PostAssistant(llm_api=openrouter)
        await openrouter.workers.start(1)
        await post_assistant.check_channel_message(
            '''Создаём любой логотип: вышел удобный БЕСПЛАТНЫЙ генератор лого AppyPie.

    • Пишем нужный промпт
    • Выбираем стиль и качество (стандарт/высокое)
    • Скачиваем ГОТОВОЕ лого в нужном формате

    Фрилансеры уже потирают ручки ''',
        )


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
