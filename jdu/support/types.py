import dataclasses


@dataclasses.dataclass
class ProductInfo:
    global_id: int
    name: str
    price: int
    brand: str
    rating: float

    def __hash__(self):
        return hash(self.global_id)
