from jarvis_db.services.market.infrastructure.marketplace_service import MarketplaceService
from jarvis_db.services.market.infrastructure.warehouse_service import WarehouseService


class DBFiller:
    def __init__(self, marketplace_service: MarketplaceService, warehouse_service: WarehouseService):
        self.marketplace_name: str = ""
        self.marketplace_id = -1

        self.marketplace_service: MarketplaceService = marketplace_service
        self.warehouse_service: WarehouseService = warehouse_service
