import json

import aiohttp
import requests


def split_to_chunks(any_list: list[any], chunk_size: int) -> list[any]:
    return list(__divide_chunks(any_list, chunk_size))


def __divide_chunks(any_list: list[any], chunk_size: int):
    for i in range(0, len(any_list), chunk_size):
        yield any_list[i:i + chunk_size]


async def get_async_request_json(url: str, session: aiohttp.ClientSession):
    async with session.get(url=url) as request:
        request.raise_for_status()
        data = await request.read()
        if len(data) > 0:
            return json.loads(data)
        return ""


def get_request_json(url: str, session: requests.Session, headers=None):
    if headers is None:
        headers = {}
    with session.get(url, headers=headers) as request:
        request.raise_for_status()
        return request.json()
