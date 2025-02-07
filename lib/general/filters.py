from telethon import events
from typing import TypeAlias, Callable
import abc

Event: TypeAlias = "events.NewMessage"
FilterType: TypeAlias = "Callable[[Event], bool] | Combinable"


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

    @abc.abstractmethod
    def __call__(self, event: Event) -> bool:
        pass


class Any(Combinable):
    def __init__(self, *filters: FilterType):
        self.filters = filters

    def __call__(self, event: Event) -> bool:
        for filter in self.filters:
            if filter(event):
                return True


class All(Combinable):
    def __init__(self, *filters: FilterType):
        self.filters = filters

    def __call__(self, event: Event) -> bool:
        for filter in self.filters:
            if not filter(event):
                return False

        return True


class Not(Combinable):
    def __init__(self, filter: FilterType):
        self.filter = filter

    def __call__(self, event: Event) -> bool:
        return not self.filter(event)


class Chat(Combinable):
    def __init__(self):
        super().__init__()

    def __call__(self, event: Event) -> bool:
        return event.is_private


class Channel(Combinable):
    def __init__(self):
        super().__init__()

    def __call__(self, event: Event) -> bool:
        return event.is_channel


class Group(Combinable):
    def __init__(self):
        super().__init__()

    def __call__(self, event: Event) -> bool:
        return event.is_group


class Command(Combinable):
    def __init__(self, cmd):
        self.cmd = cmd
        super().__init__()

    def __call__(self, event: Event) -> bool:
        return event.message.text.startswith(f'/{self.cmd}')
