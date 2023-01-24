from jarvis_db.repositores.market.infrastructure import NicheRepository
from jdu.request.downloading.wildberries import SyncWildBerriesDataProvider


class WildberriesDBUpdater():
    # maybe it can use wildberries providers
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.object_provider = SyncWildBerriesDataProvider(self.api_key)


