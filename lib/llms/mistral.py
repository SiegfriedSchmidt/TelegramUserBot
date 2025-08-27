import asyncio

from mistralai import Mistral as MistralAI
from pydantic import SecretStr

from lib.asyncio_workers import AsyncioWorkers
from lib.llms.abstract import LLM
from lib.llms.dialog import Dialog
from lib.stats import Stats


class Mistral(LLM):
    def __init__(self, api_key: SecretStr, workers: AsyncioWorkers, stats: Stats,
                 model="mistral-small-latest"):
        super().__init__(api_key, workers, stats, model)
        self.client = MistralAI(api_key=api_key.get_secret_value())

    async def _chat_complete(self, dialog: Dialog) -> str:
        completion = self.client.chat.complete(
            model=self.model,
            messages=dialog.messages
        )

        return completion.choices[0].message.content

    async def check_limits(self):
        return "ХЗ"


if __name__ == '__main__':
    from lib.config_reader import config
    from lib.asyncio_workers import AsyncioWorkers
    from lib.post_assistant import PostAssistant, Post


    async def main():
        workers = AsyncioWorkers()
        stats = Stats()
        mistral = Mistral(config.mistral_api_key, workers, stats)
        print(await mistral.check_limits())
        await mistral.workers.start(1)
        #
        # dialog = Dialog()
        # dialog.add_user_message("Hi there!")
        # rs = await mistral.chat_complete(dialog, attempts=1)
        # print(rs)
        # exit()

        post_assistant = PostAssistant(llm_api=mistral, stats=stats)

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
