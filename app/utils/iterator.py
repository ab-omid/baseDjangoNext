from typing import AsyncIterator, Generic, Optional, TypeVar

T = TypeVar("T")


class AsyncIterWithLength(Generic[T], AsyncIterator[T]):
    def __init__(self, async_iterable: AsyncIterator[tuple[T, int, int, int]]):
        self._iter = async_iterable
        self._len = None
        self._pages = None
        self._page = None

    def __len__(self) -> Optional[int]:
        return self._len

    def pages(self) -> Optional[int]:
        return self._pages

    def page(self) -> Optional[int]:
        return self._page

    def has_next(self) -> bool:
        return self._page is not None and self._pages is not None and self._page < self._pages

    def __aiter__(self) -> AsyncIterator[T]:
        return self

    async def __anext__(self) -> T:
        try:
            element, length, pages, page = await self._iter.__anext__()
            self._len = length
            self._pages = pages
            self._page = page
            return element
        except StopAsyncIteration:
            raise StopAsyncIteration
