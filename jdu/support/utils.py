import re
from typing import Any, TypeVar, Callable, Iterable

T = TypeVar("T")
V = TypeVar("V")
K = TypeVar("K")


def split_to_batches(any_list: list[Any], batch_size: int) -> list[Any]:
    return list(__divide_chunks(any_list, batch_size))


def __divide_chunks(any_list: list[Any], chunk_size: int):
    for i in range(0, len(any_list), chunk_size):
        yield any_list[i: i + chunk_size]


def map_to_dict(
        key_generator: Callable[[T], V],
        value_generator: Callable[[T], K],
        items: Iterable[T],
) -> dict[V, K]:
    return {key_generator(item): value_generator(item) for item in items}


def parsing_attribute_address(address: str) -> dict[str, str]:
    attributes_address: dict[str, str] = {}
    pattern = re.compile(r'(Респ\.[А-Яа-я\-\s]+)|([А-Яа-я\-\s]+(обл\.|область|край))', re.I)
    region = pattern.search(address)
    if not region:
        pattern = re.compile(r',\s+[А-Яа-я]+', re.I)
        region = pattern.search(address)
    pattern = re.compile(r'[А-Яа-я.]+(\.)?\s*[а-яА-Я0-9\-\d\s]+(\.)?(,\s*[\dа-яА-Я\s/.]+)?', re.I)
    street = pattern.search(address)
    if not street:
        pattern = re.compile(r'[А-Яа-я]+ улица,\s*[\dа-яА-Я/]+', re.I)
        street = pattern.search(address)
    attributes_address['region'] = region.group().lstrip(' ').replace(', ', '')
    attributes_address['street'] = street.group().lstrip(' ')
    return attributes_address
