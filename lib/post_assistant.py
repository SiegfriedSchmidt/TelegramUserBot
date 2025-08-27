from typing import Tuple, Optional, List

from lib.llm import Openrouter, Dialog
from lib.logger import asis_logger
from lib.init import llm_post_task_content
from telethon.tl.custom.message import Message
import re

from lib.stats import Stats


class Post:
    def __init__(self, message: Message, meet_requirements='', brief_information='', reason=''):
        self.message = message
        self.meet_requirements = meet_requirements
        self.brief_information = brief_information
        self.reason = reason
        self.checked_by_assistant = False
        self.successfully_checked = False

    def fill_info(self, meet_requirements: bool, brief_information: str, reason: str, successfully_checked: bool):
        self.meet_requirements = meet_requirements
        self.brief_information = brief_information
        self.reason = reason
        self.successfully_checked = successfully_checked
        self.checked_by_assistant = True


class PostAssistant:
    def __init__(self, llm_api: Openrouter, stats: Stats):
        self.llm_api = llm_api
        self.previous_posts: List[Post] = []
        self.stats = stats

    @staticmethod
    def parse_result(result: str) -> Optional[Tuple[bool, str, str]]:
        bool_match = re.search(
            r'Meet\s+the\s+requirements:\s*"?\s*(True|False)\s*"?',
            result,
            re.IGNORECASE
        )

        brief_match = re.search(
            r'Brief\s+information:\s*(.*?)\s*(?=Reason:)',
            result,
            re.IGNORECASE | re.DOTALL
        )

        reason_match = re.search(
            r'Reason:\s*(.*?)(?=\n(?:Meet\s+the\s+requirements:|Brief\s+information:|Reason:)|$)',
            result,
            re.IGNORECASE | re.DOTALL
        )

        if bool_match and brief_match:
            meet_requirements = bool_match.group(1).strip().lower() == "true"
            brief_information = brief_match.group(1).strip()
            reason_text = reason_match.group(1).strip() if reason_match else ""

            return meet_requirements, brief_information, reason_text
        else:
            return None

    def get_previous_posts_string(self):
        return ", ".join(map(lambda x: f'"{x}"', self.previous_posts))

    async def check_channel_message(self, post: Post, stub_check=False, attempts=3):
        asis_logger.info("Start checking new post message...")
        dialog = Dialog()
        dialog.add_user_message(llm_post_task_content)
        dialog.add_user_message(
            f'''New Post Content: "{post.message.text}"\nPrevious Posts Information: [{self.get_previous_posts_string()}]'''
        )

        async def try_attempts() -> Optional[Tuple[bool, str, str]]:
            if stub_check:
                asis_logger.info('Stub check enabled, use stub params')
                return True, "Summary", "Reason"

            for attempt in range(attempts):
                result = await self.llm_api.chat_complete(dialog)

                if not result:
                    return None

                parsed_result = self.parse_result(result)
                if parsed_result:
                    return parsed_result
                else:
                    asis_logger.warning(
                        f"Attempt parse the result string {attempt + 1}/{attempts} failed. Not parsed: '{result}'"
                    )

            asis_logger.error(f"All attempts ({attempts}) to parse the result string have failed!")
            return None

        rs = await try_attempts()
        self.stats.add_total_posts(1)
        if rs:
            meet_requirements, brief_information, reason = rs
            if meet_requirements:
                self.stats.add_chosen_posts(1)

            post.fill_info(meet_requirements, brief_information, reason, True)


if __name__ == '__main__':
    result = PostAssistant.parse_result('''
    Meet the requirements: False
Brief information: Advertisement for the TV show "Баранкины и камни силы" (16+) and a promotional feature for drivers in Yandex Go.
Reason: **Reasoning:**
1.  **Topic:** The post focuses on promoting a TV show (Баранкины и камни силы) and a feature within the Yandex Go app for complimenting drivers. There is **no mention of neural networks or AI**, failing Requirement 1.
2.  **NSFW:** The "16+" designation explicitly flags potential restricted content, violating Requirement 2.
3.  **Political Content:** None detected - Pass.
4.  **Duplicate Content:** Previous posts are empty - Pass.
5.  **Advertisement:** The **entire post** serves as an advertisement for the TV show (providing links) and promotes using the new "superpower" feature in Yandex Go. This violates Requirement 5 which allows ads *within* posts but prohibits posts that *are* ads.
    ''')
    print(*result, sep='\n')
