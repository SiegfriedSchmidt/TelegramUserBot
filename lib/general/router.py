from lib.database import Database
from typing import List, Callable, Type

from lib.general.filters import FilterType
from lib.general.events import Event
from lib.general.middleware import Middleware


class RouterError(Exception):
    pass


class Handler:
    def __init__(self, callback: Callable, name: str, filter: FilterType = None, middlewares: List[Middleware] = None):
        self.callback = callback
        self.filter = filter
        self.name = name
        self.middlewares = middlewares if middlewares else []


class Router:
    def __init__(self, filter: Callable[[], FilterType] = None, middlewares: List[Middleware] = None):
        self.handlers: List[Handler] = []
        self.router_filter = filter
        self.router_middleware = middlewares if middlewares else []

    def __call__(self, filter: FilterType = None, middlewares: List[Middleware] = None, override_filter=False):
        if middlewares is None:
            middlewares = []

        def wrapper(callback: Callable):
            handler_filter = filter

            if self.router_filter and not override_filter:
                if handler_filter:
                    handler_filter &= self.router_filter()
                else:
                    handler_filter = self.router_filter()

            handler = Handler(callback, callback.__name__, handler_filter, [*self.router_middleware, *middlewares])
            handler_filter.setup(handler)
            self.handlers.append(handler)
            return callback

        return wrapper

    @staticmethod
    async def run_middlewares(handler: Handler, event: Event, db: Database):
        passed, kwargs = True, {}
        for middleware in handler.middlewares:
            cur_passed, cur_kwargs = await middleware(event, db)
            passed = passed and cur_passed
            kwargs.update(cur_kwargs)

            if not passed:
                return False, kwargs

        return True, kwargs

    def get_dispatcher(self, db: Database):
        async def dispatch(event: Event):
            for handler in self.handlers:
                if handler.filter is None or await handler.filter(event, db):
                    passed, kwargs = await self.run_middlewares(handler, event, db)

                    if passed:
                        await handler.callback(event, db, **kwargs)

                    return

        return dispatch
