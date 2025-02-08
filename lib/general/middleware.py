import abc
from typing import Dict, Any, List, Tuple
from lib.general.events import Event


class Middleware(abc.ABC):
    @abc.abstractmethod
    async def __call__(self, event: Event) -> Tuple[bool, Dict[str, Any]]:
        pass


class CommandMiddleware(Middleware):
    async def __call__(self, event: Event) -> Tuple[bool, Dict[str, Any]]:
        text = event.message.text
        space_pos = text.find(' ')
        if space_pos == -1 or space_pos == len(text) - 1:
            return True, {'arg': ''}

        return True, {'arg': text[space_pos + 1:]}


class AccessMiddleware(Middleware):
    def __init__(self, usernames: List[str] = None):
        self.usernames = usernames

    async def __call__(self, event: Event) -> Tuple[bool, Dict[str, Any]]:
        username = (await event.get_chat()).username
        if self.usernames and username not in self.usernames:
            await event.respond('Не достоин')
            return False, {}
        return True, {}
