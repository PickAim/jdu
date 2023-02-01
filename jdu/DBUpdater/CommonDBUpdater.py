from jdu.providers.common import WildBerriesDataProvider


class CommonDBUpdater():
    # maybe it can use wildberries providers
    def __init__(self, api_key: str):
        self.object_provider: WildBerriesDataProvider = WildBerriesDataProvider(api_key)


