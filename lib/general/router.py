from lib.database import Database
from typing import List, Callable, Type

from lib.general.filters import FilterType
from lib.general.events import Event
from lib.general.middleware import Middleware


class RouterError(Exception):
    pass


class Handler:
    def __init__(self, callback: Callable, name: str, filter: FilterType = None, middleware: Middleware = None):
        self.callback = callback
        self.filter = filter
        self.name = name
        self.middleware = middleware


class Router:
    def __init__(self, filter: Callable[[], FilterType] = None, middleware: Middleware = None):
        self.handlers: List[Handler] = []
        self.router_filter = filter
        self.router_middleware = middleware

    def __call__(self, filter: FilterType = None, middleware: Middleware = None, override_filter=False):
        def wrapper(callback: Callable):
            handler_filter = filter

            if self.router_filter and not override_filter:
                if handler_filter:
                    handler_filter &= self.router_filter()
                else:
                    handler_filter = self.router_filter()

            handler = Handler(callback, callback.__name__, handler_filter, middleware)
            handler_filter.setup(handler)
            self.handlers.append(handler)
            return callback

        return wrapper

    def get_dispatcher(self, db: Database):
        async def dispatch(event: Event):
            for handler in self.handlers:
                if handler.filter is None or await handler.filter(event):
                    passed, kwargs = True, {}
                    if self.router_middleware:
                        passed, kwargs = await self.router_middleware(event)
                    if handler.middleware:
                        passed2, kwargs2 = await handler.middleware(event)
                        passed = passed and passed2
                        kwargs.update(kwargs2)

                    if passed:
                        await handler.callback(event, db, **kwargs)

                    return

        return dispatch
