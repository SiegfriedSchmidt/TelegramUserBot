from openai import AsyncOpenAI
from config_reader import config
from logger import logger
import asyncio


class Openrouter:
    def __init__(self, model="deepseek/deepseek-r1:free"):
        self.client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=config.openrouter_api_key.get_secret_value(),
        )
        self.model = model

    async def __get_answer(self, question: str):
        completion = await self.client.chat.completions.create(
            model="deepseek/deepseek-r1:free",
            messages=[
                {
                    "role": "user",
                    "content": question
                }
            ],
        )

        return completion.choices[0].message.content

    async def get_answer(self, question: str, attempts=5):
        rs = ''
        for attempt in range(attempts):
            try:
                rs = await self.__get_answer(question)
            except Exception as e:
                logger.warning(f'Attempt get answer {attempt + 1}/{attempts} failed: {e}')

            if rs:
                break

        if not rs:
            logger.error(f'All attempts ({attempts}) have failed!')
        return rs


async def main():
    openrouter = Openrouter()
    print(await openrouter.get_answer("Who are you?"))


if __name__ == '__main__':
    asyncio.run(main())
