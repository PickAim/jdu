from abc import ABC

import requests
from aiohttp import ClientSession
from requests import Session
from requests.adapters import HTTPAdapter

from jdu.support.commission.commision_resolver import CommissionResolver
from jdu.support.utils import get_request_json, get_async_request_json


class DataProvider(ABC):
    THREAD_TASK_COUNT = 100

    def __init__(self):
        self.session: Session | None = None
        self.commission_resolver: CommissionResolver | None = None
        self.marketplace_name: str = ""

    def reset_session(self):
        self.session.close()
        self.session = requests.Session()
        __adapter = HTTPAdapter(pool_connections=100, pool_maxsize=100)
        self.session.mount('https://', __adapter)
        self.session.mount('http://', __adapter)

    def get_request_json(self, url: str):
        return get_request_json(url, self.session)

    @staticmethod
    async def get_async_request_json(url: str, client_session: ClientSession):
        return await get_async_request_json(url, client_session)

    def get_exchange_rate(self, currency: str):
        url: str = 'https://www.cbr-xml-daily.ru/daily_json.js'
        json_data = self.get_request_json(url)
        return json_data['Valute'][currency]

    def __del__(self):
        self.session.close()
