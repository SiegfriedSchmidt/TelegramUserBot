from telethon import events, TelegramClient
from telethon.events.filters import All
from lib.database import Database
from typing import List, Callable


class Handler:
    def __init__(self, callback: Callable, event, name: str):
        self.callback = callback
        self.event = event
        self.name = name


class Router:
    def __init__(self):
        self.handlers: List[Handler] = []

    def __call__(self, event: events.NewMessage, filter: events.filters.All):
        def wrapper(callback: Callable):
            self.handlers.append(Handler(callback, event, callback.__name__))
            return callback

        return wrapper

    def register_router(self, client: TelegramClient, db: Database):
        for handler in self.handlers:
            async def wrapped(event: events.NewMessage):
                await handler.callback(event, db)

            client.on(handler.event)(wrapped)
