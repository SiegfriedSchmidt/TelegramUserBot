from lib.llm import Openrouter, Dialog
from lib.logger import asis_logger
from lib.init import llm_task_content
from telethon.tl.custom.message import Message
import re

from lib.stats import Stats


class Post:
    def __init__(self, message: Message, brief_information='', meet_requirements=''):
        self.message = message
        self.brief_information = brief_information
        self.meet_requirements = meet_requirements
        self.checked_by_assistant = False
        self.successfully_checked = False

    def fill_info(self, brief_information: str, meet_requirements: bool, successfully_checked: bool):
        self.brief_information = brief_information
        self.meet_requirements = meet_requirements
        self.successfully_checked = successfully_checked
        self.checked_by_assistant = True


class PostAssistant:
    def __init__(self, llm_api: Openrouter, stats: Stats):
        self.llm_api = llm_api
        self.previous_posts = []
        self.stats = stats

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

    async def check_channel_message(self, post: Post, stub_check=False, attempts=3):
        asis_logger.info("Start checking new post message...")
        dialog = Dialog()
        dialog.add_user_message(llm_task_content)
        dialog.add_user_message(
            f'''New Post Content: "{post.message.text}"\nPrevious Posts Information: [{self.get_previous_posts_string()}]'''
        )

        async def try_attempts():
            if stub_check:
                asis_logger.info('Stub check enabled, use stub params')
                return True, True, "Summary"

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
                    asis_logger.warning(f"Attempt parse the result string {attempt + 1}/{attempts} failed: {result}")

            asis_logger.error(f"All attempts ({attempts}) to parse the result string have failed!")
            return False, False, ''

        success, meet_requirements, brief_information = await try_attempts()
        self.stats.add_total_posts(1)
        if meet_requirements:
            self.stats.add_chosen_posts(1)

        post.fill_info(brief_information, meet_requirements, success)
