import math

__VOL_HOST_PARTS: dict[str, tuple[int, int]] = {
    "01": (0, 143),
    "02": (144, 287),
    "03": (288, 431),
    "04": (431, 719),
    "05": (720, 1007),
    "06": (1008, 1061),
    "07": (1062, 1115),
    "08": (1116, 1169),
    "09": (1170, 1313),
    "10": (1314, 1601),
    "11": (1602, 1655),
    "12": (1656, 1919),
    "13": (1920, 10000)
}


def calculate_basket_domain_part(global_product_id: int) -> str:
    vol_number = math.floor(global_product_id / 1e5)
    basket_url_part = __get_basket_host_part(vol_number)
    part_number = math.floor(global_product_id / 1e3)
    return f"{basket_url_part}/vol{vol_number}/part{part_number}/{global_product_id}"


def __get_basket_host_part(basket_number: int) -> str:
    result_basket_idx = "13"
    for basket_idx in __VOL_HOST_PARTS:
        lower_basket_frontier, upper_basket_frontier = __VOL_HOST_PARTS[
            basket_idx]
        if lower_basket_frontier <= basket_number <= upper_basket_frontier:
            result_basket_idx = basket_idx
            break
    return f"basket-{result_basket_idx}.wb.ru"
