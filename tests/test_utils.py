from jarvis_db.repositores.mappers.market.service import FrequencyRequestTableToJormMapper
from jarvis_db.repositores.market.infrastructure import NicheRepository
from jarvis_db.repositores.market.service import FrequencyRequestRepository, FrequencyResultRepository
from jarvis_db.services.market.service.frequency_service import FrequencyService
from sqlalchemy.orm import Session

from jdu.db_tools.fill.wildberries_fillers import WildberriesDBFillerImpl
from tests.initializers.wildberries_initializer import WildberriesTestDBFillerInitializer
from tests.providers.wildberries_test_provider import WildBerriesDataProviderWithoutKeyImplTest


def create_frequency_service(session: Session) -> FrequencyService:
    return FrequencyService(
        FrequencyRequestRepository(session),
        NicheRepository(session),
        FrequencyResultRepository(session),
        FrequencyRequestTableToJormMapper(),
    )


def create_wb_db_filler(session: Session) -> WildberriesDBFillerImpl:
    return WildberriesDBFillerImpl(session,
                                   WildBerriesDataProviderWithoutKeyImplTest(),
                                   WildberriesTestDBFillerInitializer)
