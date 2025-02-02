from openai import AsyncOpenAI
from lib.config_reader import config
from lib.logger import logger
from typing import List
import asyncio
import re

task_content = \
    '''
    Task:
    You are an assistant that evaluates Telegram posts to determine if they meet specific requirements.
    
    Inputs:
    New Post Content: The full text of the new post to be evaluated.
    Previous Posts Information: A brief summary or list of previous posts' key points. (This may be an empty list, e.g., [].)
    Requirements for the New Post:
    
    Content Requirement: The post must include interesting information about neural networks.
    NSFW Requirement: The post must not contain any NSFW (Not Safe For Work) content.
    Originality Requirement: The post must not include information that has already been covered in the previous posts.
    Output Instructions:
    Your response must include the following two pieces of information:
    
    Meet the requirements: A Boolean value ("True" or "False") indicating whether the new post meets all the requirements.
    Brief information: A concise summary or extraction of the key information in the new post that can help identify if similar content appears in future posts.
    Output Format:
    Meet the requirements: "True/False"
    Brief information: "brief info about post"
    '''

test_previous_posts = [
    "Интересные факты о развитии нейронных сетей и их применение в медицине",
    "Анализ современных алгоритмов глубокого обучения"
]


def parse_result(result: str) -> (bool, bool, str):
    bool_match = re.search(r'Meet\s+the\s+requirements:\s*"?\s*(True|False)\s*"?', result, re.IGNORECASE)
    brief_match = re.search(r'Brief\s+information:\s*"(.*?)"', result, re.IGNORECASE | re.DOTALL)
    if bool_match and brief_match:
        meet_requirements = bool_match.group(1).strip().lower() == "true"
        brief_information = brief_match.group(1).strip()

        return True, meet_requirements, brief_information
    else:
        return False, False, result


class Openrouter:
    def __init__(self, model="deepseek/deepseek-r1:free"):
        self.client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=config.openrouter_api_key.get_secret_value(),
        )
        self.model = model
        self.previous_posts = []

    async def __chat_complete(self, messages: List):
        completion = await self.client.chat.completions.create(
            model="deepseek/deepseek-r1:free",
            messages=messages
        )

        return completion.choices[0].message.content

    async def chat_complete(self, messages: List, attempts=6, timeout=30) -> '':
        rs = ''
        for attempt in range(attempts):
            try:
                rs = await self.__chat_complete(messages)
            except Exception as e:
                logger.warning(f'Attempt get answer {attempt + 1}/{attempts} failed: {e}')
                await asyncio.sleep(timeout)

            if rs:
                break

        if not rs:
            logger.error(f'All attempts ({attempts}) have failed!')
        return rs

    async def check_channel_message(self, post_message: str, attempts=3) -> (bool, bool, str):
        logger.info("Start checking new post message...")
        messages = [
            {
                "role": "user",
                "content": task_content
            }, {
                "role": "user",
                "content": f'''New Post Content: "{post_message}"\nPrevious Posts Information: [{", ".join(map(lambda x: f'"{x}"', self.previous_posts))}]'''
            }
        ]

        for attempt in range(attempts):
            result = await self.chat_complete(messages)

            if not result:
                return False, False, ''

            success, meet_requirements, brief_information = parse_result(result)
            if success:
                if meet_requirements:
                    self.previous_posts.append(brief_information)
                return True, meet_requirements, brief_information
            else:
                logger.warning(f"Attempt parse the result string {attempt + 1}/{attempts} failed: {result}")

        logger.error(f"All attempts ({attempts}) to parse the result string ave failed!")
        return False, False, ''


async def main():
    openrouter = Openrouter()
    print(await openrouter.check_channel_message(
        'В этом посте представляем обзор последних новостей из мира технологий. Мы рассмотрим различные инновации в IT-сфере, включая последние тренды в разработке программного обеспечения.',
    ))


if __name__ == '__main__':
    asyncio.run(main())
