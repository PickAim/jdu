import json

import aiohttp
import requests
from jorm.market.infrastructure import HandlerType

from jdu.support.constant import COMMISSION_KEY, RETURN_PERCENT_KEY, COMMISSION_WILDBERRIES_JSON


def split_to_chunks(any_list: list[any], chunk_size: int) -> list[any]:
    return list(__divide_chunks(any_list, chunk_size))


def __divide_chunks(any_list: list[any], chunk_size: int):
    for i in range(0, len(any_list), chunk_size):
        yield any_list[i:i + chunk_size]


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


def resolve_wildberries_commission_file(filepath: str) -> None:
    with open(filepath, "r", encoding='cp1251') as file:
        commission_dict: dict = {}
        lines: list[str] = file.readlines()
        for line in lines:
            splitted: list[str] = line.split(";")
            commission_dict[splitted[1]] = {
                COMMISSION_KEY: {
                    HandlerType.MARKETPLACE.value: float(splitted[2]) / 100,
                    HandlerType.PARTIAL_CLIENT.value: float(splitted[3]) / 100,
                    HandlerType.CLIENT.value: float(splitted[4]) / 100
                },
                RETURN_PERCENT_KEY: int(splitted[5].replace("%", ""))
            }
        json_string: str = json.dumps(commission_dict, indent=4, ensure_ascii=False)
        with open(COMMISSION_WILDBERRIES_JSON, "w", encoding='cp1251') as out_file:
            out_file.write(json_string)
