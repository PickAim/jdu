from initializers.wildberries_initializer import (
    TestWildberriesDataProviderInitializer,
)
from jdu.providers.wildberries_providers import (
    WildberriesDataProviderWithoutKey,
    WildberriesDataProviderWithoutKeyImpl,
    WildberriesUserMarketDataProviderImpl,
)

AUTH_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9' \
           '.eyJhY2Nlc3NJRCI6IjhiMGZkZWEwLWYxYjgtNDVjOS05NmM5LTdiMmRlNjU2N2Q3ZCJ9' \
           '.6YAvO_GYeXW3em8WZ5cLynTBKcg8x5pmMmoCkgMY6QI'


def create_wb_data_provider_without_key() -> WildberriesDataProviderWithoutKey:
    return WildberriesDataProviderWithoutKeyImpl(TestWildberriesDataProviderInitializer)


def create_wb_data_provider_with_key() -> WildberriesUserMarketDataProviderImpl:
    return WildberriesUserMarketDataProviderImpl(
        AUTH_KEY, TestWildberriesDataProviderInitializer
    )
