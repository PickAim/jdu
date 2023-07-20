from jarvis_db.services.market.infrastructure.category_service import CategoryService
from jarvis_db.services.market.infrastructure.marketplace_service import MarketplaceService
from jarvis_db.services.market.infrastructure.niche_service import NicheService
from jarvis_db.services.market.infrastructure.warehouse_service import WarehouseService
from jarvis_db.services.market.items.product_card_service import ProductCardService
from jarvis_db.services.market.items.product_history_service import ProductHistoryService


class DBFiller:
    def __init__(self):
        self.marketplace_name: str = ""
        self.marketplace_id = -1
        
        self.marketplace_service: MarketplaceService | None = None
        self.category_service: CategoryService | None = None
        self.niche_service: NicheService | None = None

        self.product_service: ProductCardService | None = None
        self.warehouse_service: WarehouseService | None = None
        self.product_history_service: ProductHistoryService | None = None
