from telethon import TelegramClient
from lib.database import Database
from typing import List, Callable

from lib.general.filters import FilterType, Event


class Handler:
    def __init__(self, callback: Callable, event, name, filter: FilterType = None):
        self.callback = callback
        self.event = event
        self.filter = filter
        self.name = name


class Router:
    def __init__(self):
        self.handlers: List[Handler] = []

    def __call__(self, event: Event, filter: FilterType = None):
        def wrapper(callback: Callable):
            self.handlers.append(Handler(callback, event, callback.__name__, filter))
            return callback

        return wrapper

    def register_router(self, client: TelegramClient, db: Database):
        for handler in self.handlers:
            async def wrapped(event, current_handler=handler):
                if (current_handler.filter is not None) and not current_handler.filter(event):
                    return

                await current_handler.callback(event, db)

            client.add_event_handler(wrapped, handler.event)
