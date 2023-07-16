import json
from collections import Counter

from jdu.support.file_constants import commission_json


def find_similar() -> int:
    with open(commission_json, "r") as json_file:
        commission_data: dict[str, dict[str, any]] = json.load(json_file)
        niche_list: list[str] = []
        for niche_commision_data_name in commission_data:
            niche_list.append(niche_commision_data_name)
        niche_dict_similar = Counter(niche_list)
        for niche_name in niche_dict_similar:
            if niche_dict_similar[niche_name] > 1:
                return 1
        return 0
