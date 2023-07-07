from jarvis_db.repositores.mappers.market.infrastructure import CategoryTableToJormMapper, NicheTableToJormMapper, \
    WarehouseTableToJormMapper
from jarvis_db.repositores.mappers.market.service import EconomyResultTableToJormMapper, \
    EconomyRequestTableToJormMapper, FrequencyRequestTableToJormMapper
from jarvis_db.repositores.market.infrastructure import CategoryRepository, WarehouseRepository, NicheRepository
from jarvis_db.repositores.market.service import EconomyRequestRepository, EconomyResultRepository, \
    FrequencyRequestRepository, FrequencyResultRepository
from jarvis_db.services.market.infrastructure.category_service import CategoryService
from jarvis_db.services.market.infrastructure.niche_service import NicheService
from jarvis_db.services.market.infrastructure.warehouse_service import WarehouseService
from jarvis_db.services.market.service.economy_service import EconomyService
from jarvis_db.services.market.service.frequency_service import FrequencyService
from sqlalchemy.orm import Session

from jdu.db_tools.fill.wildberries_fillers import WildberriesDBFillerImpl
from tests.providers.wildberries_test_provider import WildBerriesDataProviderWithoutKeyImplTest


def create_economy_service(session: Session) -> EconomyService:
    niche_mapper = NicheTableToJormMapper()
    return EconomyService(
        EconomyRequestRepository(session),
        EconomyResultRepository(session),
        EconomyResultTableToJormMapper(EconomyRequestTableToJormMapper()),
        CategoryService(
            CategoryRepository(session),
            CategoryTableToJormMapper(niche_mapper),
        ),
        NicheService(NicheRepository(session), niche_mapper),
        WarehouseService(WarehouseRepository(session), WarehouseTableToJormMapper()),
    )


def create_frequency_service(session: Session) -> FrequencyService:
    return FrequencyService(
        FrequencyRequestRepository(session),
        NicheRepository(session),
        FrequencyResultRepository(session),
        FrequencyRequestTableToJormMapper(),
    )


def create_wb_db_filler(session: Session) -> WildberriesDBFillerImpl:
    return WildberriesDBFillerImpl(WildBerriesDataProviderWithoutKeyImplTest(), session)
