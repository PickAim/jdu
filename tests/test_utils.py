from jdu.providers.wildberries_providers import (
    WildberriesDataProviderWithoutKey,
    WildberriesDataProviderWithoutKeyImpl,
    WildberriesUserMarketDataProviderImpl,
)
from tests.basic_db_test import AUTH_KEY
from tests.initializers.wildberries_initializer import (
    TestWildberriesDataProviderInitializer,
)
from tests.providers.wildberries_test_provider import (
    TestWildberriesDataProviderWithoutKeyImpl,
)


def create_wb_real_data_provider_without_key() -> WildberriesDataProviderWithoutKey:
    return WildberriesDataProviderWithoutKeyImpl(TestWildberriesDataProviderInitializer)


def create_test_wb_data_provider_without_key() -> WildberriesDataProviderWithoutKey:
    return TestWildberriesDataProviderWithoutKeyImpl(
        TestWildberriesDataProviderInitializer
    )


def create_real_wb_data_provider_with_key() -> WildberriesUserMarketDataProviderImpl:
    return WildberriesUserMarketDataProviderImpl(
        AUTH_KEY, TestWildberriesDataProviderInitializer
    )
