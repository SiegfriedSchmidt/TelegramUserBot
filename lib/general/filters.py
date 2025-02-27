from typing import TypeAlias, List

from lib.database import Database
from lib.general.events import Event
import abc

from lib.logger import main_logger

# avoid circular import
FilterType: TypeAlias = "Combinable"

from lib.general.router import Handler


class Combinable(abc.ABC):
    """
    Subclass that enables filters to be combined.

    * The :func:`bitwise or <operator.or_>` operator ``|`` can be used to combine filters with :class:`Any`.
    * The :func:`bitwise and <operator.and_>` operator ``&`` can be used to combine filters with :class:`All`.
    * The :func:`bitwise invert <operator.invert>` operator ``~`` can be used to negate a filter with :class:`Not`.

    Filters combined this way will be merged.
    This means multiple ``|`` or ``&`` will lead to a single :class:`Any` or :class:`All` being used.
    Multiple ``~`` will toggle between using :class:`Not` and not using it.
    """

    def __or__(self, other: FilterType) -> "Any":
        lhs = self.filters if isinstance(self, Any) else (self,)
        rhs = other.filters if isinstance(other, Any) else (other,)
        return Any(*lhs, *rhs)

    def __and__(self, other: FilterType) -> "All":
        lhs = self.filters if isinstance(self, All) else (self,)
        rhs = other.filters if isinstance(other, All) else (other,)
        return All(*lhs, *rhs)

    def __invert__(self) -> "Not | FilterType":
        return self.filter if isinstance(self, Not) else Not(self)

    def setup(self, handler: Handler) -> None:
        pass

    @abc.abstractmethod
    async def __call__(self, event: Event, db: Database) -> bool:
        pass


class Any(Combinable):
    def __init__(self, *filters: FilterType):
        self.filters = filters

    def setup(self, handler: Handler) -> None:
        for filter in self.filters:
            filter.setup(handler)

    async def __call__(self, event: Event, db: Database) -> bool:
        for filter in self.filters:
            if await filter(event, db):
                return True


class All(Any):
    async def __call__(self, event: Event, db: Database) -> bool:
        for filter in self.filters:
            if not await filter(event, db):
                return False

        return True


class Not(Combinable):
    def __init__(self, filter: FilterType):
        self.filter = filter

    def setup(self, handler: Handler) -> None:
        self.filter.setup(handler)

    async def __call__(self, event: Event, db: Database) -> bool:
        return not await self.filter(event, db)


class Chat(Combinable):
    async def __call__(self, event: Event, db: Database) -> bool:
        return event.is_private


class Channel(Combinable):
    def __init__(self, exclude_networks_channel=True):
        self.exclude_networks_channel = exclude_networks_channel

    async def __call__(self, event: Event, db: Database) -> bool:
        if not event.is_channel:
            return False

        if self.exclude_networks_channel and (await event.get_chat()).id == db.neural_networks_channel:
            main_logger.info("Skip networks channel post.")
            return False

        return event.is_channel


class Group(Combinable):
    async def __call__(self, event: Event, db: Database) -> bool:
        return event.is_group


class Command(Combinable):
    def __init__(self, cmd: str = ''):
        self.cmd = cmd

    def setup(self, handler: Handler) -> None:
        if self.cmd:
            self.cmd = self.cmd if self.cmd.startswith('/') else f'/{self.cmd}'
        else:
            self.cmd = f'/{handler.name}'

    async def __call__(self, event: Event, db: Database) -> bool:
        text = event.message.text
        if self.cmd == '/':
            return text.startswith(self.cmd)
        space_pos = text.find(' ')
        if space_pos == -1:
            return text == self.cmd
        return text[:space_pos] == self.cmd
