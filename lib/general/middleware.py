import abc
from typing import Dict, Any, List, Tuple

from lib.database import Database
from lib.general.events import Event
from lib.logger import main_logger


class Middleware(abc.ABC):
    @abc.abstractmethod
    async def __call__(self, event: Event, db: Database) -> Tuple[bool, Dict[str, Any]]:
        pass


class CommandMiddleware(Middleware):
    async def __call__(self, event: Event, db: Database) -> Tuple[bool, Dict[str, Any]]:
        text = event.message.text
        space_pos = text.find(' ')
        if space_pos == -1 or space_pos == len(text) - 1:
            return True, {'arg': ''}

        return True, {'arg': text[space_pos + 1:]}


class AccessMiddleware(Middleware):
    def __init__(self, usernames: List[str] = None, add_admins=True):
        self.usernames = usernames if usernames else []

    async def __call__(self, event: Event, db: Database) -> Tuple[bool, Dict[str, Any]]:
        username = (await event.get_chat()).username
        if username not in [*self.usernames, *db.admins]:
            main_logger.warning(f"From user '{username}' message '{event.message.text}'")
            await event.respond('Nicht würdig')
            return False, {}
        return True, {}
