from typing import TypeAlias, List
from lib.general.events import Event
import abc

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
    async def __call__(self, event: Event) -> bool:
        pass


class Any(Combinable):
    def __init__(self, *filters: FilterType):
        self.filters = filters

    def setup(self, handler: Handler) -> None:
        for filter in self.filters:
            filter.setup(handler)

    async def __call__(self, event: Event) -> bool:
        for filter in self.filters:
            if await filter(event):
                return True


class All(Any):
    async def __call__(self, event: Event) -> bool:
        for filter in self.filters:
            if not await filter(event):
                return False

        return True


class Not(Combinable):
    def __init__(self, filter: FilterType):
        self.filter = filter

    def setup(self, handler: Handler) -> None:
        self.filter.setup(handler)

    async def __call__(self, event: Event) -> bool:
        return not await self.filter(event)


class Chat(Combinable):
    async def __call__(self, event: Event) -> bool:
        return event.is_private


class Channel(Combinable):
    async def __call__(self, event: Event) -> bool:
        chat = await event.get_chat()
        print(chat)
        return event.is_channel


class Group(Combinable):
    async def __call__(self, event: Event) -> bool:
        return event.is_group


class Command(Combinable):
    def __init__(self, cmd: str = ''):
        self.cmd = cmd

    def setup(self, handler: Handler) -> None:
        if self.cmd:
            self.cmd = self.cmd if self.cmd.startswith('/') else f'/{self.cmd}'
        else:
            self.cmd = f'/{handler.name}'

    async def __call__(self, event: Event) -> bool:
        text = event.message.text
        if self.cmd == '/':
            return text.startswith(self.cmd)
        space_pos = text.find(' ')
        if space_pos == -1:
            return text == self.cmd
        return text[:space_pos] == self.cmd
