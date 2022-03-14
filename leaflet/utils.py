from collections.abc import Sequence

from django.utils.functional import Promise


class ListWithLazyItems(Sequence):
    """
    Mimics a lazy list.

    It keeps items in lazy state and evaluates them when they're
    returned.

    An item is considered lazy when it is
    a `django.utils.functional.Promise` instance.
    """

    def __init__(self, iterable=()):
        if isinstance(iterable, ListWithLazyItems):
            iterable = iterable._list
        self._list = list(iterable)

    def __iter__(self):
        for item in self._list:
            yield item

    def __len__(self):
        return len(self._list)

    def __getitem__(self, index):
        return self._list[index]

    def extend(self, iterable):
        if isinstance(iterable, ListWithLazyItems):
            iterable = iterable._list
        self._list.extend(iterable)

    def __radd__(self, iterable):
        lazy_list = type(self)(iterable)  # copy
        lazy_list.extend(self)
        return lazy_list

    def __add__(self, iterable):
        lazy_list = type(self)(self)  # copy
        lazy_list.extend(iterable)
        return lazy_list

    @classmethod
    def is_lazy_item(cls, item):
        return isinstance(item, Promise)


class ListWithLazyItemsRawIterator(ListWithLazyItems):
    """
    This lazy list yields raw items (i.e. Promises are not resolved)
    when iterated.
    """

    def __iter__(self):
        return iter(self._list)
