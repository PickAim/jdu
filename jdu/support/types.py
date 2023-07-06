import dataclasses


@dataclasses.dataclass
class ProductInfo:
    global_id: int
    name: str
    price: int
