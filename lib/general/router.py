from telethon import TelegramClient
from lib.database import Database
from typing import List, Callable, Type

from lib.general.filters import FilterType
from lib.general.events import Event


class RouterError(Exception):
    pass


class Handler:
    def __init__(self, callback: Callable, event, name, filter: FilterType = None):
        self.callback = callback
        self.event = event
        self.filter = filter
        self.name = name


class Router:
    def __init__(self, event: Callable[[], Event] = None, filter: Callable[[], FilterType] = None):
        self.handlers: List[Handler] = []
        self.router_event = event
        self.router_filter = filter

    def __call__(self, event: Event = None, filter: FilterType = None, override_event=False, override_filter=False):
        def wrapper(callback: Callable):
            handler_event = event
            handler_filter = filter

            if self.router_event and not override_event:
                if handler_event:
                    raise RouterError('Event placed on router and handler at the same time!')
                handler_event = self.router_event()
            else:
                if handler_event is None:
                    raise RouterError('No event specified!')

            if self.router_filter and not override_filter:
                if handler_filter:
                    handler_filter &= self.router_filter()
                else:
                    handler_filter = self.router_filter()

            handler = Handler(callback, handler_event, callback.__name__, handler_filter)
            handler_filter.setup(handler)
            self.handlers.append(handler)
            return callback

        return wrapper

    def register_router(self, client: TelegramClient, db: Database):
        for handler in self.handlers:
            async def wrapped(event, current_handler=handler):
                if (current_handler.filter is not None) and not current_handler.filter(event):
                    return

                await current_handler.callback(event, db)

            client.add_event_handler(wrapped, handler.event)
