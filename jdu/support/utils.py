from typing import TypeVar, Callable, Iterable

T = TypeVar('T')
V = TypeVar('V')
K = TypeVar('K')


def split_to_batches(any_list: list[any], batch_size: int) -> list[any]:
    return list(__divide_chunks(any_list, batch_size))


def __divide_chunks(any_list: list[any], chunk_size: int):
    for i in range(0, len(any_list), chunk_size):
        yield any_list[i:i + chunk_size]


def map_to_dict(key_generator: Callable[[T], V], value_generator: Callable[[T], K], items: Iterable[T]) -> dict[V, K]:
    return {
        key_generator(item): value_generator(item)
        for item in items
    }
