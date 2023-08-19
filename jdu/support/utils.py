import json
from typing import TypeVar, Callable, Iterable

import aiohttp
import requests

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


async def get_async_request_json(url: str, session: aiohttp.ClientSession):
    async with session.get(url=url) as request:
        if request.status == 200:
            data = await request.read()
            if len(data) > 0:
                return json.loads(data)
        return ""


def get_request_json(url: str, session: requests.Session, headers=None):
    if headers is None:
        headers = {}
    with session.get(url, headers=headers) as request:
        if request.status_code == 200:
            request.raise_for_status()
            return request.json()
        return ""
